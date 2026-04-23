// Node-oriented editable pro deck builder.
// Run this after editing SLIDES, SOURCES, and layout functions.
// The init script installs a sibling node_modules/@oai/artifact-tool package link
// and package.json with type=module for shell-run eval builders. Run with the
// Node executable from Codex workspace dependencies or the platform-appropriate
// command emitted by the init script.
// Do not use pnpm exec from the repo root or any Node binary whose module
// lookup cannot resolve the builder's sibling node_modules/@oai/artifact-tool.

const fs = await import("node:fs/promises");
const path = await import("node:path");
const { Presentation, PresentationFile } = await import("@oai/artifact-tool");

const W = 1280;
const H = 720;

const DECK_ID = "learning-order-slides";
const OUT_DIR = "/Users/powerofjinbo/Documents/New project/fcc-ee-qqlvqq/docs/learning_order_slides/outputs";
const REF_DIR = "/Users/powerofjinbo/Documents/New project/fcc-ee-qqlvqq/tmp/slides/learning_order_slides/reference-images";
const SCRATCH_DIR = path.resolve(process.env.PPTX_SCRATCH_DIR || path.join("tmp", "slides", DECK_ID));
const PREVIEW_DIR = path.join(SCRATCH_DIR, "preview");
const VERIFICATION_DIR = path.join(SCRATCH_DIR, "verification");
const INSPECT_PATH = path.join(SCRATCH_DIR, "inspect.ndjson");
const MAX_RENDER_VERIFY_LOOPS = 3;

const INK = "#172022";
const GRAPHITE = "#3A4548";
const MUTED = "#6E777B";
const PAPER = "#F4F1E8";
const PAPER_96 = "#F4F1E8F2";
const WHITE = "#FFFFFF";
const ACCENT = "#0D8B7A";
const ACCENT_DARK = "#07564D";
const GOLD = "#C99A3D";
const CORAL = "#C96854";
const TRANSPARENT = "#00000000";

const TITLE_FACE = "PingFang SC";
const BODY_FACE = "PingFang SC";
const MONO_FACE = "Menlo";

const FALLBACK_PLATE_DATA_URL =
  "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=";

const SOURCES = {
  primary: "Repository: powerofjinbo/fcc-ee-qqlvqq. Core scripts: run_lvqq.py, h_hww_lvqq.py, plots_lvqq.py, ml/*.py, paper/*.",
};

const SLIDES = [
  {
    "kicker": "FCC LVQQ STUDY PLAN",
    "title": "FCC lvqq Pipeline\n学习顺序 Slides",
    "subtitle": "目标不是先背脚本，而是先搞清楚 输入 / 输出 / cut / feature / fit 的依赖关系。",
    "expectedVisual": "Cover slide with study-roadmap framing.",
    "moment": "先看数据怎么流，再看每一步为什么这样做",
    "notes": "封面页。强调学习顺序与运行顺序有关，但更关键的是理解依赖关系：driver -> selection -> validation -> ML -> fit -> paper。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "OVERVIEW",
    "title": "先记住\n全局地图",
    "subtitle": "先把仓库当成 4 层，而不是一堆并列脚本。",
    "expectedVisual": "Metric overview slide.",
    "metrics": [
      [
        "1",
        "正常使用只需要记住一个主入口：run_lvqq.py",
        "driver / orchestration"
      ],
      [
        "4",
        "核心层次：selection、plots、ml、paper",
        "understand the layers"
      ],
      [
        "7",
        "建议按 7 天路线逐层往下钻",
        "from driver to fit"
      ]
    ],
    "notes": "这一页只建立总图。提醒自己：不要一上来就扎进 train_xgboost_bdt.py，否则很容易只看到模型，看不到 upstream physics selection。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "REPO MAP",
    "title": "Repo 结构\n怎么读",
    "subtitle": "你现在觉得结构乱，主要是因为 helper、分析、论文层混在根目录视角里。",
    "expectedVisual": "Three-card role split slide.",
    "cards": [
      [
        "Top Level",
        "run_lvqq.py 是总调度；h_hww_lvqq.py 是 FCCAnalyses event graph；ml_config.py 管 sample、feature、路径。"
      ],
      [
        "functions/ + utils.h",
        "这是 C++ helper 层，不是普通 Python function 集合。它们被 includePaths 注入后，直接服务于 df.Define(...) 和 df.Filter(...)。"
      ],
      [
        "paper/",
        "这是结果包装层。它不决定 selection 或 ML 本身，而是把 plots 和 fit 结果整理成 paper figures 与 main.tex。"
      ]
    ],
    "notes": "顺带回答用户结构问题。指出最不整齐的地方其实是 utils.h 还在根目录，而不是函数太多。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "DAY 1",
    "title": "Day 1\nrun_lvqq.py + ml_config.py",
    "subtitle": "先看 orchestration，再看配置；先搞清楚谁调用谁，再看 feature list。",
    "expectedVisual": "Three-card study plan slide.",
    "cards": [
      [
        "读什么",
        "run_sequence、step_histmaker、step_treemaker、step_train、step_fit、main；再看 ml_config 里的 ML_FEATURES、SIGNAL_SAMPLES、BACKGROUND_SAMPLES。"
      ],
      [
        "要回答",
        "每个 target 读什么输入、写到哪个目录？background fraction 改的是处理比例还是物理定义？为什么 ml_config 要作为共享配置层存在？"
      ],
      [
        "自己跑",
        "python3 run_lvqq.py --help；然后口头复述 all / stage1 / ml / paper 分别对应什么。"
      ]
    ],
    "notes": "第一天不要追求细节。你的目标只是能画出一张阶段图：histmaker -> treemaker -> train -> fit / apply -> plots -> paper。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "DAY 2",
    "title": "Day 2\nh_hww_lvqq.py 前半段",
    "subtitle": "先吃透 cut1 到 cut4：1 lepton、isolation、extra-lepton veto、MET。",
    "expectedVisual": "Three-card study plan slide.",
    "cards": [
      [
        "读什么",
        "build_graph_lvqq() 里 lepton object 定义、coneIsolation、n_leptons_p20 / p5、missingEnergy、missingMass、cosTheta_miss。"
      ],
      [
        "要回答",
        "Define 和 Filter 区别是什么？为什么先要唯一高动量轻子，再做 isolation，再 veto 额外轻子？MET > 20 GeV 主要在压什么背景？"
      ],
      [
        "自己跑",
        "python3 run_lvqq.py histmaker --background-fraction 0.02；再去 plots 看 lepton_p、lepton_iso、missingEnergy_e 的分布。"
      ]
    ],
    "notes": "这里开始建立 physics intuition：每个 cut 都应该对应一个明确的背景类型，而不是纯机械筛选。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "DAY 3",
    "title": "Day 3\nh_hww_lvqq.py 后半段",
    "subtitle": "这一页要彻底讲清 cut5 的 4 jets、Z-priority pairing、以及 cut6-7。",
    "expectedVisual": "Three-card study plan slide.",
    "cards": [
      [
        "对象构造",
        "先 remove 掉已选 lepton，再把剩余 ReconstructedParticles 做 exclusive ee_kt clustering，得到 jets，再定义 Zcand、Wstar、Wlep、Hcand、recoil。"
      ],
      [
        "Jan 真正在问什么",
        "4 个 jet 不是从已有 jet list 里挑出来的；真正的 filter 是 njets == 4。对象构造在前，事件筛选在后，这个口头表达一定要分开。"
      ],
      [
        "自己跑",
        "python3 run_lvqq.py treemaker --background-fraction 0.02；然后确认 output/h_hww_lvqq/treemaker/ecm240 里树上有哪些 ML feature。"
      ]
    ],
    "notes": "这是最关键的一天。你必须能用一句话准确回答 cut5：remove lepton -> cluster rest into 4 jets -> require njets == 4。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "DAY 4",
    "title": "Day 4\nplots_lvqq.py",
    "subtitle": "这一步不是补图，而是验证你的 selection 是否真的按预期工作。",
    "expectedVisual": "Three-card study plan slide.",
    "cards": [
      [
        "读什么",
        "getHist、collectCutflowData、makeCutflowTable、makePlot、makeNormalizedPlot、makeComparisonPlot。"
      ],
      [
        "要回答",
        "哪些 process 被 merge 成 plotting group？为什么 histmaker 输出不需要再 scale？哪几张图最适合验证 cut6 和 cut7 的物理意义？"
      ],
      [
        "自己跑",
        "python3 run_lvqq.py plots；重点看 cutflow、deltaZ、recoil_m_afterZ、Hcand_m_final_norm。"
      ]
    ],
    "notes": "你要学会把 plots 当作 debug / validation 入口，而不是 paper decoration。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "DAY 5",
    "title": "Day 5\ntrain_xgboost_bdt.py：数据进入模型",
    "subtitle": "先理解 sample reading、physics weight、class balancing、train/test split，再谈模型本身。",
    "expectedVisual": "Three-card study plan slide.",
    "cards": [
      [
        "读什么",
        "read_samples、normalize_class_weights、main() 里 sentinel 修正、class balance、train_test_split、test_scores.csv / kfold_scores.csv 的写出逻辑。"
      ],
      [
        "要回答",
        "phys_weight 为什么是 lumi * xsec / (ngen * fraction)？为什么训练时用 class-balanced 权重，但评估和 fit 仍然用 phys_weight？"
      ],
      [
        "自己跑",
        "LVQQ_BACKGROUND_FRACTION=0.02 python3 ml/train_xgboost_bdt.py --no-grid-search --kfold 5；然后读 training_metrics.json。"
      ]
    ],
    "notes": "这一天的核心是 dataset accounting，不是 AUC 本身。你必须能清楚说出 70/30 split 和 validation split 的关系。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "DAY 6",
    "title": "Day 6\ntrain_xgboost_bdt.py：过拟合与 5-fold",
    "subtitle": "这一页专门回答两个问题：怎么防止过拟合？5-fold 到底是干什么的？",
    "expectedVisual": "Metric summary slide.",
    "metrics": [
      [
        "3",
        "三层防线：独立 test、训练内 validation、early stopping",
        "split + stopping"
      ],
      [
        "4+",
        "控制复杂度：max_depth、min_child_weight、subsample、colsample_bytree",
        "model capacity"
      ],
      [
        "5",
        "5-fold 的目标是给全部事件产生无偏 score，不是单纯报性能",
        "out-of-fold scoring"
      ]
    ],
    "notes": "强调 overtraining 判断不只看 AUC，还看 train/test score 分布、KS statistic、weighted chi2/ndf。k-fold 结果最终服务于 fit 输入。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "DAY 7",
    "title": "Day 7\nfit + apply + paper",
    "subtitle": "最后再去看统计和论文层，这样你才知道 fit 到底在消费什么输入。",
    "expectedVisual": "Three-card study plan slide.",
    "cards": [
      [
        "fit_profile_likelihood.py",
        "重点读 build_templates、build_pyhf_model、fit_asimov、scan_bdt_cut。你要能说清 counting scan 和 20-bin shape fit 的区别。"
      ],
      [
        "apply_xgboost_bdt.py",
        "把 model score 写回 scored ROOT ntuple。它很有用，但不是默认 headline fit 的核心输入，所以学习顺序放在 fit 后面更顺。"
      ],
      [
        "paper/",
        "generate_supporting_figures.py、sync_paper_figures.py、main.tex 负责把上游结果整理成图和文字。analysis 决定结果，paper 决定怎么呈现。"
      ]
    ],
    "notes": "最后一天把统计层和展示层串起来：selection/ML 为什么会落到这些模板和这些 figures 上。",
    "sources": [
      "primary"
    ]
  },
  {
    "kicker": "CHECKLIST",
    "title": "最后自测\n你必须能答出来",
    "subtitle": "如果下面三张卡你都能口头说顺，这条 pipeline 就真的进脑子了。",
    "expectedVisual": "Final checklist slide.",
    "cards": [
      [
        "结构题",
        "run_lvqq.py、functions/、paper/ 各干什么？histmaker、treemaker、train、fit、apply、plots、paper 的输入输出是什么？"
      ],
      [
        "方法题",
        "cut5 的 4 jets 怎么来？训练集怎么分？怎么防过拟合？5-fold 为什么不是可有可无的装饰？"
      ],
      [
        "命令题",
        "先跑 histmaker / treemaker / plots，再跑 train / fit / apply。每跑完一步，都能去对应输出目录和图里验证自己刚学到的结论。"
      ]
    ],
    "notes": "收尾页。建议用户真正开始学时，每一页过完就回脚本做一次口头复述和一次命令执行。",
    "sources": [
      "primary"
    ]
  }
];

const inspectRecords = [];

async function pathExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function readImageBlob(imagePath) {
  const bytes = await fs.readFile(imagePath);
  if (!bytes.byteLength) {
    throw new Error(`Image file is empty: ${imagePath}`);
  }
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function normalizeImageConfig(config) {
  if (!config.path) {
    return config;
  }
  const { path: imagePath, ...rest } = config;
  return {
    ...rest,
    blob: await readImageBlob(imagePath),
  };
}

async function ensureDirs() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const obsoleteFinalArtifacts = [
    "preview",
    "verification",
    "inspect.ndjson",
    ["presentation", "proto.json"].join("_"),
    ["quality", "report.json"].join("_"),
  ];
  for (const obsolete of obsoleteFinalArtifacts) {
    await fs.rm(path.join(OUT_DIR, obsolete), { recursive: true, force: true });
  }
  await fs.mkdir(SCRATCH_DIR, { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  await fs.mkdir(VERIFICATION_DIR, { recursive: true });
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

function normalizeText(text) {
  if (Array.isArray(text)) {
    return text.map((item) => String(item ?? "")).join("\n");
  }
  return String(text ?? "");
}

function textLineCount(text) {
  const value = normalizeText(text);
  if (!value.trim()) {
    return 0;
  }
  return Math.max(1, value.split(/\n/).length);
}

function requiredTextHeight(text, fontSize, lineHeight = 1.18, minHeight = 8) {
  const lines = textLineCount(text);
  if (lines === 0) {
    return minHeight;
  }
  return Math.max(minHeight, lines * fontSize * lineHeight);
}

function assertTextFits(text, boxHeight, fontSize, role = "text") {
  const required = requiredTextHeight(text, fontSize);
  const tolerance = Math.max(2, fontSize * 0.08);
  if (normalizeText(text).trim() && boxHeight + tolerance < required) {
    throw new Error(
      `${role} text box is too short: height=${boxHeight.toFixed(1)}, required>=${required.toFixed(1)}, ` +
        `lines=${textLineCount(text)}, fontSize=${fontSize}, text=${JSON.stringify(normalizeText(text).slice(0, 90))}`,
    );
  }
}

function wrapText(text, widthChars) {
  const value = normalizeText(text);
  if (!/\s/.test(value)) {
    const lines = [];
    for (let i = 0; i < value.length; i += widthChars) {
      lines.push(value.slice(i, i + widthChars));
    }
    return lines.join("\n");
  }
  const words = value.split(/\s+/).filter(Boolean);
  const lines = [];
  let current = "";
  for (const word of words) {
    const next = current ? `${current} ${word}` : word;
    if (next.length > widthChars && current) {
      lines.push(current);
      current = word;
    } else {
      current = next;
    }
  }
  if (current) {
    lines.push(current);
  }
  return lines.join("\n");
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

function recordImage(slideNo, image, role, imagePath, x, y, w, h) {
  inspectRecords.push({
    kind: "image",
    slide: slideNo,
    id: image?.id || `slide-${slideNo}-${role}-${inspectRecords.length + 1}`,
    role,
    path: imagePath,
    bbox: [x, y, w, h],
  });
}

function applyTextStyle(box, text, size, color, bold, face, align, valign, autoFit, listStyle) {
  box.text = text;
  box.text.fontSize = size;
  box.text.color = color;
  box.text.bold = Boolean(bold);
  box.text.alignment = align;
  box.text.verticalAlignment = valign;
  box.text.typeface = face;
  box.text.insets = { left: 0, right: 0, top: 0, bottom: 0 };
  if (autoFit) {
    box.text.autoFit = autoFit;
  }
  if (listStyle) {
    box.text.style = "list";
  }
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
    size = 22,
    color = INK,
    bold = false,
    face = BODY_FACE,
    align = "left",
    valign = "top",
    fill = TRANSPARENT,
    line = TRANSPARENT,
    lineWidth = 0,
    autoFit = null,
    listStyle = false,
    checkFit = true,
    role = "text",
  } = {},
) {
  if (!checkFit && textLineCount(text) > 1) {
    throw new Error("checkFit=false is only allowed for single-line headers, footers, and captions.");
  }
  if (checkFit) {
    assertTextFits(text, h, size, role);
  }
  const box = addShape(slide, "rect", x, y, w, h, fill, line, lineWidth);
  applyTextStyle(box, text, size, color, bold, face, align, valign, autoFit, listStyle);
  recordText(slideNo, box, role, text, x, y, w, h);
  return box;
}

async function addImage(slide, slideNo, config, position, role, sourcePath = null) {
  const image = slide.images.add(await normalizeImageConfig(config));
  image.position = position;
  recordImage(slideNo, image, role, sourcePath || config.path || config.uri || "inline-data-url", position.left, position.top, position.width, position.height);
  return image;
}

async function addPlate(slide, slideNo, opacityPanel = false) {
  slide.background.fill = PAPER;
  const platePath = path.join(REF_DIR, `slide-${String(slideNo).padStart(2, "0")}.png`);
  if (await pathExists(platePath)) {
    await addImage(
      slide,
      slideNo,
      { path: platePath, fit: "cover", alt: `Text-free art-direction plate for slide ${slideNo}` },
      { left: 0, top: 0, width: W, height: H },
      "art plate",
      platePath,
    );
  } else {
    await addImage(
      slide,
      slideNo,
      { dataUrl: FALLBACK_PLATE_DATA_URL, fit: "cover", alt: `Fallback blank art plate for slide ${slideNo}` },
      { left: 0, top: 0, width: W, height: H },
      "fallback art plate",
      "fallback-data-url",
    );
  }
  if (opacityPanel) {
    addShape(slide, "rect", 0, 0, W, H, "#FFFFFFB8", TRANSPARENT, 0, { slideNo, role: "plate readability overlay" });
  }
}

function addHeader(slide, slideNo, kicker, idx, total) {
  addText(slide, slideNo, String(kicker || "").toUpperCase(), 64, 34, 430, 24, {
    size: 13,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    checkFit: false,
    role: "header",
  });
  addText(slide, slideNo, `${String(idx).padStart(2, "0")} / ${String(total).padStart(2, "0")}`, 1114, 34, 104, 24, {
    size: 13,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    align: "right",
    checkFit: false,
    role: "header",
  });
  addShape(slide, "rect", 64, 64, 1152, 2, INK, TRANSPARENT, 0, { slideNo, role: "header rule" });
  addShape(slide, "ellipse", 57, 57, 16, 16, ACCENT, INK, 2, { slideNo, role: "header marker" });
}

function addTitleBlock(slide, slideNo, title, subtitle = null, x = 64, y = 86, w = 780, dark = false) {
  const titleColor = dark ? PAPER : INK;
  const bodyColor = dark ? PAPER : GRAPHITE;
  addText(slide, slideNo, title, x, y, w, 142, {
    size: 40,
    color: titleColor,
    bold: true,
    face: TITLE_FACE,
    role: "title",
  });
  if (subtitle) {
    addText(slide, slideNo, subtitle, x + 2, y + 148, Math.min(w, 720), 70, {
      size: 19,
      color: bodyColor,
      face: BODY_FACE,
      role: "subtitle",
    });
  }
}

function addIconBadge(slide, slideNo, x, y, accent = ACCENT, kind = "signal") {
  addShape(slide, "ellipse", x, y, 54, 54, PAPER_96, INK, 1.2, { slideNo, role: "icon badge" });
  if (kind === "flow") {
    addShape(slide, "ellipse", x + 13, y + 18, 10, 10, accent, INK, 1, { slideNo, role: "icon glyph" });
    addShape(slide, "ellipse", x + 31, y + 27, 10, 10, accent, INK, 1, { slideNo, role: "icon glyph" });
    addShape(slide, "rect", x + 22, y + 25, 19, 3, INK, TRANSPARENT, 0, { slideNo, role: "icon glyph" });
  } else if (kind === "layers") {
    addShape(slide, "roundRect", x + 13, y + 15, 26, 13, accent, INK, 1, { slideNo, role: "icon glyph" });
    addShape(slide, "roundRect", x + 18, y + 24, 26, 13, GOLD, INK, 1, { slideNo, role: "icon glyph" });
    addShape(slide, "roundRect", x + 23, y + 33, 20, 10, CORAL, INK, 1, { slideNo, role: "icon glyph" });
  } else {
    addShape(slide, "rect", x + 16, y + 29, 6, 12, accent, TRANSPARENT, 0, { slideNo, role: "icon glyph" });
    addShape(slide, "rect", x + 25, y + 21, 6, 20, accent, TRANSPARENT, 0, { slideNo, role: "icon glyph" });
    addShape(slide, "rect", x + 34, y + 14, 6, 27, accent, TRANSPARENT, 0, { slideNo, role: "icon glyph" });
  }
}

function addCard(slide, slideNo, x, y, w, h, label, body, { accent = ACCENT, fill = PAPER_96, line = INK, iconKind = "signal" } = {}) {
  if (h < 156) {
    throw new Error(`Card is too short for editable pro-deck copy: height=${h.toFixed(1)}, minimum=156.`);
  }
  addShape(slide, "roundRect", x, y, w, h, fill, line, 1.2, { slideNo, role: `card panel: ${label}` });
  addShape(slide, "rect", x, y, 8, h, accent, TRANSPARENT, 0, { slideNo, role: `card accent: ${label}` });
  addIconBadge(slide, slideNo, x + 22, y + 24, accent, iconKind);
  addText(slide, slideNo, label, x + 88, y + 22, w - 108, 28, {
    size: 15,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    role: "card label",
  });
  const wrapped = wrapText(body, Math.max(28, Math.floor(w / 13)));
  const bodyY = y + 86;
  const bodyH = h - (bodyY - y) - 22;
  if (bodyH < 54) {
    throw new Error(`Card body area is too short: height=${bodyH.toFixed(1)}, cardHeight=${h.toFixed(1)}, label=${JSON.stringify(label)}.`);
  }
  addText(slide, slideNo, wrapped, x + 24, bodyY, w - 48, bodyH, {
    size: 15,
    color: INK,
    face: BODY_FACE,
    role: `card body: ${label}`,
  });
}

function addMetricCard(slide, slideNo, x, y, w, h, metric, label, note = null, accent = ACCENT) {
  if (h < 132) {
    throw new Error(`Metric card is too short for editable pro-deck copy: height=${h.toFixed(1)}, minimum=132.`);
  }
  addShape(slide, "roundRect", x, y, w, h, PAPER_96, INK, 1.2, { slideNo, role: `metric panel: ${label}` });
  addShape(slide, "rect", x, y, w, 7, accent, TRANSPARENT, 0, { slideNo, role: `metric accent: ${label}` });
  addText(slide, slideNo, metric, x + 22, y + 24, w - 44, 54, {
    size: 34,
    color: INK,
    bold: true,
    face: TITLE_FACE,
    role: "metric value",
  });
  addText(slide, slideNo, label, x + 24, y + 82, w - 48, 38, {
    size: 16,
    color: GRAPHITE,
    face: BODY_FACE,
    role: "metric label",
  });
  if (note) {
    addText(slide, slideNo, note, x + 24, y + h - 42, w - 48, 22, {
      size: 10,
      color: MUTED,
      face: BODY_FACE,
      role: "metric note",
    });
  }
}

function addNotes(slide, body, sourceKeys) {
  const sourceLines = (sourceKeys || []).map((key) => `- ${SOURCES[key] || key}`).join("\n");
  slide.speakerNotes.setText(`${body || ""}\n\n[Sources]\n${sourceLines}`);
}

function addReferenceCaption(slide, slideNo) {
  addText(
    slide,
    slideNo,
    "原则：每学完一页，就回到对应脚本亲手跑一次命令。",
    64,
    674,
    980,
    22,
    {
      size: 10,
      color: MUTED,
      face: BODY_FACE,
      checkFit: false,
      role: "caption",
    },
  );
}

async function slideCover(presentation) {
  const slideNo = 1;
  const data = SLIDES[0];
  const slide = presentation.slides.add();
  await addPlate(slide, slideNo);
  addShape(slide, "rect", 0, 0, W, H, "#FFFFFFCC", TRANSPARENT, 0, { slideNo, role: "cover contrast overlay" });
  addShape(slide, "rect", 64, 86, 7, 455, ACCENT, TRANSPARENT, 0, { slideNo, role: "cover accent rule" });
  addText(slide, slideNo, data.kicker, 86, 88, 520, 26, {
    size: 13,
    color: ACCENT_DARK,
    bold: true,
    face: MONO_FACE,
    role: "kicker",
  });
  addText(slide, slideNo, data.title, 82, 130, 785, 184, {
    size: 48,
    color: INK,
    bold: true,
    face: TITLE_FACE,
    role: "cover title",
  });
  addText(slide, slideNo, data.subtitle, 86, 326, 610, 86, {
    size: 20,
    color: GRAPHITE,
    face: BODY_FACE,
    role: "cover subtitle",
  });
  addShape(slide, "roundRect", 86, 456, 390, 92, PAPER_96, INK, 1.2, { slideNo, role: "cover moment panel" });
  addText(slide, slideNo, data.moment || "Replace with core idea", 112, 478, 336, 40, {
    size: 23,
    color: INK,
    bold: true,
    face: TITLE_FACE,
    role: "cover moment",
  });
  addReferenceCaption(slide, slideNo);
  addNotes(slide, data.notes, data.sources);
}

async function slideCards(presentation, idx) {
  const data = SLIDES[idx - 1];
  const slide = presentation.slides.add();
  await addPlate(slide, idx);
  addShape(slide, "rect", 0, 0, W, H, "#FFFFFFB8", TRANSPARENT, 0, { slideNo: idx, role: "content contrast overlay" });
  addHeader(slide, idx, data.kicker, idx, SLIDES.length);
  addTitleBlock(slide, idx, data.title, data.subtitle, 64, 86, 760);
  const cards = data.cards?.length
    ? data.cards
    : [
        ["Replace", "Add a specific, sourced point for this slide."],
        ["Author", "Use native PowerPoint chart objects for charts; use deterministic geometry for cards and callouts."],
        ["Verify", "Render previews, inspect them at readable size, and fix actionable layout issues within 3 total render loops."],
      ];
  const cols = Math.min(3, cards.length);
  const cardW = (1114 - (cols - 1) * 24) / cols;
  const iconKinds = ["signal", "flow", "layers"];
  for (let cardIdx = 0; cardIdx < cols; cardIdx += 1) {
    const [label, body] = cards[cardIdx];
    const x = 84 + cardIdx * (cardW + 24);
    addCard(slide, idx, x, 388, cardW, 220, label, body, { iconKind: iconKinds[cardIdx % iconKinds.length] });
  }
  addReferenceCaption(slide, idx);
  addNotes(slide, data.notes, data.sources);
}

async function slideMetrics(presentation, idx) {
  const data = SLIDES[idx - 1];
  const slide = presentation.slides.add();
  await addPlate(slide, idx);
  addShape(slide, "rect", 0, 0, W, H, "#FFFFFFBD", TRANSPARENT, 0, { slideNo: idx, role: "metrics contrast overlay" });
  addHeader(slide, idx, data.kicker, idx, SLIDES.length);
  addTitleBlock(slide, idx, data.title, data.subtitle, 64, 86, 700);
  const metrics = data.metrics || [
    ["00", "Replace metric", "Source"],
    ["00", "Replace metric", "Source"],
    ["00", "Replace metric", "Source"],
  ];
  const accents = [ACCENT, GOLD, CORAL];
  for (let metricIdx = 0; metricIdx < Math.min(3, metrics.length); metricIdx += 1) {
    const [metric, label, note] = metrics[metricIdx];
    addMetricCard(slide, idx, 92 + metricIdx * 370, 404, 330, 174, metric, label, note, accents[metricIdx % accents.length]);
  }
  addReferenceCaption(slide, idx);
  addNotes(slide, data.notes, data.sources);
}

async function createDeck() {
  await ensureDirs();
  if (!SLIDES.length) {
    throw new Error("SLIDES must contain at least one slide.");
  }
  const presentation = Presentation.create({ slideSize: { width: W, height: H } });
  await slideCover(presentation);
  for (let idx = 2; idx <= SLIDES.length; idx += 1) {
    const data = SLIDES[idx - 1];
    if (data.metrics) {
      await slideMetrics(presentation, idx);
    } else {
      await slideCards(presentation, idx);
    }
  }
  return presentation;
}

async function saveBlobToFile(blob, filePath) {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  await fs.writeFile(filePath, bytes);
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

async function nextRenderLoopNumber() {
  return (await currentRenderLoopCount()) + 1;
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
  await ensureDirs();
  const nextLoop = await nextRenderLoopNumber();
  if (nextLoop > MAX_RENDER_VERIFY_LOOPS) {
    throw new Error(
      `Render/verify/fix loop cap reached: ${MAX_RENDER_VERIFY_LOOPS} total renders are allowed. ` +
        "Do not rerender; note any remaining visual issues in the final response.",
    );
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
  const loopRecord = await appendRenderVerifyLoop(presentation, previewPaths, pptxPath);
  return { pptxPath, loopRecord };
}

const presentation = await createDeck();
const result = await verifyAndExport(presentation);
console.log(result.pptxPath);
