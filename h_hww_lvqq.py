import os

import ROOT

from ml_config import (
    BACKGROUND_SAMPLES,
    BACKGROUND_FRACTIONS,
    ML_FEATURES,
    ML_SPECTATORS,
    SAMPLE_PROCESSING_FRACTIONS,
    SIGNAL_SAMPLES,
)

ROOT.TH1.SetDefaultSumw2(ROOT.kTRUE) # 它保证了当你给事例乘以物理权重（如横截面归一化、亮度缩放）时，让直方图上的误差棒是数学上正确的

# ============================================================
# FCC-ee analysis: e+e- -> Z(qq) H(WW -> l nu qq)
# Final state: 4 jets + 1 lepton (e/mu) + MET
# ============================================================

ecm = 240
mode = os.environ.get("LVQQ_MODE", "histmaker").strip().lower()   # 默认histmaker，还有一种模式是treemaker
if mode not in {"histmaker", "treemaker"}:                        # 要求必须在histmaker和treemaker之间选一个否则报错
    raise RuntimeError(f"Unsupported LVQQ_MODE={mode!r}; use 'histmaker' or 'treemaker'")   

treemaker = mode == "treemaker"      # 如果mode是treemaker，那么treemaker这个变量就会被赋予True，否则为False

# 决定多少核CPU来跑数据，部署算力
def _get_worker_cpus() -> int:
    raw_value = os.environ.get("LVQQ_CPUS", os.environ.get("SLURM_CPUS_PER_TASK", "32"))
    try:
        cpus = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer") from exc
    if cpus < 1:
        raise RuntimeError(f"Invalid CPU setting {raw_value!r}; expected a positive integer")
    return cpus

# 任务清单
processList = {
    # Signal: ZH -> Z(qq) H(WW* -> lvqq)
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in SIGNAL_SAMPLES},
    # Full background model with mixed processing fractions.
    **{sample: {"fraction": SAMPLE_PROCESSING_FRACTIONS[sample]} for sample in BACKGROUND_SAMPLES},
}

inputDir = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/"
procDict = "/ceph/submit/data/group/fcc/ee/generation/DelphesEvents/winter2023/IDEA/samplesDict.json"
includePaths = ["../functions/functions.h", "../functions/functions_gen.h", "utils.h"]  #调用我的utils.h里面的具体函数

if treemaker:
    outputDir = f"output/h_hww_lvqq/treemaker/ecm{ecm}/"
else:
    outputDir = f"output/h_hww_lvqq/histmaker/ecm{ecm}/"

nCPUS = _get_worker_cpus()
ROOT.EnableImplicitMT(nCPUS)
print(f"[lvqq] active backgrounds: {len(BACKGROUND_SAMPLES)}")
print(
    "[lvqq] fractions:"
    f" WW={BACKGROUND_FRACTIONS['ww']:.6g},"
    f" ZZ={BACKGROUND_FRACTIONS['zz']:.6g},"
    f" qq={BACKGROUND_FRACTIONS['qq']:.6g},"
    f" tautau={BACKGROUND_FRACTIONS['tautau']:.6g}"
)

doScale = True
intLumi = 10.8e6 if ecm == 240 else 3e6

# 各个物理量的bin的个数，类似于“精细程度”，“分辨率”
bins_count = (50, 0, 50)
bins_nlep = (10, -0.5, 9.5)
bins_p = (200, 0, 200)
bins_m = (400, 0, 400)
bins_met = (200, 0, 200)
bins_chi2 = (200, 0, 50)
bins_recoil = (400, 0, 200)
bins_cos = (100, 0, 1)
bins_iso = (100, 0, 1)


def build_graph_lvqq(df, dataset):
    hists = []

    df = df.Define("ecm", str(ecm))
    df = df.Define("weight", "1.0")
    weightsum = df.Sum("weight")


    # 设置12个循环cut，但实际上我们只用7个
    for i in range(0, 12):
        df = df.Define(f"cut{i}", str(i))

    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut0"))

    df = df.Alias("Muon0", "Muon#0.index")
    df = df.Alias("Electron0", "Electron#0.index")

    df = df.Define("muons_all", "FCCAnalyses::ReconstructedParticle::get(Muon0, ReconstructedParticles)")
    df = df.Define("electrons_all", "FCCAnalyses::ReconstructedParticle::get(Electron0, ReconstructedParticles)")

    # cut1: exactly one high-momentum lepton
    df = df.Define("muons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(muons_all)")   # 筛选miu子
    df = df.Define("electrons_p20", "FCCAnalyses::ReconstructedParticle::sel_p(20)(electrons_all)") # 筛选电子
    df = df.Define("leptons_p20", "FCCAnalyses::ReconstructedParticle::merge(muons_p20, electrons_p20)")  # 合并轻子名称
    df = df.Define("n_leptons_p20", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p20)")  # 计算总轻子个数
    hists.append(df.Histo1D(("n_leptons_p20", "", *bins_nlep), "n_leptons_p20"))   # 保存一个过滤前的直方图
    df = df.Filter("n_leptons_p20 == 1") # 最后关卡，只有lepton = 1才算通过
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut1"))   # 在 cutFlow 直方图的第 1 个 Bin 填入通过这一关的事例数。

    df = df.Define("lepton_p", "FCCAnalyses::ReconstructedParticle::get_p(leptons_p20)[0]")  # 定义幸存（通过）的lepton，直接取第一个因为一共就一个
    hists.append(df.Histo1D(("lepton_p", "", *bins_p), "lepton_p"))  # 为这唯一的轻子画一个动量谱

    # cut2: isolated prompt lepton
    df = df.Define("lepton_iso_v", "FCCAnalyses::coneIsolation(0.01, 0.30)(leptons_p20, ReconstructedParticles)")  # 计算每个lepton的孤立度
    df = df.Define("lepton_iso", "lepton_iso_v[0]")  # 取出第一个也是唯一一个lepton的孤立度数值，看是否符合规则（真正的信号，这种轻子非常干净，周围没有任何其他粒子，这才是我们要找的目标。）
    hists.append(df.Histo1D(("lepton_iso", "", *bins_iso), "lepton_iso")) # 绘制过滤前的孤立度的直方图
    df = df.Filter("lepton_iso < 0.15")   # 只保留孤立度小于0.15的事例
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut2")) # 更新cutflow，放进第二个bin

    # cut3: veto extra leptons above 5 GeV
    df = df.Define("muons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(muons_all)")
    df = df.Define("electrons_p5", "FCCAnalyses::ReconstructedParticle::sel_p(5)(electrons_all)") # 把动量大于5 GeV的lepton都筛选出来
    df = df.Define("leptons_p5", "FCCAnalyses::ReconstructedParticle::merge(muons_p5, electrons_p5)") # 合并一下，叫做leptons_p5
    df = df.Define("n_leptons_p5", "FCCAnalyses::ReconstructedParticle::get_n(leptons_p5)") # 数一下一共有几个
    hists.append(df.Histo1D(("n_leptons_p5", "", *bins_nlep), "n_leptons_p5")) # 画个图
    df = df.Filter("n_leptons_p5 == 1") # 要求大于5 GeV的只能有一个，多了不行
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut3")) # 画个图

    # cut4: missing-energy selection
    df = df.Define("missingEnergy_rp", "FCCAnalyses::missingEnergy(ecm, ReconstructedParticles)") # 调用底层函数missingEnergy， 输入总能量ecm = 240 和所有可见粒子，这个函数自动算出缺失四动量的对象，当作幽灵粒子存起来
    df = df.Define("missingEnergy_e", "missingEnergy_rp[0].energy") # 选出幽灵粒子列表的第一个，直接读取他的energy属性
    df = df.Define("missingEnergy_p", "FCCAnalyses::ReconstructedParticle::get_p(missingEnergy_rp)[0]") # 计算那个幽灵粒子的动量大小
    df = df.Define("missingMass", "FCCAnalyses::missingMass(ecm, ReconstructedParticles)") # 根据能量守恒和动量守恒， 直接算逃跑东西的总质量
    df = df.Define("cosTheta_miss", "FCCAnalyses::get_cosTheta_miss(missingEnergy_rp)") # 算出缺失动量在探测器里的角度余弦值，绝对值接近1，说明是水瓶飞走；接近0，说明是垂直往外崩
    hists.append(df.Histo1D(("missingEnergy_e", "", *bins_met), "missingEnergy_e")) 
    hists.append(df.Histo1D(("missingEnergy_p", "", *bins_met), "missingEnergy_p"))
    hists.append(df.Histo1D(("missingMass", "", *bins_m), "missingMass"))
    hists.append(df.Histo1D(("cosTheta_miss", "", *bins_cos), "cosTheta_miss")) # 把上面的物理特性信息都存在直方图里面
    df = df.Filter("missingEnergy_e > 20") # energy必须大于20！否则都滚蛋！
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut4")) # 通过筛选后，在统计图上加一笔

    # cut5: remove the selected lepton and cluster the rest into 4 jets
    df = df.Define("rps_no_leptons", "FCCAnalyses::ReconstructedParticle::remove(ReconstructedParticles, leptons_p5)")
    df = df.Alias("rps_sel", "rps_no_leptons") # 把之前都选好的粒子都移走，因为我们接下来别的jet算法可能会误伤，以防万一

    df = df.Define("visibleEnergy", "FCCAnalyses::visibleEnergy(rps_sel)") # 把筛选完剩下的粒子放进函数 算出总能量visibleEnergy，应该全部来自于4个夸克
    df = df.Define("visibleEnergy_norm", "visibleEnergy / ecm") # 用这个能量除以对撞机能量240GeV，算出一个百分比（归一化）
    hists.append(df.Histo1D(("visibleEnergy", "", *bins_p), "visibleEnergy")) # 画成直方图存起来

    df = df.Define("RP_px", "FCCAnalyses::ReconstructedParticle::get_px(rps_sel)")
    df = df.Define("RP_py", "FCCAnalyses::ReconstructedParticle::get_py(rps_sel)")
    df = df.Define("RP_pz", "FCCAnalyses::ReconstructedParticle::get_pz(rps_sel)")
    df = df.Define("RP_e", "FCCAnalyses::ReconstructedParticle::get_e(rps_sel)")       # 这四行代码作用就是提取剩下的粒子的所有信息，并单独列出来，为喷注聚类算法准备食材

    df = df.Define("pseudo_jets", "FCCAnalyses::JetClusteringUtils::set_pseudoJets(RP_px, RP_py, RP_pz, RP_e)") # 把你刚才提取出的坐标和能量，打包成 pseudoJets（伪喷注）格式。
    为什么要这步：高能物理界有一个垄断级别的聚类软件包叫 FastJet。它有自己专属的数据格式。这一行就是把你粗糙的数字列表，转换成 FastJet 能直接处理的标准格式
    
    df = df.Define("clustered_jets", "JetClustering::clustering_ee_kt(2, 4, 0, 10)(pseudo_jets)")   # 调用正负电子专用的聚类算法，利用参数 4 强行把所有强子碎片拼凑成恰好 4 个喷注，然后把它们解析成你可以读取的 jets 列表
    df = df.Define("jets", "FCCAnalyses::JetClusteringUtils::get_pseudoJets(clustered_jets)")        # 从上一步生成的 clustered_jets 中，提取出纯粹的 jets 列表。
    
    df = df.Define("njets", "jets.size()")
    hists.append(df.Histo1D(("njets", "", *bins_count), "njets"))
    df = df.Filter("njets == 4")                                    # 这是你的 Cut 5。数一下喷注的数量，画个图记录一下，然后无情砍掉那些因为碎片太少或太刁钻、导致算法死活拼不出 4 个喷注的劣质事件。
                                                                    # 过完这道门，剩下的事件百分之百都拥有刚好 4 个喷注。
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut5"))

    df = df.Define("jet0_p", "sqrt(jets[0].px()*jets[0].px() + jets[0].py()*jets[0].py() + jets[0].pz()*jets[0].pz())")
    df = df.Define("jet1_p", "sqrt(jets[1].px()*jets[1].px() + jets[1].py()*jets[1].py() + jets[1].pz()*jets[1].pz())")
    df = df.Define("jet2_p", "sqrt(jets[2].px()*jets[2].px() + jets[2].py()*jets[2].py() + jets[2].pz()*jets[2].pz())")    # 用勾股定理计算每个jet的三维动量大小
    df = df.Define("jet3_p", "sqrt(jets[3].px()*jets[3].px() + jets[3].py()*jets[3].py() + jets[3].pz()*jets[3].pz())")    # 剥离了方向信息，纯粹算冲劲多大
    df = df.Define("jet_p_sum", "jet0_p + jet1_p + jet2_p + jet3_p")            # 把上面算出的四个动量数值直接相加（标量和）
    hists.append(df.Histo1D(("jet0_p", "", *bins_p), "jet0_p"))
    hists.append(df.Histo1D(("jet1_p", "", *bins_p), "jet1_p"))
    hists.append(df.Histo1D(("jet2_p", "", *bins_p), "jet2_p"))        # 画一下图
    hists.append(df.Histo1D(("jet3_p", "", *bins_p), "jet3_p"))

    # Pair jets with a Z-priority strategy for H -> WW*
    df = df.Define("jets_e", "FCCAnalyses::JetClusteringUtils::get_e(jets)")
    df = df.Define("jets_px", "FCCAnalyses::JetClusteringUtils::get_px(jets)")    # 上一步你刚拿到 4 个干净的jets，现在你需要把每个喷注的能量E和三个方向的动量（px, py, pz）分别提取出来，存成四个独立的数组
    df = df.Define("jets_py", "FCCAnalyses::JetClusteringUtils::get_py(jets)")
    df = df.Define("jets_pz", "FCCAnalyses::JetClusteringUtils::get_pz(jets)")
    df = df.Define("jets_tlv", "FCCAnalyses::makeLorentzVectors(jets_px, jets_py, jets_pz, jets_e)") 
    # 底层 C++ 的配对引擎需要的是 TLorentzVector（ROOT里的标准四维动量对象）。所以用 makeLorentzVectors 把刚才拆解出来的 E, px, py, pz 重新打包，合成一个标准输入格式 jets_tlv，准备送进我的引擎。
    df = df.Define("paired_ZWstar", "FCCAnalyses::pairing_Zpriority_4jets(jets_tlv, 91.19)") # 直接呼叫你刚刚在 utils.h 里写的那个绝妙的主函数 pairing_Zpriority_4jets。传入打包好的 4 个喷注和 Z 玻色子的标准质量 91.19。引擎经过穷举计算后，返回一个装有两个粒子的列表，命名为 paired_ZWstar
    df = df.Define("deltaZ", "FCCAnalyses::pairing_Zpriority_deltaZ(jets_tlv, 91.19)") # 呼叫那个孪生打分函数，它直接返回“全场最佳组合距离 91.19 差了多少”，存进变量 deltaZ 里。这个值越小，说明这个事件越有可能是真实的信号

    # 从引擎退回来的篮子（paired_ZWstar）里，把第 0 号座位的人请出来，命名为 Zcand（Z 候选者）；把第 1 号座位的人请出来，命名为 Wstar（虚 W 候选者）
    df = df.Define("Zcand", "paired_ZWstar[0]")
    df = df.Define("Wstar", "paired_ZWstar[1]")
    # 读取我们拼出来的 Z 候选者的不变质量。如果你画出它的分布图，它应该会在 91 GeV 附近形成一个漂亮的钟形波峰（共振峰）
    df = df.Define("Zcand_m", "Zcand.M()")
    df = df.Define("Zcand_dm", "abs(Zcand_m - 91.19)") # 计算这个拼出来的质量和理想质量的具体偏差
    # 读取那个“兜底”剩下的虚 W 玻色子的质量。因为它是 off-shell 的，它的质量分布会非常宽泛，通常集中在 10 到 40 GeV 之间，而不是真实的 80 GeV。这就是你采用“Z优先策略”获得的最大物理回报！
    df = df.Define("Wstar_m", "Wstar.M()")
    # 把你千辛万苦算出来的 Z质量、虚W质量 和 配对质量误差分(deltaZ) 全部画成一维直方图，丢进 hists 列表里等待最后输出。这些图将是你分析报告里最核心的物理结果展示。
    hists.append(df.Histo1D(("Zcand_m", "", *bins_m), "Zcand_m"))
    hists.append(df.Histo1D(("Wstar_m", "", *bins_m), "Wstar_m"))
    hists.append(df.Histo1D(("deltaZ", "", *bins_chi2), "deltaZ"))

    # New features from autonomous exploration
    # Jet merging variables (Durham kT distance when going from n+1 to n jets)
    # 从之前那台“破壁机”(clustered_jets) 的历史记录里，提取出喷注从 4 个合并成 3 个时的距离参数 d_34，以及从 3 个合并成 2 个时的距离参数 d_23。（虽然应该说是能量参数）
    # 如果 d_34 很小，且 d_23 也很小，模型：“这绝对是个 qq 或 WW 背景，带着俩软胶子，砍掉！”
    # 如果 d_34 很大，且 d_23 也极大，模型：“四个极其坚挺的硬核，完美的 ZH 信号，保留！
    df = df.Define("d_23", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 2)")
    df = df.Define("d_34", "FCCAnalyses::JetClusteringUtils::get_exclusive_dmerge(clustered_jets, 3)")

    # 这里没有任何悬念了！这就是你的 Python 前台在呼叫你刚刚在 utils.h 里亲手清理和确认过的那三个 C++ 辅助函数。算出了 4 喷注总质量、事件推力（形状）以及轻子-中微子夹角
    # 这些统统都会作为输入特征喂给后续的 BDT 模型
    df = df.Define("totalJetMass", "FCCAnalyses::totalJetMass(jets_tlv)")
    df = df.Define("thrust", "FCCAnalyses::computeThrust(rps_no_leptons)")
    df = df.Define("angleLepMiss", "FCCAnalyses::angleLeptonMiss(leptons_p20, missingEnergy_rp)")
    
    # 人为凭空构造一个四维动量 init_tlv，它的动量是 (0, 0, 0)，能量是 240
    # 正负电子对撞机的最大优势就在于：“我们一开始就知道总能量和总动量！” 电子和正电子迎面撞击，总动量抵消为 0，总能量就是 240 GeV。这是我们做精确测量的绝对基石
    df = df.Define("init_tlv", "TLorentzVector ret; ret.SetPxPyPzE(0,0,0,ecm); return ret;")
    # 用总动量 init_tlv，直接减去前面拼出来的 Z 玻色子动量 Zcand，得到一个神秘的剩余动量 recoil_tlv
    # 这就是动量守恒定律！发生的是 ee to ZH反应。如果你已经抓住了Z，那么剩下的东西不管它跑到哪里去了，不管它衰变成了多复杂的东西（甚至是看不见的暗物质），它必定就是希格斯玻色子 (Higgs) 的动量！
    df = df.Define("recoil_tlv", "init_tlv - Zcand") 
    
    df = df.Define("recoil_m", "recoil_tlv.M()")     # 反冲系统”的不变质量 recoil_m
    df = df.Define("recoil_dmH", "abs(recoil_m - 125.0)") # 计算它和标准希格斯质量 (125 GeV) 的差值 recoil_dmH，最后把 recoil_m 画成直方图！
    hists.append(df.Histo1D(("recoil_m", "", *bins_recoil), "recoil_m")) # 画图！
    
    # 提取你事件里那个动量大于 20 GeV 的孤立轻子（leptons_p20[0]）的 x, y, z 动量和能量，打包成标准的四维动量对象 lepton_tlv
    df = df.Define(
        "lepton_tlv",
        "TLorentzVector v; v.SetPxPyPzE(leptons_p20[0].momentum.x, leptons_p20[0].momentum.y, leptons_p20[0].momentum.z, leptons_p20[0].energy); return v;",
    )

    # 把探测器里记录的“缺失能量”（missingEnergy_rp）同样打包成四维动量 nu_tlv
    df = df.Define(
        "nu_tlv",
        "TLorentzVector v; v.SetPxPyPzE(missingEnergy_rp[0].momentum.x, missingEnergy_rp[0].momentum.y, missingEnergy_rp[0].momentum.z, missingEnergy_rp[0].energy); return v;",
    )

    # 把轻子和中微子的四维动量加在一起，命名为 Wlep，然后计算它的质量并画图
    df = df.Define("Wlep", "lepton_tlv + nu_tlv")
    df = df.Define("Wlep_m", "Wlep.M()")
    hists.append(df.Histo1D(("Wlep_m", "", *bins_m), "Wlep_m"))

    # 全场最震撼的一行加法！把刚刚算出来的真实 W（Wlep），加上你很早之前在 C++ 引擎里用两个剩余喷注强行凑出来的那个虚 W（Wstar），合并成最终的希格斯候选者 Hcand。算出它的总质量，并画图保存！
    df = df.Define("Hcand", "Wlep + Wstar")
    df = df.Define("Hcand_m", "Hcand.M()")
    hists.append(df.Histo1D(("Hcand_m", "", *bins_m), "Hcand_m"))

    # cut6: Z mass window
    # 下达过滤指令：要求刚刚拼出来的Z候选者质量（Zcand_m）与标准值91.19的误差绝对值必须小于15。符合要求的放行，不符合的直接砍掉！同时在 CutFlow 柱状图上记下一笔
    df = df.Filter("abs(Zcand_m - 91.19) < 15")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut6"))
    hists.append(df.Histo1D(("Hcand_m_afterZ", "", *bins_m), "Hcand_m"))
    hists.append(df.Histo1D(("recoil_m_afterZ", "", *bins_recoil), "recoil_m"))

    # cut7: recoil window
    # 最后一道防线！利用计算出的反冲质量（recoil_m），要求它距离标准希格斯质量125的误差不能超过20（也就是保留105 - 145的区间）
    df = df.Filter("abs(recoil_m - 125) < 20")
    hists.append(df.Histo1D(("cutFlow", "", *bins_count), "cut7"))
    hists.append(df.Histo1D(("Hcand_m_final", "", *bins_m), "Hcand_m"))

    # 在经历了九九八十一难、跨过了全部 7 道 Cut 之后，画出最后幸存者们重构出的希格斯质量分布图 Hcand_m_final。物理意义：这就是你这张物理彩票的最终大奖！
    # 此时留下的事件纯度极高。你亲自用碎片拼出来的这个分布图，将在 125 GeV 处呈现出一个完美的共振峰。这就是你向全世界宣布“我找到了H to WW的铁证！

    return hists, weightsum, df         # 满载而归，打包交差


if treemaker:
    class RDFanalysis:
        @staticmethod
        def analysers(df):
            hists, weightsum, df = build_graph_lvqq(df, "")
            return df

        @staticmethod
        def output():
            return ML_SPECTATORS + ML_FEATURES
else:
    def build_graph(df, dataset):
        hists, weightsum, df = build_graph_lvqq(df, dataset)
        return hists, weightsum
