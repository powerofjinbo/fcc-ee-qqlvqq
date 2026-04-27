#!/usr/bin/env python3
"""Train an XGBoost BDT for the lvqq analysis from FCCAnalyses treemaker ntuples.

v3 improvements (ML specialist review fixes):
- Physics-correct event weights (lumi * xsec / ngen)
- Normalized class weights for balanced learning
- Extended hyperparameter grid search (incl. min_child_weight, subsample)
- Early stopping in both grid search and final training
- Weighted KS overtraining test (binned chi2)
- missingMass sentinel value handling
- Background sculpting diagnostic (BDT score vs Hcand_m)
- Per-sample score distributions
- Training history saved (evals_result)
- Diagnostic plots (ROC, feature importance, BDT score, overtraining, sculpting)
"""

import argparse
import json
import sys
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd
import uproot
import xgboost as xgb
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split, StratifiedKFold
from scipy.stats import ks_2samp

THIS_DIR = Path(__file__).resolve().parent
ANALYSIS_DIR = THIS_DIR.parent
sys.path.insert(0, str(ANALYSIS_DIR))

from ml_config import (
    BACKGROUND_FRACTIONS,
    BACKGROUND_SAMPLES,
    DEFAULT_MODEL_DIR,
    DEFAULT_TREE_NAME,
    DEFAULT_TREEMAKER_DIR,            # 材料都准备打包好
    ML_FEATURES,
    SAMPLE_PROCESSING_FRACTIONS,
    SIGNAL_SAMPLES,
)

# Cross-sections [pb], total generated events, and processing fraction.
# Weight = lumi * xsec / (ngen * fraction) to correctly account for
# only processing a subset of generated events.
SAMPLE_INFO = {
    # Signal (fraction=1, all events processed)
    "wzp6_ee_qqH_HWW_ecm240": {"xsec": 0.01140, "ngen": 1100000, "fraction": 1.0},            # 加载好所有原料，信号背景
    "wzp6_ee_bbH_HWW_ecm240": {"xsec": 0.006350, "ngen": 1000000, "fraction": 1.0},
    "wzp6_ee_ccH_HWW_ecm240": {"xsec": 0.004988, "ngen": 1200000, "fraction": 1.0},
    "wzp6_ee_ssH_HWW_ecm240": {"xsec": 0.006403, "ngen": 1200000, "fraction": 1.0},
    # Diboson and 2-fermion backgrounds. The processed fraction is shared with
    # the FCCAnalyses stage through ml_config.py to keep the whole chain aligned.
    "p8_ee_WW_ecm240":        {"xsec": 16.4385, "ngen": 373375386, "fraction": SAMPLE_PROCESSING_FRACTIONS["p8_ee_WW_ecm240"]},
    "p8_ee_ZZ_ecm240":        {"xsec": 1.35899, "ngen": 209700000, "fraction": SAMPLE_PROCESSING_FRACTIONS["p8_ee_ZZ_ecm240"]},
    "wz3p6_ee_uu_ecm240":     {"xsec": 11.9447, "ngen": 100790000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_uu_ecm240"]},
    "wz3p6_ee_dd_ecm240":     {"xsec": 10.8037, "ngen": 100910000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_dd_ecm240"]},
    "wz3p6_ee_cc_ecm240":     {"xsec": 11.0595, "ngen": 101290000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_cc_ecm240"]},
    "wz3p6_ee_ss_ecm240":     {"xsec": 10.7725, "ngen": 102348636, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_ss_ecm240"]},
    "wz3p6_ee_bb_ecm240":     {"xsec": 10.4299, "ngen": 99490000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_bb_ecm240"]},
    "wz3p6_ee_tautau_ecm240": {"xsec": 4.6682, "ngen": 235800000, "fraction": SAMPLE_PROCESSING_FRACTIONS["wz3p6_ee_tautau_ecm240"]},
    # ZH with H->other (fraction=1, all events processed)
    "wzp6_ee_qqH_Hbb_ecm240":    {"xsec": 0.03106, "ngen": 500000, "fraction": 1.0},
    "wzp6_ee_qqH_Htautau_ecm240": {"xsec": 0.003345, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_qqH_Hgg_ecm240":    {"xsec": 0.004367, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_qqH_Hcc_ecm240":    {"xsec": 0.001542, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_qqH_HZZ_ecm240":    {"xsec": 0.001397, "ngen": 1200000, "fraction": 1.0},
    "wzp6_ee_bbH_Hbb_ecm240":    {"xsec": 0.01731, "ngen": 100000, "fraction": 1.0},
    "wzp6_ee_bbH_Htautau_ecm240": {"xsec": 0.001864, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_bbH_Hgg_ecm240":    {"xsec": 0.002433, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_bbH_Hcc_ecm240":    {"xsec": 0.0008591, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_bbH_HZZ_ecm240":    {"xsec": 0.0007782, "ngen": 1000000, "fraction": 1.0},
    "wzp6_ee_ccH_Hbb_ecm240":    {"xsec": 0.01359, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_ccH_Htautau_ecm240": {"xsec": 0.001464, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ccH_Hgg_ecm240":    {"xsec": 0.001911, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ccH_Hcc_ecm240":    {"xsec": 0.0006748, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ccH_HZZ_ecm240":    {"xsec": 0.0006113, "ngen": 1200000, "fraction": 1.0},
    "wzp6_ee_ssH_Hbb_ecm240":    {"xsec": 0.01745, "ngen": 200000, "fraction": 1.0},
    "wzp6_ee_ssH_Htautau_ecm240": {"xsec": 0.001879, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ssH_Hgg_ecm240":    {"xsec": 0.002453, "ngen": 400000, "fraction": 1.0},
    "wzp6_ee_ssH_Hcc_ecm240":    {"xsec": 0.0008662, "ngen": 300000, "fraction": 1.0},
    "wzp6_ee_ssH_HZZ_ecm240":    {"xsec": 0.0007847, "ngen": 600000, "fraction": 1.0},
}
INT_LUMI = 10.8e6  # pb^-1


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', default=DEFAULT_TREEMAKER_DIR)
    parser.add_argument('--output-dir', default=DEFAULT_MODEL_DIR)
    parser.add_argument('--tree-name', default=DEFAULT_TREE_NAME)
    parser.add_argument('--signal-samples', nargs='*', default=SIGNAL_SAMPLES)
    parser.add_argument('--background-samples', nargs='*', default=BACKGROUND_SAMPLES)
    parser.add_argument('--features', nargs='*', default=ML_FEATURES)
    parser.add_argument('--test-size', type=float, default=0.30) # 70训练，30测试
    parser.add_argument('--random-state', type=int, default=42) # 只是个随机的数字，随机种子，确保可重复性
    parser.add_argument('--n-jobs', type=int, default=8)
    parser.add_argument('--no-grid-search', action='store_true',            # 是让 AI 自己去排列组合尝试成百上千种参数，寻找最优解，这通常要跑好几个小时甚至通宵
                        help='Skip grid search, use default hyperparameters')
    parser.add_argument('--no-plots', action='store_true',
                        help='Skip diagnostic plots')
    parser.add_argument('--kfold', type=int, default=5,       # 5 fold交叉验证
                        help='Number of folds for k-fold CV scoring (0 to disable)')
    return parser.parse_args()


def get_tree_status(root_file, tree_name):
    has_tree = tree_name in root_file
    num_entries = root_file[tree_name].num_entries if has_tree else 0        # 确认数据表的存在 (行 2-3)

    selected = None
    if 'eventsSelected' in root_file:
        try:
            selected = int(root_file['eventsSelected'].member('fVal'))
        except Exception:
            selected = None

    processed = None
    if 'eventsProcessed' in root_file:
        try:
            processed = int(root_file['eventsProcessed'].member('fVal'))        # 这一段就是用python读取c++的信息，做一个信息转换
        except Exception:
            processed = None

    return {
        'has_tree': has_tree,
        'num_entries': num_entries,
        'selected': selected,
        'processed': processed,
    }


def read_samples(input_dir, tree_name, sample_names, features, label):
    """Read samples and compute physics-correct per-event weights."""
    frames = []
    input_dir = Path(input_dir)
    for sample in sample_names:
        root_path = input_dir / f'{sample}.root'
        if not root_path.exists():
            print(f'[warn] missing sample: {root_path}')            # 按着你给的清单（比如WW, ZZ, ZH信号等），一个个去文件夹里找对应的 .root 文件
            continue
# 0-pass）：这是极其专业的高能物理细节！有时候，你让模拟器生成了 10 万个某种罕见的背景事件。
# 但是在跑 C++ 预处理代码时，因为你的 Cut 太严了（比如要求必须有两个喷注一个轻子），这 10 万个事件全军覆没，一个都没活下来。
# 代码逻辑：遇到这种情况，C++ 引擎根本就不会去创建那棵数据树（Tree）。如果没有这段代码的保护，程序就会因为找不到 Tree 而报错。
# 这里的逻辑是：如果没找到树，且侦察兵看到门上的标签写着“幸存者=0” (selected == 0)，那程序就知道：“哦，不是文件坏了，是这批数据全死光了。” 于是淡定地打印一条 [info] 并跳过。
        with uproot.open(root_path) as root_file:
            status = get_tree_status(root_file, tree_name)
            if not status['has_tree']:
                if status['selected'] == 0:
                    processed = status['processed']
                    processed_msg = f', processed={processed}' if processed is not None else ''
                    print(
                        f'[info] {root_path} is a 0-pass sample '
                        f'(eventsSelected=0{processed_msg}); no tree "{tree_name}" was written, skipping'
                    )
                else:
                    print(f'[warn] {root_path} has no tree "{tree_name}", skipping')
                continue
            tree = root_file[tree_name]
            if tree.num_entries == 0:
                print(f'[info] {root_path} has tree "{tree_name}" but 0 entries, skipping')
                continue
            available = set(tree.keys())
            use_features = [f for f in features if f in available]
            missing = [f for f in features if f not in available]
            if missing:
                print(f'[warn] {root_path} missing branches: {missing}')
            frame = tree.arrays(use_features, library='pd')           
            # uproot 库施展了魔法，把 C++ 底层以列式存储的复杂二进制 ROOT 树，瞬间读取到内存中，并将其转化为一个 Pandas DataFrame

        # Compute physics weight: lumi * xsec / ngen_total
        info = SAMPLE_INFO.get(sample, {})
        if info:
            frac = info.get('fraction', 1.0)
            phys_weight = INT_LUMI * info['xsec'] / (info['ngen'] * frac)    # 给出物理权重，一个数字
        else:
            phys_weight = 1.0
            print(f'[warn] no cross-section info for {sample}, using weight=1')

        frame['phys_weight'] = phys_weight        # 告诉 AI 这个事件在现实里值多少分量
        frame['label'] = label                    # 这可是“泄题”答案！ 1 代表信号，0 代表背景。AI 就是要看着这个答案来学习调整内部网络
        frame['sample_name'] = sample             # 记下它的老家（比如它来自 p8_ee_WW_ecm240）。这个对 AI 没用，但对你事后画图（看看 AI 是把哪种背景认错了）极其关键
        n = len(frame)                            # (存活数)：你的代码历经千辛万苦，最后实际上向 Pandas 里塞了多少行数据
        expected = INT_LUMI * info.get('xsec', 0)    # 有效产出，经过你前面 7 道极其严苛的 Cut 之后，在真实的对撞机里，这种事件还能剩下多少个？
        print(f'  {sample}: {n} events, phys_weight={phys_weight:.6f}, '        # (理论总产出)：如果不做任何 Cut，大自然原本会生成多少个这种事件
              f'effective={n*phys_weight:.0f} (expected total={expected:.0f})')
        frames.append(frame)

    if not frames:
        raise RuntimeError('No input ntuples found for training.')
    return pd.concat(frames, ignore_index=True)
    # 上面是 Pandas 最强大的拼接魔法。它把所有表格首尾相连，上下拼接，砸成了一张包含所有特征、所有权重、所有标签的超级大表。
    至此，数据准备工作彻底收官！

def normalize_class_weights(w, y):
    """Normalize weights so signal and background have equal total weight.

    Preserves intra-class weight structure (relative weights within each class
    are unchanged). This ensures balanced learning while respecting the physics
    weight ratios between samples within each class.                                 
    """
    w = w.copy()
    sig_mask = y == 1
    bkg_mask = y == 0                                                                # 归一化一下，让信号背景1:1，这样才公平！
    sig_total = w[sig_mask].sum()
    bkg_total = w[bkg_mask].sum()
    # Scale both classes to have total weight = number of events in smaller class
    target = min(sig_mask.sum(), bkg_mask.sum())
    w[sig_mask] *= target / sig_total
    w[bkg_mask] *= target / bkg_total
    print(f'  Normalized weights: sig total={w[sig_mask].sum():.0f}, '
          f'bkg total={w[bkg_mask].sum():.0f}')
    return w


def weighted_ks_test(scores_a, weights_a, scores_b, weights_b, n_bins=50):
    """Weighted KS-like test using binned chi2 comparison.

    Returns (chi2/ndf, p_value) using weighted histograms.
    scipy's ks_2samp doesn't support weights, so we use a binned approach.
    """

    # 动作：把 AI 给出的打分（从 0 分到 1 分，0 代表背景，1 代表信号）切成 50 个区间（Bins）
    # 然后，把 scores_a（通常是训练集的打分）和 scores_b（通常是测试集的打分）分别投进这 50 个格子里，投进去的不是简单的“次数 +1”，而是“加上这个事件的物理权重”。
    from scipy.stats import chi2 as chi2_dist
    bins = np.linspace(0, 1, n_bins + 1)

    h_a, _ = np.histogram(scores_a, bins=bins, weights=weights_a)
    h_b, _ = np.histogram(scores_b, bins=bins, weights=weights_b)

    # Normalize to unit area，训练集的数据量通常比测试集大得多（比如 70% 对 30%）。
    # 为了让它们能在同一张图上对比，必须把它们的高度都压缩/拉伸，让它们各自的总面积（概率之和）都变成 1
    sum_a = h_a.sum()
    sum_b = h_b.sum()
    if sum_a > 0:
        h_a = h_a / sum_a
    if sum_b > 0:
        h_b = h_b / sum_b

    # Binned chi2: sum (a - b)^2 / (var_a + var_b)
    # Variance from weighted histograms
    h_a_w2, _ = np.histogram(scores_a, bins=bins, weights=weights_a**2)        # 计算了每个 Bin 真正的统计波动范围（Variance）。
    h_b_w2, _ = np.histogram(scores_b, bins=bins, weights=weights_b**2)
    var_a = h_a_w2 / (sum_a**2) if sum_a > 0 else np.zeros_like(h_a)
    var_b = h_b_w2 / (sum_b**2) if sum_b > 0 else np.zeros_like(h_b)

    denom = var_a + var_b                                #  终极卡方审判，算法开始巡视这 50 个格子，每个格子都会算一下卡方，
                                                         # 看训练集的柱子和测试集的柱子高度差了多少。如果这个高度差，超出了正常的统计波动范围（分母的 Var），卡方值就会剧烈飙升！
    mask = denom > 0
    chi2_val = np.sum((h_a[mask] - h_b[mask])**2 / denom[mask])
    ndf = mask.sum() - 1
    p_value = 1.0 - chi2_dist.cdf(chi2_val, ndf) if ndf > 0 else 1.0
    return chi2_val / max(ndf, 1), p_value                # 最后，把卡方值转换成统计学里著名的 p_value，越大说明泛化能力很强，没有过拟合


def make_validation_split(X, y, w, random_state, test_size=0.2):            # 20% 是从已经切好的“训练集 (Train Set)”里面再次切出来的
    """Create a validation split that is disjoint from the fit sample."""
    indices = np.arange(len(X))
    idx_fit, idx_val = train_test_split(
        indices, test_size=test_size, random_state=random_state, stratify=y,
    )
    return (
        X.iloc[idx_fit], X.iloc[idx_val],
        y.iloc[idx_fit], y.iloc[idx_val],
        w.iloc[idx_fit], w.iloc[idx_val],
    )


def fit_with_early_stopping(X_train, y_train, w_train, params, random_state, n_jobs, eval_metric):
    """Choose the boosting length on a held-out validation split, then retrain."""
    X_fit, X_val, y_fit, y_val, w_fit, w_val = make_validation_split(
        X_train, y_train, w_train, random_state=random_state,
    )

    fit_kwargs = {
        'objective': 'binary:logistic',            # 告诉 AI，我们现在做的是非黑即白的二分类任务（信号 vs 背景），你要输出一个 0 到 1 之间的概率。
        'eval_metric': eval_metric,
        'tree_method': 'hist',
        'random_state': random_state,
        'n_jobs': n_jobs,
        'verbosity': 0,
        **params,
    }
    model_es = xgb.XGBClassifier(early_stopping_rounds=30, **fit_kwargs)        # 注意这里的 model_es（es 代表 early stopping），它并不是我们最终要用的模型，而是一个“探路先锋”！
    # 探路先锋开始疯狂建树。每建完一棵，它就拿 X_val 考一次试。
    # 如果它连续建了 30 棵树，在 X_val 上的得分不但没有提高，反而下降了（说明开始过拟合了），它就会立刻强行熄火！！！
    model_es.fit(
        X_fit, y_fit, sample_weight=w_fit,
        eval_set=[(X_val, y_val)],
        sample_weight_eval_set=[w_val],
        verbose=False,
    )

    # 先锋熄火后，程序翻看它的训练日志：
    # “报告！我在建到第 215 棵树的时候，在模拟考里的成绩达到了巅峰。后面的 30 棵树全是在死记硬背！”
    best_iteration = getattr(model_es, 'best_iteration', None)
    n_estimators_final = (best_iteration + 1
                          if best_iteration is not None
                          else params['n_estimators'])

    final_kwargs = dict(fit_kwargs)

    # 最聪明的“回炉重造”
    # 很多新手做到第四步，拿到那个 model_es 就直接当最终模型用了。但这在物理学家眼里是极其浪费的！
    # 因为那个先锋模型，仅仅是用 80% 的 X_fit 训练出来的，那 20% 的 X_val 它为了避嫌，根本没看过里面的具体特征。
    final_kwargs['n_estimators'] = n_estimators_final
    model = xgb.XGBClassifier(**final_kwargs)
    model.fit(X_train, y_train, sample_weight=w_train, verbose=False)



    # 高手的做法是：

    # 抛弃那个探路先锋 model_es。

    # 造一个全新的、干干净净的模型 (model)。

    # 把刚刚刺探到的最高机密（最多只能建 216 棵树）死死锁进新模型的参数里。

    # 把完整的 X_train（100% 的日常复习资料，把那 20% 的模拟考卷也塞回去让它看答案） 毫无保留地喂给新模型！

    # 因为锁死了树的上限是 216 棵，新模型在这 100% 的数据上绝对不会过拟合，并且榨干了每一滴数据的价值！
    val_score = model.predict_proba(X_val)[:, 1]
    val_auc = roc_auc_score(y_val, val_score, sample_weight=w_val)

    evals_result = model_es.evals_result() if hasattr(model_es, 'evals_result') else {}
    return model, best_iteration, n_estimators_final, val_auc, evals_result

# 现在我们需要寻找树的其他参数，
# 痛点：如果你有 200 万行物理事件数据，还要去测试几十种模型参数，那你的电脑可能要跑到下个月才能停下来。
# 妙招：算法在这里做了一个“抽样（Subsample）”。如果总数据大于 5 万，它就随机抽出 50,000 个事件来当“试验田”。
def grid_search(X_train, y_train, w_train, random_state, n_jobs):
    """Run hyperparameter grid search on a subsample with early stopping."""
    print('\n=== Hyperparameter Grid Search ===')
    # Subsample for speed
    n_sub = min(50000, len(X_train))
    idx = np.random.RandomState(random_state).choice(len(X_train), n_sub, replace=False)
    X_sub = X_train.iloc[idx]
    y_sub = y_train.iloc[idx]
    w_sub = w_train.iloc[idx]

    # Split subsample into train/val
    X_t, X_v, y_t, y_v, w_t, w_v = train_test_split(
        X_sub, y_sub, w_sub, test_size=0.3, random_state=random_state, stratify=y_sub
    )

    # Extended grid: now includes min_child_weight and subsample
    # 这就是程序的“试验配方表”。这几个参数全是 XGBoost 防过拟合的顶级法宝：
    # max_depth (树的深度)：只让它看 3、4、5 层。对于高能物理来说，太深的树（比如 10 层）几乎肯定会把蒙特卡洛模拟的随机波动（噪音）当成物理定律背下来。
    # learning_rate (学习率)：每次树更新时跨的步子有多大。
    # min_child_weight：物理权重数据的克星！ 如果一片树叶子上的总权重小于这个值，程序就不允许继续分裂。这极其有效地防止了模型去死抠那些极端罕见的离群点。
    # subsample / colsample_bytree：这就是机器学习里著名的“Dropout/Bagging”思维。每次建树，随机丢弃 20%~30% 的事件或特征（比如不让它看 recoil_m）。这能逼着模型不能只依赖某一个强力特征，必须全方位学习。
    param_grid = {
        'max_depth': [3, 4, 5],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [1000],  # single large value; early stopping finds optimum
        'min_child_weight': [5, 10, 20],
        'subsample': [0.7, 0.8],
        'colsample_bytree': [0.7, 0.8],
    }

    best_auc = 0
    best_params = {}
    results = []

    # 接下来它就要开启一个巨大的 for 循环。把这 108 个“克隆体 AI”扔进那 5 万条数据的角斗场里。
    # 每个克隆体依然配备了我们上一回合聊过的 early_stopping_rounds=30（探路先锋机制），如果连续 30 次考不好就自动抬走。
    # 程序就是要克隆出 108 个不同的 XGBoost 模型，逐一跑完这 108 个配方，最后对比它们的 AUC 考试分数，选出“最强王者”。
    combos = list(product(
        param_grid['max_depth'],
        param_grid['learning_rate'],
        param_grid['n_estimators'],
        param_grid['min_child_weight'],
        param_grid['subsample'],
        param_grid['colsample_bytree'],
    ))
    print(f'  Testing {len(combos)} combinations...')

    for depth, lr, n_est, mcw, ss, csbt in combos:
        model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='auc',
            tree_method='hist',
            max_depth=depth,
            learning_rate=lr,
            n_estimators=n_est,
            min_child_weight=mcw,
            subsample=ss,                                            # 遍历所有组合方式108
            colsample_bytree=csbt,
            random_state=random_state,
            n_jobs=n_jobs,
            early_stopping_rounds=30,
            verbosity=0,
        )
        model.fit(
            X_t, y_t, sample_weight=w_t,
            eval_set=[(X_v, y_v)],
            sample_weight_eval_set=[w_v],
            verbose=False,
        )
        score = model.predict_proba(X_v)[:, 1]                       # 打分，算出AUC
        auc = roc_auc_score(y_v, score, sample_weight=w_v)
        
        # 如果当前这个克隆体考出的 AUC，比之前的历史最高分（best_auc）还要高，它就会立刻把前任踢下台，把自己的参数记录在 best_params 皇冠里
        results.append({
            'max_depth': depth, 'learning_rate': lr,
            'n_estimators': n_est, 'min_child_weight': mcw,
            'subsample': ss, 'colsample_bytree': csbt,
            'val_auc': auc,
            'best_iteration': model.best_iteration if hasattr(model, 'best_iteration') else n_est,
        })
        if auc > best_auc:
            best_auc = auc
            best_params = {
                'max_depth': depth, 'learning_rate': lr,
                'n_estimators': n_est, 'min_child_weight': mcw,
                'subsample': ss, 'colsample_bytree': csbt,
            }

    print(f'  Best: depth={best_params["max_depth"]}, '
          f'lr={best_params["learning_rate"]}, '
          f'n_est={best_params["n_estimators"]}, '
          f'mcw={best_params["min_child_weight"]}, '
          f'ss={best_params["subsample"]}, '
          f'csbt={best_params["colsample_bytree"]}, '
          f'AUC={best_auc:.4f}')
    return best_params, results
# 当 108 次循环彻底跑完，程序的最后几行会极其自豪地 print 出最终加冕为王的“最优参数组合”，并把这套参数通过 return best_params, results 交还给主程序。
# 主程序拿到这套“最强配方”后，终于要用 100% 的海量物理数据进行最终的大结局训练了

def make_plots(output_dir, y_train, y_test, train_score, test_score,
               w_train, w_test, model, features, full_df_test=None):
    """Generate diagnostic plots including sculpting and per-sample distributions."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('[warn] matplotlib not available, skipping plots')                # 画图而已
        return

    plot_dir = output_dir / 'plots'
    plot_dir.mkdir(exist_ok=True)

    def add_fcc_label(ax, x=0.05, y=0.97):
        ax.text(x, y, r'$\mathbf{FCC\text{-}ee}$ Simulation',
                transform=ax.transAxes, fontsize=10, va='top',
                fontstyle='italic')
        ax.text(x, y - 0.06, r'$\sqrt{s}=240$ GeV, $10.8\,\mathrm{ab}^{-1}$',
                transform=ax.transAxes, fontsize=9, va='top')

    # 1. ROC curve
    fpr, tpr, _ = roc_curve(y_test, test_score, sample_weight=w_test)
    auc_val = roc_auc_score(y_test, test_score, sample_weight=w_test)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(fpr, tpr, label=f'Test AUC = {auc_val:.4f}')
    fpr_tr, tpr_tr, _ = roc_curve(y_train, train_score, sample_weight=w_train)
    auc_tr = roc_auc_score(y_train, train_score, sample_weight=w_train)
    ax.plot(fpr_tr, tpr_tr, '--', label=f'Train AUC = {auc_tr:.4f}')
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3)
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('ROC Curve')
    ax.legend(loc='lower right')
    add_fcc_label(ax)
    fig.savefig(plot_dir / 'roc_curve.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'roc_curve.pdf', bbox_inches='tight')
    plt.close()

    # 2. Signal efficiency vs background rejection
    fig, ax = plt.subplots(figsize=(6, 6))
    bkg_rej = 1 - fpr
    ax.plot(tpr, bkg_rej, label=f'Test AUC = {auc_val:.4f}')
    ax.set_xlabel('Signal Efficiency')
    ax.set_ylabel('Background Rejection')
    ax.set_title('Signal Efficiency vs Background Rejection')
    ax.legend()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    fig.savefig(plot_dir / 'sig_eff_vs_bkg_rej.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'sig_eff_vs_bkg_rej.pdf', bbox_inches='tight')
    plt.close()

    # 3. Weighted BDT score distributions for train/test comparison
    fig, ax = plt.subplots(figsize=(8, 6))
    # Match the final profile-likelihood fit binning for easier comparison.
    bins = np.linspace(0, 1, 21)
    # Train - weighted
    ax.hist(train_score[y_train == 1], bins=bins, weights=w_train[y_train == 1],
            density=True, alpha=0.5,
            label='Signal (train)', color='blue', histtype='stepfilled')
    ax.hist(train_score[y_train == 0], bins=bins, weights=w_train[y_train == 0],
            density=True, alpha=0.5,
            label='Background (train)', color='red', histtype='stepfilled')
    # Test as points - weighted
    h_sig, _ = np.histogram(test_score[y_test == 1], bins=bins,
                             weights=w_test[y_test == 1], density=True)
    h_bkg, _ = np.histogram(test_score[y_test == 0], bins=bins,
                             weights=w_test[y_test == 0], density=True)
    centers = 0.5 * (bins[:-1] + bins[1:])
    ax.scatter(centers, h_sig, marker='o', s=20, color='blue',
               label='Signal (test)', zorder=5)
    ax.scatter(centers, h_bkg, marker='o', s=20, color='red',
               label='Background (test)', zorder=5)
    ax.set_xlabel('BDT Score')
    ax.set_ylabel('Normalised (weighted)')
    ax.set_title('BDT Score Distributions')
    ax.legend(fontsize=9)
    add_fcc_label(ax, x=0.35, y=0.97)
    fig.savefig(plot_dir / 'overtraining_check.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'overtraining_check.pdf', bbox_inches='tight')
    plt.close()

    # 4. Feature importance
    importance = pd.Series(model.feature_importances_, index=features).sort_values()
    fig, ax = plt.subplots(figsize=(8, max(6, len(features) * 0.3)))
    importance.plot(kind='barh', ax=ax)
    ax.set_xlabel('Feature Importance (Gain)')
    ax.set_title('Feature Importance')
    add_fcc_label(ax, x=0.60, y=0.97)
    fig.savefig(plot_dir / 'feature_importance.png', dpi=150, bbox_inches='tight')
    fig.savefig(plot_dir / 'feature_importance.pdf', bbox_inches='tight')
    plt.close()

    # 5. Background sculpting check: BDT score vs Hcand_m
    if full_df_test is not None and 'Hcand_m' in full_df_test.columns:
        bkg_mask = y_test == 0
        if bkg_mask.sum() > 0:
            fig, ax = plt.subplots(figsize=(8, 6))
            sc = ax.scatter(
                full_df_test.loc[bkg_mask, 'Hcand_m'],
                test_score[bkg_mask],
                c=w_test[bkg_mask], cmap='viridis', s=2, alpha=0.5,
            )
            fig.colorbar(sc, ax=ax, label='Event weight')
            ax.set_xlabel('$m_{H,cand}$ [GeV]')
            ax.set_ylabel('BDT Score')
            ax.set_title('Background Sculpting Check: BDT Score vs $m_{H,cand}$')
            ax.axvline(125, color='red', linestyle='--', alpha=0.5, label='$m_H = 125$ GeV')
            ax.legend()
            fig.savefig(plot_dir / 'sculpting_check.png', dpi=150, bbox_inches='tight')
            fig.savefig(plot_dir / 'sculpting_check.pdf', bbox_inches='tight')
            plt.close()

            # Profile plot: mean BDT score in Hcand_m bins
            fig, ax = plt.subplots(figsize=(8, 5))
            m_bins = np.linspace(50, 200, 31)
            m_centers = 0.5 * (m_bins[:-1] + m_bins[1:])
            bkg_hcand = full_df_test.loc[bkg_mask, 'Hcand_m'].values
            bkg_scores = test_score[bkg_mask]
            bkg_w = w_test[bkg_mask]
            mean_scores = []
            for i in range(len(m_bins) - 1):
                in_bin = (bkg_hcand >= m_bins[i]) & (bkg_hcand < m_bins[i+1])
                if in_bin.sum() > 0:
                    mean_scores.append(np.average(bkg_scores[in_bin], weights=bkg_w[in_bin]))
                else:
                    mean_scores.append(np.nan)
            ax.plot(m_centers, mean_scores, 'o-', color='red')
            ax.set_xlabel('$m_{H,cand}$ [GeV]')
            ax.set_ylabel('Mean BDT Score (background)')
            ax.set_title('Background Sculpting Profile')
            ax.axvline(125, color='gray', linestyle='--', alpha=0.5)
            ax.grid(True, alpha=0.3)
            fig.savefig(plot_dir / 'sculpting_profile.png', dpi=150, bbox_inches='tight')
            fig.savefig(plot_dir / 'sculpting_profile.pdf', bbox_inches='tight')
            plt.close()

    # 6. Per-sample score distributions
    if full_df_test is not None and 'sample_name' in full_df_test.columns:
        fig, ax = plt.subplots(figsize=(8, 6))
        bins = np.linspace(0, 1, 51)
        for sample_name in full_df_test['sample_name'].unique():
            mask = full_df_test['sample_name'] == sample_name
            if mask.sum() == 0:
                continue
            short_name = sample_name.replace('wzp6_ee_', '').replace('p8_ee_', '').replace('_ecm240', '')
            ax.hist(test_score[mask], bins=bins, weights=w_test[mask],
                    density=True, alpha=0.6, histtype='step', linewidth=1.5,
                    label=short_name)
        ax.set_xlabel('BDT Score')
        ax.set_ylabel('Normalised (weighted)')
        ax.set_title('Per-Sample BDT Score Distributions (Test Set)')
        ax.legend(fontsize=8, ncol=2)
        fig.savefig(plot_dir / 'per_sample_scores.png', dpi=150, bbox_inches='tight')
        fig.savefig(plot_dir / 'per_sample_scores.pdf', bbox_inches='tight')
        plt.close()

    print(f'  Plots saved to {plot_dir}/')

# 核心痛点：30% 的数据不够，70% 的数据有毒
# 破局之法：$k$-Fold（交叉验证）的终极骗术
# 它的核心逻辑如下：
# 切五等份 (n_folds=5)：把所有的物理事件均匀地分成 5 份（A, B, C, D, E），并且依然使用了 StratifiedKFold 保证每份里信号和背景的比例完美一致。
# 第一轮轮换：用 A、B、C、D 这 80% 的数据训练出一个“克隆体 AI”，然后让它去考 E 这 20% 的试卷，并记录下 E 的得分。
# 第二轮轮换：扔掉上一个 AI。用 A、B、C、E 训练出一个全新的 AI，让它去考 D 这 20% 的试卷，记录下 D 的得分。
# 以此类推... 循环 5 次
def kfold_score_all(X, y, w_phys, w_norm, full_df, best_params, n_folds=5, random_state=42, n_jobs=8):
    """Score ALL events using k-fold cross-validation.

    Each event is scored by a model that was NOT trained on it.
    This gives 100% of events with unbiased BDT scores for the fit,
    instead of only the 30% test set.
    """
    print(f'\n=== {n_folds}-Fold Cross-Validation Scoring ===')
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=random_state)

    scores = np.zeros(len(X))
    for fold_i, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_t, y_t, w_t = X.iloc[train_idx], y.iloc[train_idx], w_norm.iloc[train_idx]
        X_v = X.iloc[val_idx]
        model_k, best_iteration, _, _, _ = fit_with_early_stopping(
            X_t, y_t, w_t, best_params,
            random_state=random_state + fold_i,
            n_jobs=n_jobs,
            eval_metric='auc',
        )
        scores[val_idx] = model_k.predict_proba(X_v)[:, 1]
        auc_k = roc_auc_score(y.iloc[val_idx], scores[val_idx],
                              sample_weight=w_phys.iloc[val_idx])
        best_iter_text = 'NA' if best_iteration is None else str(best_iteration + 1)
        print(f'  Fold {fold_i+1}/{n_folds}: AUC={auc_k:.4f} '
              f'({len(val_idx)} events, {best_iter_text} trees)')

    overall_auc = roc_auc_score(y, scores, sample_weight=w_phys)
    print(f'  Overall k-fold AUC: {overall_auc:.4f}')

    kfold_df = pd.DataFrame({
        'y_true': y.to_numpy(),
        'phys_weight': w_phys.to_numpy(),
        'bdt_score': scores,
        'sample_name': full_df['sample_name'].to_numpy(),
    })
    return kfold_df, overall_auc
# 最后返回的这个 kfold_df，就是你整个物理分析流水线产出的终极核武器。它包含了：
# y_true：绝对真理（它到底是信号还是背景）。
# phys_weight：物理重量（它在大自然里到底算几次对撞）。
# bdt_score：AI 给出的一视同仁的打分。
# sample_name：它的老家（具体的物理背景类型）。

def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print('=== Loading Data ===')
    print(
        'Background fractions: '
        f"WW={BACKGROUND_FRACTIONS['ww']:.6g}, "
        f"ZZ={BACKGROUND_FRACTIONS['zz']:.6g}, "
        f"qq={BACKGROUND_FRACTIONS['qq']:.6g}, "
        f"tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
    )
    print('Signal:')
    sig_df = read_samples(args.input_dir, args.tree_name,
                          args.signal_samples, args.features, 1)
    print('Background:')
    bkg_df = read_samples(args.input_dir, args.tree_name,
                          args.background_samples, args.features, 0)
    full_df = pd.concat([sig_df, bkg_df], ignore_index=True)

    # Use only features that exist in the data
    available_features = [f for f in args.features if f in full_df.columns]
    missing_features = [f for f in args.features if f not in full_df.columns]
    if missing_features:
        print(f'[warn] Missing features (will skip): {missing_features}')
    print(f'\nUsing {len(available_features)} features')

    X = full_df[available_features].copy()
    y = full_df['label']
    w = full_df['phys_weight'].astype(float)

    # Fix sentinel values: missingMass uses -999 for undefined cases
    if 'missingMass' in X.columns:
        n_sentinel = (X['missingMass'] < -900).sum()                                            # 把信号和背景文件读进来拼成一个大表 full_df
        if n_sentinel > 0:
            print(f'[fix] Replacing {n_sentinel} missingMass sentinel values (-999) with 0')
            X.loc[X['missingMass'] < -900, 'missingMass'] = 0.0

    # Report class balance with physics weights
    sig_weighted = w[y == 1].sum()
    bkg_weighted = w[y == 0].sum()
    print(f'\n=== Class Balance (physics-weighted) ===')
    print(f'  Signal:     {(y==1).sum()} events, weighted sum = {sig_weighted:.0f}')
    print(f'  Background: {(y==0).sum()} events, weighted sum = {bkg_weighted:.0f}')
    print(f'  Weighted ratio bkg/sig = {bkg_weighted/sig_weighted:.1f}')

    # Normalize class weights for balanced learning (ML review item 4)
    w_normalized = normalize_class_weights(w, y)

    # Single index-based split to guarantee consistency across all arrays                 # 黄金一刀：在这里干净利落地切出了那 30% 绝对不能碰的“终极考卷”（idx_test）
    indices = np.arange(len(X))
    idx_train, idx_test = train_test_split(
        indices, test_size=args.test_size,
        random_state=args.random_state, stratify=y,
    )
    X_train, X_test = X.iloc[idx_train], X.iloc[idx_test]
    y_train, y_test = y.iloc[idx_train], y.iloc[idx_test]
    w_train, w_test = w_normalized.iloc[idx_train], w_normalized.iloc[idx_test]
    w_phys_train, w_phys_test = w.iloc[idx_train], w.iloc[idx_test]
    full_df_test = full_df.iloc[idx_test]

    # Hyperparameter search
    if not args.no_grid_search:
        best_params, grid_results = grid_search(
            X_train, y_train, w_train, args.random_state, args.n_jobs                    # 启动咱们之前聊过的那 108 个克隆人的角斗场
        )
        # Save grid search results
        pd.DataFrame(grid_results).to_csv(
            output_dir / 'grid_search_results.csv', index=False
        )
    else:
        best_params = {
            'max_depth': 4, 'learning_rate': 0.05, 'n_estimators': 1000,
            'min_child_weight': 5, 'subsample': 0.8, 'colsample_bytree': 0.8,
        }
        grid_results = []

    # Train final model with a held-out validation split for early stopping.
    # The test sample is kept untouched for the performance report.
    print(f'\n=== Training Final Model ===')
    print(f'  Params: {best_params}')
    
    # 拿到最强参数后，调用那个带“随堂模拟考”的函数，用 70% 的训练集，正式训练出最终的王牌 AI 模型
    model, best_iteration, final_n_estimators, val_auc, training_history = fit_with_early_stopping(    
        X_train, y_train, w_train, best_params,
        random_state=args.random_state,
        n_jobs=args.n_jobs,
        eval_metric=['logloss', 'auc'],
    )
    print(f'  Validation AUC (held-out from training): {val_auc:.4f}')
    print(f'  Trees kept after early stopping: {final_n_estimators}')

    train_score = model.predict_proba(X_train)[:, 1]
    test_score = model.predict_proba(X_test)[:, 1]

    # Weighted AUC (use physics weights for evaluation, not normalized)
    train_auc = roc_auc_score(y_train, train_score, sample_weight=w_phys_train)
    test_auc = roc_auc_score(y_test, test_score, sample_weight=w_phys_test)

    # Overtraining check: weighted KS test (binned chi2) on signal and background
    ks_sig_chi2, ks_sig_p = weighted_ks_test(
        train_score[y_train == 1], w_train[y_train == 1],
        test_score[y_test == 1], w_test[y_test == 1],
    )
    ks_bkg_chi2, ks_bkg_p = weighted_ks_test(
        train_score[y_train == 0], w_train[y_train == 0],
        test_score[y_test == 0], w_test[y_test == 0],
    )
    # Also compute unweighted KS for comparison
    ks_sig_uw = ks_2samp(train_score[y_train == 1], test_score[y_test == 1])
    ks_bkg_uw = ks_2samp(train_score[y_train == 0], test_score[y_test == 0])

    print(f'\n=== Results ===')
    print(f'  Train AUC: {train_auc:.4f}')
    print(f'  Test AUC:  {test_auc:.4f}')
    print(f'  |delta AUC|:    {abs(train_auc - test_auc):.4f}')
    print(f'  Weighted chi2/ndf (signal):     {ks_sig_chi2:.2f}, p={ks_sig_p:.4f}')
    
    # 召唤咱们最开始看的那个严苛的“加权 KS 质检员”。
    # 最终判定 AI 是否过拟合的测谎仪，用的是“考分差距（Delta AUC）是否大于 2%”，以及“KS 统计量是否大于 0.05”。如果超标，终端里会直接红字亮起 WARNING!
    
    print(f'  Weighted chi2/ndf (background): {ks_bkg_chi2:.2f}, p={ks_bkg_p:.4f}')
    print(f'  Unweighted KS (signal):     stat={ks_sig_uw.statistic:.4f}, p={ks_sig_uw.pvalue:.4f}')
    print(f'  Unweighted KS (background): stat={ks_bkg_uw.statistic:.4f}, p={ks_bkg_uw.pvalue:.4f}')
    # Use KS statistic (not p-value) for overtraining check — p-value is too
    # sensitive with large samples and flags negligible differences.
    overtraining = (abs(train_auc - test_auc) > 0.02
                    or ks_sig_uw.statistic > 0.05
                    or ks_bkg_uw.statistic > 0.05)
    print(f'  Overtraining: {"WARNING!" if overtraining else "OK"}')

    serializable_history = {}
    for ds_name, ds_metrics in training_history.items():
        serializable_history[ds_name] = {
            k: [float(v) for v in vals] for k, vals in ds_metrics.items()
        }

    metrics = {
        'train_auc': float(train_auc),
        'test_auc': float(test_auc),
        'validation_auc': float(val_auc),
        'delta_auc': float(abs(train_auc - test_auc)),
        'weighted_chi2_signal': float(ks_sig_chi2),
        'weighted_chi2_signal_pvalue': float(ks_sig_p),
        'weighted_chi2_background': float(ks_bkg_chi2),
        'weighted_chi2_background_pvalue': float(ks_bkg_p),
        'ks_signal_stat': float(ks_sig_uw.statistic),
        'ks_signal_pvalue': float(ks_sig_uw.pvalue),
        'ks_background_stat': float(ks_bkg_uw.statistic),
        'ks_background_pvalue': float(ks_bkg_uw.pvalue),
        'overtraining_flag': bool(overtraining),
        'n_train': int(len(X_train)),
        'n_test': int(len(X_test)),
        'n_signal_train': int((y_train == 1).sum()),
        'n_background_train': int((y_train == 0).sum()),
        'weighted_signal_sum': float(sig_weighted),
        'weighted_background_sum': float(bkg_weighted),
        'features': available_features,
        'best_hyperparameters': best_params,
        'early_stopping_best_iteration': int(best_iteration + 1)
            if best_iteration is not None else best_params['n_estimators'],
        'weight_normalization': 'class-balanced',
        'validation_fraction': 0.20,
    }

    model_path = output_dir / 'xgboost_bdt.json'           # 把模型、所有的测试参数、特征重要性，全部保存成 JSON 和 CSV 文件，这是模型本体！！！！！！它包含了成百上千棵树的结构
    model.save_model(model_path)

    with open(output_dir / 'training_metrics.json', 'w') as handle:
        json.dump(metrics, handle, indent=2, sort_keys=True)

    # Save training history separately (can be large)
    if serializable_history:
        with open(output_dir / 'training_history.json', 'w') as handle:
            json.dump(serializable_history, handle, indent=2)

    importance = pd.Series(
        model.feature_importances_, index=available_features            # 这是“功劳簿”。它记录了哪个物理变量（比如 $m_{recoil}$）对分类贡献最大
    ).sort_values(ascending=False)
    importance.to_csv(output_dir / 'feature_importance.csv', header=['importance'])

    pd.DataFrame({
        'y_true': y_test.to_numpy(),
        'phys_weight': w_phys_test.to_numpy(),
        'norm_weight': w_test.to_numpy(),
        'bdt_score': test_score,
        'sample_name': full_df_test['sample_name'].to_numpy(),
    }).to_csv(output_dir / 'test_scores.csv', index=False)

    # Diagnostic plots
    if not args.no_plots:
        make_plots(output_dir, y_train, y_test, train_score, test_score,
                   w_phys_train, w_phys_test, model, available_features,
                   full_df_test=full_df_test)

    # K-fold cross-validation scoring (all events get unbiased scores)            # 如果你在启动程序时开了这个开关，它会额外花好几倍的时间，通过交叉验证给所有原始数据（不只是 30% 测试集）打上完全公正的分数，并存为 kfold_scores.csv
    if args.kfold > 0:
        kfold_df, kfold_auc = kfold_score_all(
            X, y, w, w_normalized, full_df, best_params,
            n_folds=args.kfold, random_state=args.random_state, n_jobs=args.n_jobs,
        )
        kfold_df.to_csv(output_dir / 'kfold_scores.csv', index=False)
        print(f'  k-fold scores saved ({len(kfold_df)} events, AUC={kfold_auc:.4f})')

    print(f'\n  model: {model_path}')
    print(f'  test AUC: {test_auc:.4f}')
    print(f'  features: {len(available_features)}')
    print('Done.')


if __name__ == '__main__':
    main()
