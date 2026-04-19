const fs = await import("node:fs/promises");
const path = await import("node:path");
const { Presentation, PresentationFile } = await import("@oai/artifact-tool");

const W = 1280;
const H = 720;

const DECK_ID = "fcc-ml-architecture";
const OUT_DIR = "/Users/powerofjinbo/Documents/New project/fcc-ee-qqlvqq/deliverables/fcc_ml_architecture/outputs";
const SCRATCH_DIR = path.resolve(process.env.PPTX_SCRATCH_DIR || path.join("tmp", "slides", DECK_ID));
const PREVIEW_DIR = path.join(SCRATCH_DIR, "preview");
const VERIFICATION_DIR = path.join(SCRATCH_DIR, "verification");
const INSPECT_PATH = path.join(SCRATCH_DIR, "inspect.ndjson");
const MAX_RENDER_VERIFY_LOOPS = 3;

const INK = "#0F1720";
const GRAPHITE = "#344054";
const MUTED = "#667085";
const PAPER = "#F7F4EE";
const PAPER_CARD = "#FFFDF9";
const ACCENT = "#1F9D74";
const ACCENT_DARK = "#13644A";
const GOLD = "#D6A542";
const CORAL = "#D46A58";
const SKY = "#4F7CAC";
const LIGHT_GREEN = "#DFF4EC";
const LIGHT_GOLD = "#F7EFD5";
const LIGHT_CORAL = "#F7E2DD";
const LINE = "#CAD2D9";
const WHITE = "#FFFFFF";
const TRANSPARENT = "#00000000";

const TITLE_FACE = "PingFang SC";
const BODY_FACE = "PingFang SC";
const MONO_FACE = "Aptos Mono";

const SOURCES = {
  repo: "Repository: powerofjinbo/fcc-ee-qqlvqq",
  workflow: "run_lvqq.py, README.md, ml/README.md",
  selection: "h_hww_lvqq.py, plots_lvqq.py",
  config: "ml_config.py",
  train: "ml/train_xgboost_bdt.py",
  apply: "ml/apply_xgboost_bdt.py",
  fit: "ml/fit_profile_likelihood.py",
  paper: "paper/main.tex",
};

const inspectRecords = [];

function normalizeText(text) {
  if (Array.isArray(text)) {
    return text.map((item) => String(item ?? "")).join("\n");
  }
  return String(text ?? "");
}

function textLineCount(text) {
  const value = normalizeText(text);
  if (!value.trim()) return 0;
  return Math.max(1, value.split(/\n/).length);
}

function requiredTextHeight(text, fontSize, lineHeight = 1.18, minHeight = 8) {
  const lines = textLineCount(text);
  if (lines === 0) return minHeight;
  return Math.max(minHeight, lines * fontSize * lineHeight);
}

function assertTextFits(text, boxHeight, fontSize, role = "text") {
  const required = requiredTextHeight(text, fontSize);
  const tolerance = Math.max(2, fontSize * 0.1);
  if (normalizeText(text).trim() && boxHeight + tolerance < required) {
    throw new Error(
      `${role} text box is too short: height=${boxHeight.toFixed(1)}, required>=${required.toFixed(1)}, text=${JSON.stringify(normalizeText(text).slice(0, 120))}`,
    );
  }
}

function lineConfig(fill = TRANSPARENT, width = 0) {
  return { style: "solid", fill, width };
}

function recordShape(slideNo, shape, role, shapeType, x, y, w, h) {
  if (!slideNo) return;
  inspectRecords.push({
    kind: "shape",
    slide: slideNo,
    id: shape?.id || `slide-${slideNo}-${role}-${inspectRecords.length + 1}`,
    role,
    shapeType,
    bbox: [x, y, w, h],
  });
}

function recordText(slideNo, shape, role, text, x, y, w, h) {
  const value = normalizeText(text);
  inspectRecords.push({
    kind: "textbox",
    slide: slideNo,
    id: shape?.id || `slide-${slideNo}-${role}-${inspectRecords.length + 1}`,
    role,
    text: value,
    textPreview: value.replace(/\n/g, " | ").slice(0, 180),
    textChars: value.length,
    textLines: textLineCount(value),
    bbox: [x, y, w, h],
  });
}

function addShape(slide, geometry, x, y, w, h, fill = TRANSPARENT, line = TRANSPARENT, lineWidth = 0, meta = {}) {
  const shape = slide.shapes.add({
    geometry,
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: lineConfig(line, lineWidth),
  });
  recordShape(meta.slideNo, shape, meta.role || geometry, geometry, x, y, w, h);
  return shape;
}

function addText(
  slide,
  slideNo,
  text,
  x,
  y,
  w,
  h,
  {
    size = 20,
    color = INK,
    bold = false,
    face = BODY_FACE,
    align = "left",
    valign = "top",
    fill = TRANSPARENT,
    line = TRANSPARENT,
    lineWidth = 0,
    role = "text",
    checkFit = true,
  } = {},
) {
  if (checkFit) {
    assertTextFits(text, h, size, role);
  }
  const box = addShape(slide, "rect", x, y, w, h, fill, line, lineWidth, { slideNo, role });
  box.text = normalizeText(text);
  box.text.fontSize = size;
  box.text.color = color;
  box.text.bold = Boolean(bold);
  box.text.alignment = align;
  box.text.verticalAlignment = valign;
  box.text.typeface = face;
  box.text.insets = { left: 0, right: 0, top: 0, bottom: 0 };
  recordText(slideNo, box, role, text, x, y, w, h);
  return box;
}

function addBackground(slide, slideNo) {
  slide.background.fill = PAPER;
  addShape(slide, "ellipse", -80, -110, 360, 240, LIGHT_GREEN, TRANSPARENT, 0, { slideNo, role: "bg accent" });
  addShape(slide, "ellipse", 1010, -70, 280, 200, LIGHT_GOLD, TRANSPARENT, 0, { slideNo, role: "bg accent" });
  addShape(slide, "ellipse", 1080, 560, 250, 210, LIGHT_CORAL, TRANSPARENT, 0, { slideNo, role: "bg accent" });
  addShape(slide, "rect", 52, 52, 1176, 616, "#FFFFFFC8", LINE, 1.2, { slideNo, role: "canvas frame" });
  addShape(slide, "rect", 52, 52, 1176, 12, ACCENT, TRANSPARENT, 0, { slideNo, role: "top band" });
}

function addHeader(slide, slideNo, kicker, idx, total) {
  addText(slide, slideNo, kicker, 76, 78, 420, 26, {
    size: 12,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    role: "header kicker",
    checkFit: false,
  });
  addText(slide, slideNo, `${String(idx).padStart(2, "0")} / ${String(total).padStart(2, "0")}`, 1090, 78, 100, 24, {
    size: 12,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    align: "right",
    role: "header index",
    checkFit: false,
  });
  addShape(slide, "rect", 76, 110, 1114, 1.5, LINE, TRANSPARENT, 0, { slideNo, role: "header rule" });
}

function addFooter(slide, slideNo, footerText) {
  addShape(slide, "rect", 76, 646, 1114, 1, LINE, TRANSPARENT, 0, { slideNo, role: "footer rule" });
  addText(slide, slideNo, footerText, 76, 654, 1060, 18, {
    size: 10,
    color: MUTED,
    face: BODY_FACE,
    role: "footer",
    checkFit: false,
  });
}

function addTitleBlock(slide, slideNo, title, subtitle) {
  addText(slide, slideNo, title, 76, 130, 780, 92, {
    size: 34,
    color: INK,
    bold: true,
    face: TITLE_FACE,
    role: "title",
  });
  addText(slide, slideNo, subtitle, 78, 228, 820, 58, {
    size: 17,
    color: GRAPHITE,
    face: BODY_FACE,
    role: "subtitle",
  });
}

function addPill(slide, slideNo, text, x, y, w, fill, color = INK) {
  addShape(slide, "roundRect", x, y, w, 32, fill, TRANSPARENT, 0, { slideNo, role: `pill ${text}` });
  addText(slide, slideNo, text, x + 14, y + 8, w - 28, 18, {
    size: 12,
    color,
    bold: true,
    face: MONO_FACE,
    role: "pill text",
    checkFit: false,
  });
}

function addPanel(slide, slideNo, x, y, w, h, title, body, accent = ACCENT, fill = PAPER_CARD) {
  addShape(slide, "roundRect", x, y, w, h, fill, LINE, 1.2, { slideNo, role: `panel ${title}` });
  addShape(slide, "rect", x, y, 8, h, accent, TRANSPARENT, 0, { slideNo, role: `panel accent ${title}` });
  addText(slide, slideNo, title, x + 22, y + 16, w - 44, 22, {
    size: 14,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    role: `panel title ${title}`,
    checkFit: false,
  });
  addText(slide, slideNo, body, x + 22, y + 46, w - 44, h - 62, {
    size: 15,
    color: INK,
    face: BODY_FACE,
    role: `panel body ${title}`,
  });
}

function addMetricCard(slide, slideNo, x, y, w, h, metric, label, note = "", accent = ACCENT, fill = PAPER_CARD) {
  addShape(slide, "roundRect", x, y, w, h, fill, LINE, 1.2, { slideNo, role: `metric ${label}` });
  addShape(slide, "rect", x, y, w, 8, accent, TRANSPARENT, 0, { slideNo, role: `metric accent ${label}` });
  addText(slide, slideNo, metric, x + 20, y + 24, w - 40, 50, {
    size: 30,
    color: INK,
    bold: true,
    face: TITLE_FACE,
    role: `metric value ${label}`,
  });
  addText(slide, slideNo, label, x + 20, y + 82, w - 40, 22, {
    size: 15,
    color: GRAPHITE,
    face: BODY_FACE,
    role: `metric label ${label}`,
    checkFit: false,
  });
  if (note && h >= 150) {
    addText(slide, slideNo, note, x + 20, y + 108, w - 40, h - 118, {
      size: 9,
      color: MUTED,
      face: BODY_FACE,
      role: `metric note ${label}`,
    });
  }
}

function addFlowBox(slide, slideNo, x, y, w, h, step, title, body, accent = ACCENT) {
  addShape(slide, "roundRect", x, y, w, h, PAPER_CARD, LINE, 1.2, { slideNo, role: `flow ${title}` });
  addShape(slide, "ellipse", x + 18, y + 18, 36, 36, accent, TRANSPARENT, 0, { slideNo, role: `flow index ${title}` });
  addText(slide, slideNo, step, x + 18, y + 28, 36, 16, {
    size: 12,
    color: WHITE,
    bold: true,
    face: MONO_FACE,
    align: "center",
    role: `flow number ${title}`,
    checkFit: false,
  });
  addText(slide, slideNo, title, x + 68, y + 20, w - 88, 26, {
    size: 16,
    color: INK,
    bold: true,
    face: BODY_FACE,
    role: `flow title ${title}`,
    checkFit: false,
  });
  addText(slide, slideNo, body, x + 22, y + 68, w - 44, h - 90, {
    size: 14,
    color: GRAPHITE,
    face: BODY_FACE,
    role: `flow body ${title}`,
  });
}

function addArrowLink(slide, slideNo, x, y, w = 46, h = 10) {
  addShape(slide, "rightArrow", x, y, w, h, ACCENT, TRANSPARENT, 0, { slideNo, role: "flow arrow" });
}

function addNotes(slide, text, sourceKeys) {
  const sourceLines = (sourceKeys || []).map((key) => `- ${SOURCES[key] || key}`).join("\n");
  slide.speakerNotes.setText(`${text}\n\n[Sources]\n${sourceLines}`);
}

function makeSlide(presentation, slideNo, kicker, title, subtitle, footerText) {
  const slide = presentation.slides.add();
  addBackground(slide, slideNo);
  addHeader(slide, slideNo, kicker, slideNo, 12);
  addTitleBlock(slide, slideNo, title, subtitle);
  addFooter(slide, slideNo, footerText);
  return slide;
}

function renderCover(presentation) {
  const slideNo = 1;
  const slide = presentation.slides.add();
  addBackground(slide, slideNo);
  addShape(slide, "rect", 76, 132, 8, 398, ACCENT, TRANSPARENT, 0, { slideNo, role: "cover accent" });
  addText(slide, slideNo, "FCC lvqq / ML Architecture", 102, 136, 420, 26, {
    size: 12,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    role: "cover kicker",
    checkFit: false,
  });
  addText(slide, slideNo, "FCC 项目\nML 结构与训练链条\n详尽梳理", 102, 176, 520, 188, {
    size: 44,
    color: INK,
    bold: true,
    face: TITLE_FACE,
    role: "cover title",
  });
  addText(
    slide,
    slideNo,
    "基于仓库代码路径逐层还原：样本 -> 事件级 cut -> 特征工程 -> XGBoost BDT -> 5-fold 打分 -> pyhf 20-bin shape fit。",
    106,
    382,
    560,
    62,
    {
      size: 18,
      color: GRAPHITE,
      face: BODY_FACE,
      role: "cover subtitle",
    },
  );
  addShape(slide, "roundRect", 102, 474, 430, 86, PAPER_CARD, LINE, 1.2, { slideNo, role: "cover callout" });
  addText(slide, slideNo, "一句话结论", 126, 492, 110, 20, {
    size: 14,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    role: "cover callout label",
    checkFit: false,
  });
  addText(slide, slideNo, "代码里明确是 BDT，且不是“只做一次 train/test”这么简单，而是开发评估与最终 fit 输入分成两条线。", 126, 520, 380, 34, {
    size: 15,
    color: INK,
    face: BODY_FACE,
    role: "cover callout body",
  });

  addShape(slide, "roundRect", 724, 166, 436, 304, PAPER_CARD, LINE, 1.2, { slideNo, role: "cover summary panel" });
  addText(slide, slideNo, "这套分析真正回答的 4 个问题", 752, 190, 260, 24, {
    size: 16,
    color: INK,
    bold: true,
    face: BODY_FACE,
    role: "cover list title",
    checkFit: false,
  });
  addText(
    slide,
    slideNo,
    "1. cut 在 ML 前面做了哪些事情\n2. 70/30 与 5-fold 分别服务什么目标\n3. BDT score 是怎样进 counting scan 和 shape fit 的\n4. 哪些脚本负责训练、应用、拟合与出图",
    752,
    228,
    350,
    128,
    {
      size: 16,
      color: GRAPHITE,
      face: BODY_FACE,
      role: "cover list body",
    },
  );
  addPill(slide, slideNo, "XGBoost BDT", 752, 374, 122, LIGHT_GREEN);
  addPill(slide, slideNo, "70/30 + 20% val", 886, 374, 168, LIGHT_GOLD);
  addPill(slide, slideNo, "5-fold CV", 752, 420, 106, LIGHT_CORAL);
  addPill(slide, slideNo, "pyhf 20 bins", 872, 420, 120, "#E7ECF4");

  addFooter(slide, slideNo, "Source: run_lvqq.py | h_hww_lvqq.py | ml/*.py | paper/main.tex");
  addNotes(slide, "Cover slide with direct framing of the full analysis chain.", ["repo", "workflow", "paper"]);
}

function renderQuickAnswers(presentation) {
  const slideNo = 2;
  const slide = makeSlide(
    presentation,
    slideNo,
    "DIRECT ANSWERS",
    "先把你最关心的问题\n直接回答掉",
    "这页只讲答案，不展开推导。后面每一页再把代码对应关系拆开。",
    "Source: ml/train_xgboost_bdt.py | ml/fit_profile_likelihood.py | paper/main.tex",
  );
  addMetricCard(slide, slideNo, 76, 320, 350, 150, "XGBoost BDT", "模型类型", "训练脚本就是 ml/train_xgboost_bdt.py；apply 脚本新增 bdt_score。", ACCENT, PAPER_CARD);
  addMetricCard(slide, slideNo, 466, 320, 350, 150, "70 / 30", "开发划分", "train_test_split(stratify=y)；再从 70% 训练块里切 20% 做 early stopping validation。", GOLD, PAPER_CARD);
  addMetricCard(slide, slideNo, 856, 320, 334, 150, "5-fold", "最终无偏打分", "不是代替 train/test，而是额外做全样本 out-of-fold score，供 fit 优先使用。", CORAL, PAPER_CARD);

  addPanel(
    slide,
    slideNo,
    76,
    500,
    532,
    126,
    "Cut 怎么做",
    "先在 FCCAnalyses 里做 7 个顺序 cut：\n1 高 p lepton，2 isolation，3 extra lepton veto，4 MET，5 exactly 4 jets，6 Z window，7 recoil window。\n只有过完这些 cut 的事件才会写进 treemaker ntuple，再进入 ML。",
    ACCENT,
  );
  addPanel(
    slide,
    slideNo,
    636,
    500,
    554,
    126,
    "谁先谁后",
    "默认统计主链是：histmaker -> treemaker -> train -> fit。\n若需要把分数重新写回 ROOT，再额外执行 apply；fit 优先读取 kfold_scores.csv，否则退回 test_scores.csv。",
    GOLD,
  );
  addNotes(slide, "Direct answers slide.", ["workflow", "train", "fit", "paper"]);
}

function renderWorkflow(presentation) {
  const slideNo = 3;
  const slide = makeSlide(
    presentation,
    slideNo,
    "END-TO-END ORDER",
    "端到端工作流：\n谁先谁后",
    "入口统一由 run_lvqq.py 调度。默认统计主链是 event selection -> ML training -> fit；apply 是额外导出支线。",
    "Source: run_lvqq.py | README.md",
  );

  const yTop = 300;
  const boxW = 240;
  const boxH = 138;
  addFlowBox(slide, slideNo, 76, yTop, boxW, boxH, "1", "histmaker", "LVQQ_MODE=histmaker\n输出 cutflow 和 kinematic hist。\n目录：output/.../histmaker/", ACCENT);
  addArrowLink(slide, slideNo, 324, yTop + 58);
  addFlowBox(slide, slideNo, 374, yTop, boxW, boxH, "2", "treemaker", "LVQQ_MODE=treemaker\n只写 spectators + ML_FEATURES。\n目录：output/.../treemaker/", GOLD);
  addArrowLink(slide, slideNo, 622, yTop + 58);
  addFlowBox(slide, slideNo, 672, yTop, boxW, boxH, "3", "train", "读取 treemaker ROOT。\n训练 XGBoost，写 model / metrics / test_scores / kfold_scores。", CORAL);
  addArrowLink(slide, slideNo, 920, yTop + 58);
  addFlowBox(slide, slideNo, 970, yTop, 220, boxH, "4", "fit", "直接读取 kfold_scores.csv / test_scores.csv。\n做 counting scan + 20-bin shape fit。", SKY);

  const yBottom = 462;
  addFlowBox(slide, slideNo, 184, yBottom, 280, 130, "5", "apply", "可选：把训练好的模型重新打到 treemaker ntuple。\n输出带 bdt_score 的 ROOT。", ACCENT);
  addArrowLink(slide, slideNo, 480, yBottom + 54);
  addFlowBox(slide, slideNo, 542, yBottom, 280, 130, "6", "plots", "plots_lvqq.py + regenerate_roc.py + paper support figures。", GOLD);
  addArrowLink(slide, slideNo, 838, yBottom + 54);
  addFlowBox(slide, slideNo, 900, yBottom, 290, 130, "7", "paper", "tectonic 编译论文。\npaper/main.tex 引用前面所有结果图。", CORAL);

  addShape(slide, "roundRect", 76, 606, 1114, 28, PAPER_CARD, LINE, 1.2, { slideNo, role: "workflow takeaway" });
  addText(slide, slideNo, "关键理解：histmaker/treemaker 是前置物理选择；train 之后就能直接 fit；apply 只是把分数回写 ROOT 的额外导出步骤。", 92, 614, 1080, 16, {
    size: 12,
    color: INK,
    face: BODY_FACE,
    role: "workflow takeaway text",
    checkFit: false,
  });
  addNotes(slide, "Ordered workflow from run_lvqq.py.", ["workflow"]);
}

function renderSamples(presentation) {
  const slideNo = 4;
  const slide = makeSlide(
    presentation,
    slideNo,
    "SAMPLES",
    "样本构成与背景配置",
    "默认是 full-stat 配置，但代码支持按背景类别改 fraction；训练和 FCCAnalyses 阶段共用同一套 fraction 配置。",
    "Source: ml_config.py | ml/train_xgboost_bdt.py | paper/main.tex",
  );

  addPanel(
    slide,
    slideNo,
    76,
    318,
    520,
    254,
    "Signal 与 irreducible samples",
    "Signal 共 4 个 hadronic-Z 入口：\n- wzp6_ee_qqH_HWW_ecm240\n- wzp6_ee_bbH_HWW_ecm240\n- wzp6_ee_ccH_HWW_ecm240\n- wzp6_ee_ssH_HWW_ecm240\n\n此外 fit 还把 ZH(other) 保留为独立背景组，而不是简单丢掉。",
    ACCENT,
  );
  addPanel(
    slide,
    slideNo,
    624,
    318,
    566,
    254,
    "Reducible backgrounds 与分组",
    "训练脚本和 fit 脚本最终按 5 个物理背景组看待：\nWW / ZZ / qq / tautau / ZH_other。\n\nml_config.py 默认 fraction：WW=ZZ=qq=tautau=1.0。\n也可通过 LVQQ_BACKGROUND_FRACTION 或各组专门环境变量覆盖。",
    GOLD,
  );
  addMetricCard(slide, slideNo, 76, 590, 250, 42, "4", "Signal 样本入口", "", ACCENT, LIGHT_GREEN);
  addMetricCard(slide, slideNo, 350, 590, 250, 42, "5", "Fit 背景物理组", "", GOLD, LIGHT_GOLD);
  addMetricCard(slide, slideNo, 624, 590, 250, 42, "100%", "默认背景统计", "", CORAL, LIGHT_CORAL);
  addMetricCard(slide, slideNo, 898, 590, 292, 42, "共享配置", "FCCAnalyses 与训练共用 fraction", "", SKY, "#E7ECF4");
  addNotes(slide, "Samples and fraction logic.", ["config", "train", "paper"]);
}

function renderCuts(presentation) {
  const slideNo = 5;
  const slide = makeSlide(
    presentation,
    slideNo,
    "EVENT SELECTION",
    "Cut 在哪里做，\n按什么顺序做",
    "所有前置 cut 都在 h_hww_lvqq.py 的 build_graph_lvqq() 里顺序执行；treemaker 只写 cut 之后留下的事件。",
    "Source: h_hww_lvqq.py | plots_lvqq.py | paper/main.tex",
  );

  const cutsLeft =
    "cut1  恰好 1 个 p>20 GeV 的 lepton\ncut2  isolation < 0.15\ncut3  veto 额外 p>5 GeV lepton\ncut4  missingEnergy_e > 20 GeV";
  const cutsRight =
    "cut5  去掉 lepton 后聚成 exactly 4 jets\ncut6  |mZcand - 91.19| < 15 GeV\ncut7  |mrecoil - 125| < 20 GeV\n输出  只把 survivors 写进 treemaker";

  addPanel(slide, slideNo, 76, 318, 520, 238, "前四个 cut：拓扑与 lepton/MET", cutsLeft, ACCENT);
  addPanel(slide, slideNo, 624, 318, 566, 238, "后三个 cut：jet pairing 与质量窗", cutsRight, GOLD);
  addShape(slide, "roundRect", 76, 572, 1114, 60, PAPER_CARD, LINE, 1.2, { slideNo, role: "cuts takeaway" });
  addText(slide, slideNo, "关键点", 98, 588, 60, 16, {
    size: 12,
    color: CORAL,
    bold: true,
    face: MONO_FACE,
    role: "cuts takeaway label",
    checkFit: false,
  });
  addText(slide, slideNo, "ML 不是从原始事件直接学出来的。它吃的是已经经过 7 个物理选择、并且完成 jet pairing 与高层变量构造之后的 flat ntuple。", 176, 584, 980, 24, {
    size: 14,
    color: INK,
    face: BODY_FACE,
    role: "cuts takeaway text",
    checkFit: false,
  });
  addNotes(slide, "Cut order slide.", ["selection", "paper"]);
}

function renderFeatures(presentation) {
  const slideNo = 6;
  const slide = makeSlide(
    presentation,
    slideNo,
    "FEATURE ENGINEERING",
    "变量工程与\nZ-priority pairing",
    "你项目的“ML 结构”不只是模型，而是 cut 后如何把四个 jet 与 lepton/MET 变成对分类有用的高层变量。",
    "Source: h_hww_lvqq.py | ml_config.py | paper/main.tex",
  );

  addPanel(
    slide,
    slideNo,
    76,
    318,
    348,
    278,
    "Z-priority pairing",
    "先把 4 jets 两两配对。\n从 3 种 disjoint pairing 中，选择 invariant mass 最接近 mZ 的一对当 Zcand。\n剩下两 jet 组成 hadronic W*。\n这样不会错误地把 off-shell W* 强迫贴近 mW。",
    ACCENT,
  );
  addPanel(
    slide,
    slideNo,
    452,
    318,
    348,
    278,
    "20 个训练特征",
    "lepton / MET / visible energy / 4 jet momenta / Zcand_dm / Wstar_m / recoil_dmH / Wlep_m / Hcand_m / thrust / angleLepMiss / d23 / d34 等。\n\nML_SPECTATORS 只有：weight, njets。",
    GOLD,
  );
  addPanel(
    slide,
    slideNo,
    828,
    318,
    362,
    278,
    "最强区分信息",
    "paper/main.tex 给出的主导变量是 d34（42.5% importance）。\n它来自 Durham jet merging distance，正好抓住 signal 四喷注结构与 WW 两喷注倾向的差别。",
    CORAL,
  );
  addNotes(slide, "Feature engineering slide.", ["selection", "config", "paper"]);
}

function renderSplit(presentation) {
  const slideNo = 7;
  const slide = makeSlide(
    presentation,
    slideNo,
    "DATA SPLIT",
    "开发划分：\n70/30 之外还有一层 20% validation",
    "这是最容易误读的地方：train/test 与 early stopping validation 是两层不同目的的切分。",
    "Source: ml/train_xgboost_bdt.py",
  );

  addMetricCard(slide, slideNo, 76, 316, 240, 152, "100%", "全体选中事件", "sig_df + bkg_df -> full_df\n-> X, y, phys_weight", ACCENT, PAPER_CARD);
  addArrowLink(slide, slideNo, 332, 382, 46, 10);
  addMetricCard(slide, slideNo, 392, 316, 240, 152, "70%", "开发训练块", "idx_train；后面真正训练和\nvalidation 都从这里再切。", GOLD, PAPER_CARD);
  addArrowLink(slide, slideNo, 648, 382, 46, 10);
  addMetricCard(slide, slideNo, 708, 316, 240, 152, "30%", "保持 untouched 的 test", "只用于开发性能报告、AUC、KS\n与 test_scores.csv。", CORAL, PAPER_CARD);

  addMetricCard(slide, slideNo, 316, 482, 240, 152, "56%", "fit 子块", "X_fit / y_fit / w_fit；\n真正用于训练树参数。", ACCENT, PAPER_CARD);
  addArrowLink(slide, slideNo, 572, 548, 40, 10);
  addMetricCard(slide, slideNo, 628, 482, 240, 152, "14%", "validation 子块", "从 70% 里切 20%；\n只用于 early stopping。", GOLD, PAPER_CARD);

  addShape(slide, "roundRect", 76, 618, 1114, 18, PAPER_CARD, LINE, 1.2, { slideNo, role: "split takeaway" });
  addText(slide, slideNo, "所以代码里同时存在 70/30 和 20% validation；前者服务开发评估，后者服务 early stopping，不冲突。", 92, 622, 1080, 12, {
    size: 11,
    color: INK,
    face: BODY_FACE,
    role: "split takeaway text",
    checkFit: false,
  });
  addNotes(slide, "Data split logic.", ["train"]);
}

function renderTraining(presentation) {
  const slideNo = 8;
  const slide = makeSlide(
    presentation,
    slideNo,
    "TRAINING RECIPE",
    "怎么训练：权重、grid search、early stopping",
    "训练脚本并不是直接把 ROOT 扔给 XGBoost，而是先做 physics weight、再做 class-balanced normalization，然后才 search/train。",
    "Source: ml/train_xgboost_bdt.py | paper/main.tex",
  );

  addPanel(
    slide,
    slideNo,
    76,
    318,
    344,
    278,
    "1. 物理权重",
    "每个 sample 的基础权重：\nphys_weight = L * xsec / (ngen * processed_fraction)。\n\n这保证即使只处理了部分大背景统计，也能还原到正确归一化。",
    ACCENT,
  );
  addPanel(
    slide,
    slideNo,
    448,
    318,
    344,
    278,
    "2. 类别平衡",
    "normalize_class_weights() 不改类内相对关系，只把 signal 与 background 的总权重都缩到较小类的 event 数规模。\n\n作用：训练更平衡，但评估仍然回到 phys_weight。",
    GOLD,
  );
  addPanel(
    slide,
    slideNo,
    820,
    318,
    370,
    278,
    "3. 搜参与 final model",
    "grid search 在最多 50k 训练样本子集上跑。\n参数网格：depth(3,4,5) × lr(0.01,0.05,0.1) × mcw(5,10,20) × subsample(0.7,0.8) × colsample(0.7,0.8) = 108 组。\n每组都带 early_stopping_rounds=30。",
    CORAL,
  );
  addNotes(slide, "Training recipe slide.", ["train", "paper"]);
}

function renderEvaluation(presentation) {
  const slideNo = 9;
  const slide = makeSlide(
    presentation,
    slideNo,
    "EVALUATION",
    "开发性能、过拟合检查与\n训练产物",
    "开发性能来自独立的 70/30 划分；最终给 fit 的并不局限于这 30%。",
    "Source: ml/train_xgboost_bdt.py | paper/main.tex",
  );

  addMetricCard(slide, slideNo, 76, 318, 320, 164, "0.9711", "5-fold weighted AUC", "paper/main.tex: all selected events, out-of-fold score。", ACCENT, PAPER_CARD);
  addMetricCard(slide, slideNo, 428, 318, 320, 164, "0.9719 / 0.9710", "Train / Test AUC", "同一份开发 split 的 performance report。", GOLD, PAPER_CARD);
  addMetricCard(slide, slideNo, 780, 318, 410, 164, "d34 = 42.5%", "最强特征", "paper/main.tex 给出 top importance；feature_importance.csv 也会落盘。", CORAL, PAPER_CARD);

  addPanel(
    slide,
    slideNo,
    76,
    494,
    540,
    132,
    "过拟合检查",
    "代码同时看：\n- |train_auc - test_auc| > 0.02？\n- signal/background 的 KS statistic > 0.05？\n任一满足就把 overtraining_flag 记成 WARNING。",
    ACCENT,
  );
  addPanel(
    slide,
    slideNo,
    644,
    494,
    546,
    132,
    "训练输出文件",
    "xgboost_bdt.json + training_metrics.json\ntraining_history.json + feature_importance.csv\ntest_scores.csv + kfold_scores.csv\nplots/*.png|pdf",
    GOLD,
  );
  addNotes(slide, "Evaluation slide.", ["train", "paper"]);
}

function renderKFold(presentation) {
  const slideNo = 10;
  const slide = makeSlide(
    presentation,
    slideNo,
    "KFOLD SCORING",
    "5-fold 不是多余步骤，\n它是 fit 输入的关键",
    "代码里 train/test split 与 k-fold 是并行存在的两条线：一个给开发报告，一个给最终统计输入。",
    "Source: ml/train_xgboost_bdt.py | ml/fit_profile_likelihood.py | paper/main.tex",
  );

  addPanel(
    slide,
    slideNo,
    76,
    318,
    340,
    278,
    "怎么做",
    "StratifiedKFold(n_splits=5, shuffle=True, random_state=42)。\n每个 fold 用 80% 训练、20% 验证，但每个 event 的 score 都来自“没见过它”的模型。",
    ACCENT,
  );
  addPanel(
    slide,
    slideNo,
    444,
    318,
    340,
    278,
    "为什么要做",
    "如果只拿 test_scores.csv，最终 fit 只能看到 30% 事件。\n而 kfold_scores.csv 给出的是 100% 事件的无偏 score，更适合后面的模板拟合。",
    GOLD,
  );
  addPanel(
    slide,
    slideNo,
    812,
    318,
    378,
    278,
    "fit 里怎么用",
    "fit_profile_likelihood.py 会先找 model_dir/kfold_scores.csv。\n找到就直接用，并注明“不需要 weight scaling”。\n只有退回 test_scores.csv 时，才把 phys_weight 再除以 test_frac=0.30。",
    CORAL,
  );
  addNotes(slide, "K-fold slide.", ["train", "fit", "paper"]);
}

function renderFit(presentation) {
  const slideNo = 11;
  const slide = makeSlide(
    presentation,
    slideNo,
    "FIT LOGIC",
    "BDT cut scan、20-bin shape fit\n与最终精度",
    "这里有两个相关但不同的步骤：一个是 counting reference scan，一个是真正的 20-bin shape fit。",
    "Source: ml/fit_profile_likelihood.py | paper/main.tex",
  );

  addPanel(
    slide,
    slideNo,
    76,
    318,
    340,
    278,
    "1-bin counting scan",
    "scan_bdt_cut() 默认扫：\n0.00-0.89 每 0.05 一步，\n0.90-0.99 每 0.01 一步。\n\n这是 cut-and-count 参考线，不是最终 headline result。",
    ACCENT,
  );
  addPanel(
    slide,
    slideNo,
    444,
    318,
    340,
    278,
    "20-bin shape fit",
    "最终默认 bdt_cut = 0.0，\n在 [0, 1] 上均匀切 20 个 bin。\n信号 strength 参数是 mu；背景按 WW / ZZ / qq / tautau / ZH_other 分组进入模板。",
    GOLD,
  );
  addPanel(
    slide,
    slideNo,
    812,
    318,
    378,
    278,
    "系统误差与结果",
    "每个背景组给 1% normsys。\n默认再加 Barlow-Beeston staterror。\n\npaper/main.tex：\nshape fit 精度 = 0.88%\nphysics-only floor = 0.79%\nbest counting precision = 1.03% @ cut 0.97",
    CORAL,
  );
  addNotes(slide, "Fit logic slide.", ["fit", "paper"]);
}

function renderTakeaways(presentation) {
  const slideNo = 12;
  const slide = makeSlide(
    presentation,
    slideNo,
    "TAKEAWAYS",
    "文件地图与\n最终 takeaways",
    "这一页把“你该去哪个文件看哪个问题”收口，同时把方法链条压成一句话。",
    "Source: repo overview",
  );

  addPanel(
    slide,
    slideNo,
    76,
    318,
    548,
    226,
    "你要看哪类问题，就去哪里",
    "工作流入口：run_lvqq.py\n事件级 cut 与高层变量：h_hww_lvqq.py\n样本列表与 feature 清单：ml_config.py\n训练 / grid search / 70/30 / 5-fold：ml/train_xgboost_bdt.py\n默认统计拟合：ml/fit_profile_likelihood.py\n批量打分导出 ROOT：ml/apply_xgboost_bdt.py",
    ACCENT,
  );
  addPanel(
    slide,
    slideNo,
    652,
    318,
    538,
    226,
    "最终一句话",
    "你的 ML 结构是：\n先做物理 cut 和变量构造，再训练 XGBoost BDT。\n开发评估用 70/30 split；树数选择靠训练内 20% validation。\n最终给 fit 的主输入则是 5-fold out-of-fold score。\n统计解释不是简单 cut-and-count，而是 pyhf 的 20-bin BDT shape fit。",
    GOLD,
  );
  addMetricCard(slide, slideNo, 76, 566, 250, 58, "7", "事件级顺序 cut", "", ACCENT, LIGHT_GREEN);
  addMetricCard(slide, slideNo, 350, 566, 250, 58, "20", "训练特征", "", GOLD, LIGHT_GOLD);
  addMetricCard(slide, slideNo, 624, 566, 250, 58, "5", "fold 无偏打分", "", CORAL, LIGHT_CORAL);
  addMetricCard(slide, slideNo, 898, 566, 292, 58, "0.88%", "shape-fit 精度", "", SKY, "#E7ECF4");
  addNotes(slide, "Final takeaway slide.", ["workflow", "selection", "config", "train", "apply", "fit", "paper"]);
}

async function ensureDirs() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  await fs.mkdir(SCRATCH_DIR, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  await fs.mkdir(VERIFICATION_DIR, { recursive: true });
}

async function createDeck() {
  await ensureDirs();
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  renderCover(presentation);
  renderQuickAnswers(presentation);
  renderWorkflow(presentation);
  renderSamples(presentation);
  renderCuts(presentation);
  renderFeatures(presentation);
  renderSplit(presentation);
  renderTraining(presentation);
  renderEvaluation(presentation);
  renderKFold(presentation);
  renderFit(presentation);
  renderTakeaways(presentation);
  return presentation;
}

async function saveBlobToFile(blob, filePath) {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  await fs.writeFile(filePath, bytes);
}

async function pathExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function writeInspectArtifact(presentation) {
  inspectRecords.unshift({
    kind: "deck",
    id: DECK_ID,
    slideCount: presentation.slides.count,
    slideSize: { width: W, height: H },
  });
  presentation.slides.items.forEach((slide, index) => {
    inspectRecords.splice(index + 1, 0, {
      kind: "slide",
      slide: index + 1,
      id: slide?.id || `slide-${index + 1}`,
    });
  });
  const lines = inspectRecords.map((record) => JSON.stringify(record)).join("\n") + "\n";
  await fs.writeFile(INSPECT_PATH, lines, "utf8");
}

async function currentRenderLoopCount() {
  const logPath = path.join(VERIFICATION_DIR, "render_verify_loops.ndjson");
  if (!(await pathExists(logPath))) return 0;
  const previous = await fs.readFile(logPath, "utf8");
  return previous.split(/\r?\n/).filter((line) => line.trim()).length;
}

async function appendRenderVerifyLoop(presentation, previewPaths, pptxPath) {
  const logPath = path.join(VERIFICATION_DIR, "render_verify_loops.ndjson");
  const priorCount = await currentRenderLoopCount();
  const record = {
    kind: "render_verify_loop",
    deckId: DECK_ID,
    loop: priorCount + 1,
    maxLoops: MAX_RENDER_VERIFY_LOOPS,
    capReached: priorCount + 1 >= MAX_RENDER_VERIFY_LOOPS,
    timestamp: new Date().toISOString(),
    slideCount: presentation.slides.count,
    previewCount: previewPaths.length,
    previewDir: PREVIEW_DIR,
    inspectPath: INSPECT_PATH,
    pptxPath,
  };
  await fs.appendFile(logPath, JSON.stringify(record) + "\n", "utf8");
  return record;
}

async function verifyAndExport(presentation) {
  const priorCount = await currentRenderLoopCount();
  if (priorCount + 1 > MAX_RENDER_VERIFY_LOOPS) {
    throw new Error(`Render/verify loop cap reached: ${MAX_RENDER_VERIFY_LOOPS}`);
  }
  await writeInspectArtifact(presentation);
  const previewPaths = [];
  for (let idx = 0; idx < presentation.slides.items.length; idx += 1) {
    const slide = presentation.slides.items[idx];
    const preview = await presentation.export({ slide, format: "png", scale: 1 });
    const previewPath = path.join(PREVIEW_DIR, `slide-${String(idx + 1).padStart(2, "0")}.png`);
    await saveBlobToFile(preview, previewPath);
    previewPaths.push(previewPath);
  }
  const pptxBlob = await PresentationFile.exportPptx(presentation);
  const pptxPath = path.join(OUT_DIR, "output.pptx");
  await pptxBlob.save(pptxPath);
  await appendRenderVerifyLoop(presentation, previewPaths, pptxPath);
  return { pptxPath, previewPaths };
}

const presentation = await createDeck();
const result = await verifyAndExport(presentation);
console.log(result.pptxPath);
