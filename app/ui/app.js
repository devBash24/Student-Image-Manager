const DEFAULT_CONFIG = {
  language: "en",
  student_number_patterns: ["^202\\d{7}$", "\\d{10}", "[A-Z]{2}\\d{6}"],
  department_rules: { "20": "IT", "30": "Business", "51": "Atmospheric Science" },
  excel_columns: {
    student_no: "student_no",
    first_name: "first_name",
    last_name: "last_name",
    passport_number: "passport_number",
  },
  ocr: {
    tesseract_cmd: "",
    crop_bottom_ratio: 0.28,
    threshold: 150,
    tesseract_config: "--psm 6",
    language: "eng",
    confidence_threshold: 60,
  },
  output: {
    mode: "copy",
    folder_name: "output",
    folder_path: "",
    unknown_department: "Unknown",
  },
  supported_extensions: [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"],
};

const i18n = {
  en: {
    title: "OCR Graduating Student Scanner",
    imageFolder: "Image Folder",
    excelFile: "Student Info (.xlsx)",
    outputFolder: "Output Folder",
    noFolder: "Select an image folder",
    noExcel: "Select student info spreadsheet",
    browse: "Browse...",
    startScan: "Start Scan",
    stop: "Stop",
    scanningImages: "Scanning images...",
    imagesScanned: "Images Scanned:",
    validNumbers: "Valid Student Numbers:",
    invalidErrors: "Invalid/Errors:",
    completed: "Completed",
    errors: "Errors",
    ocrLogResults: "OCR Log / Results",
    search: "Search...",
    settings: "Settings",
    openOutput: "Open output folder",
    settingsTitle: "Scanner Settings",
    validationSettings: "Validation Settings",
    studentPatterns: "Student Number Patterns",
    departmentRules: "Department Rules JSON",
    colStudent: "Student number column",
    colFirst: "First name column",
    colLast: "Last name column",
    colPassport: "Passport number column",
    ocrSettings: "OCR Settings",
    language: "UI Language",
    ocrLanguage: "OCR Language",
    ocrMode: "OCR Mode",
    confidence: "OCR Confidence Threshold",
    ocrCropRatio: "Crop bottom ratio",
    ocrThreshold: "Binarization threshold",
    ocrTesseractCmd: "Tesseract executable path",
    outputMode: "Output Mode",
    supportedExtensions: "Image extensions",
    resetDefaults: "Reset to Defaults",
    saveSettings: "Save Settings",
    closeSettings: "Close settings",
    configSaved: "Settings saved",
    defaultsLoaded: "Defaults loaded",
    chooseInputs: "Select both an image folder and Excel file first.",
    processingStarted: "Processing started",
    processingStopped: "Stop requested",
    processingComplete: "Processing complete",
    processing_image: "Processing image",
    image_success: "Valid",
    processing_stopped: "Processing stopped",
    validation_failed: "Invalid",
    ocr_failed: "OCR failed",
    excel_match_failed: "No Excel match",
    copy_failed: "Copy failed",
    noFailures: "No failed images",
    noLogs: "No scan results yet",
    noImage: "No image preview",
    invalidConfig: "Fix the settings before scanning",
    image_missing: "Image preview unavailable",
  },
  "zh-CN": {
    title: "OCR 毕业学生照片扫描器",
    imageFolder: "照片文件夹",
    excelFile: "学生信息（.xlsx）",
    outputFolder: "输出文件夹",
    noFolder: "选择照片文件夹",
    noExcel: "选择学生信息表",
    browse: "浏览...",
    startScan: "开始扫描",
    stop: "停止",
    scanningImages: "正在扫描照片...",
    imagesScanned: "已扫描照片：",
    validNumbers: "有效学生编号：",
    invalidErrors: "无效/错误：",
    completed: "已完成",
    errors: "错误",
    ocrLogResults: "OCR 日志 / 结果",
    search: "搜索...",
    settings: "设置",
    openOutput: "打开输出文件夹",
    settingsTitle: "扫描器设置",
    validationSettings: "验证设置",
    studentPatterns: "学生编号规则",
    departmentRules: "院系规则 JSON",
    colStudent: "学生编号列",
    colFirst: "名字列",
    colLast: "姓氏列",
    colPassport: "护照号码列",
    ocrSettings: "OCR 设置",
    language: "界面语言",
    ocrLanguage: "OCR 语言",
    ocrMode: "OCR 模式",
    confidence: "OCR 置信度阈值",
    ocrCropRatio: "底部裁剪比例",
    ocrThreshold: "二值化阈值",
    ocrTesseractCmd: "Tesseract 可执行文件路径",
    outputMode: "输出模式",
    supportedExtensions: "图片扩展名",
    resetDefaults: "恢复默认",
    saveSettings: "保存设置",
    closeSettings: "关闭设置",
    configSaved: "设置已保存",
    defaultsLoaded: "默认设置已载入",
    chooseInputs: "请先选择照片文件夹和 Excel 文件。",
    processingStarted: "开始处理",
    processingStopped: "已请求停止",
    processingComplete: "处理完成",
    processing_image: "正在处理照片",
    image_success: "有效",
    processing_stopped: "处理已停止",
    validation_failed: "无效",
    ocr_failed: "OCR 失败",
    excel_match_failed: "没有匹配的 Excel 记录",
    copy_failed: "复制失败",
    noFailures: "没有失败的照片",
    noLogs: "暂无扫描结果",
    noImage: "暂无图片预览",
    invalidConfig: "扫描前请修正设置",
    image_missing: "图片预览不可用",
  },
};

const state = {
  route: "setup",
  config: null,
  language: "en",
  imageFolder: "",
  excelFile: "",
  outputFolder: "",
  progress: { total: 0, processed: 0, success: 0, failed: 0, percent: 0 },
  logs: [],
  lastResult: null,
  lastPreviewPath: "",
};

const $ = (id) => document.getElementById(id);
const clone = (value) => JSON.parse(JSON.stringify(value));
const t = (key) => (i18n[state.language] && i18n[state.language][key]) || i18n.en[key] || key;

function setRoute(route) {
  state.route = route;
  document.body.dataset.route = route;
}

function joinPath(root, child) {
  if (!root) return child || "";
  if (!child) return root;
  const slash = root.includes("\\") ? "\\" : "/";
  return root.endsWith("\\") || root.endsWith("/") ? `${root}${child}` : `${root}${slash}${child}`;
}

function defaultOutputFolder() {
  const configured = state.outputFolder || state.config?.output?.folder_path || "";
  if (configured) return configured;
  return state.imageFolder ? joinPath(state.imageFolder, state.config?.output?.folder_name || "output") : "output";
}

function translate() {
  document.documentElement.lang = state.language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => {
    element.setAttribute("placeholder", t(element.dataset.i18nPlaceholder));
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((element) => {
    element.setAttribute("aria-label", t(element.dataset.i18nAria));
  });
  $("imageFolderText").textContent = state.imageFolder || t("noFolder");
  $("excelFileText").textContent = state.excelFile || t("noExcel");
  $("outputFolderText").textContent = defaultOutputFolder();
}

function addLog(entry) {
  state.logs.unshift({ time: new Date().toLocaleTimeString(), ...entry });
  renderLogs();
}

function renderLogs() {
  const list = $("resultLog");
  const query = $("logSearch").value.trim().toLowerCase();
  list.innerHTML = "";
  const filtered = state.logs.filter((entry) => {
    const text = `${entry.label || ""} ${entry.image || ""} ${entry.student_no || ""}`.toLowerCase();
    return !query || text.includes(query);
  });
  if (filtered.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = t(state.logs.length === 0 ? "noLogs" : "noFailures");
    list.appendChild(empty);
    return;
  }
  filtered.forEach((entry) => {
    const item = document.createElement("li");
    item.className = entry.level === "error" ? "error" : "";
    const suffix = entry.student_no ? ` ${entry.student_no}` : "";
    item.textContent = `${entry.label}${suffix}${entry.image ? `: ${entry.image}` : ""}`;
    list.appendChild(item);
  });
}

function renderProgress(payload = state.progress) {
  state.progress = { ...state.progress, ...payload };
  $("scannedCount").textContent = `${state.progress.processed || 0} / ${state.progress.total || 0}`;
  $("validCount").textContent = state.progress.success || 0;
  $("errorCount").textContent = state.progress.failed || 0;
  $("ringErrors").textContent = state.progress.failed || 0;
  $("percentValue").textContent = `${state.progress.percent || 0}%`;
  $("progressBar").style.width = `${state.progress.percent || 0}%`;
  $("percentRing").style.setProperty("--value", state.progress.percent || 0);
  const errorValue = state.progress.total ? Math.min(100, Math.round((state.progress.failed / state.progress.total) * 100)) : 0;
  document.querySelector(".ring--errors").style.setProperty("--value", errorValue);
}

async function setPreviewImage(path, targetId = "scanImage") {
  const image = $(targetId);
  if (!path || !image) return;
  try {
    const result = await window.pywebview.api.get_image_data_url(path);
    if (!result.ok) {
      image.removeAttribute("src");
      return;
    }
    image.src = result.src;
    state.lastPreviewPath = path;
  } catch {
    image.removeAttribute("src");
  }
}

async function loadSampleImage() {
  if (!state.imageFolder || !state.config) return;
  const result = await window.pywebview.api.sample_image(state.imageFolder, state.config);
  if (!result.ok) return;
  await setPreviewImage(result.image, "scanImage");
  await setPreviewImage(result.image, "resultImage");
}

function loadForm(config) {
  $("patterns").value = (config.student_number_patterns || []).join("\n");
  $("departments").value = JSON.stringify(config.department_rules || {}, null, 2);
  $("colStudent").value = config.excel_columns?.student_no || "student_no";
  $("colFirst").value = config.excel_columns?.first_name || "first_name";
  $("colLast").value = config.excel_columns?.last_name || "last_name";
  $("colPassport").value = config.excel_columns?.passport_number || "passport_number";
  $("languageSelect").value = config.language || "en";
  $("ocrLanguage").value = config.ocr?.language || "eng";
  $("ocrMode").value = config.ocr?.tesseract_config || "--psm 6";
  $("confidence").value = config.ocr?.confidence_threshold ?? 60;
  $("ocrCrop").value = config.ocr?.crop_bottom_ratio ?? 0.28;
  $("ocrThreshold").value = config.ocr?.threshold ?? 150;
  $("ocrTesseractCmd").value = config.ocr?.tesseract_cmd || "";
  $("outputMode").value = config.output?.mode === "move" ? "move" : "copy";
  $("supportedExtensions").value = (config.supported_extensions || []).join(", ");
}

function readConfigFromForm() {
  const config = clone(state.config || DEFAULT_CONFIG);
  config.language = $("languageSelect").value;
  config.student_number_patterns = $("patterns").value.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  config.department_rules = JSON.parse($("departments").value);
  config.excel_columns = {
    student_no: $("colStudent").value.trim(),
    first_name: $("colFirst").value.trim(),
    last_name: $("colLast").value.trim(),
    passport_number: $("colPassport").value.trim(),
  };
  const crop = parseFloat($("ocrCrop").value);
  const threshold = parseInt($("ocrThreshold").value, 10);
  const confidence = parseInt($("confidence").value, 10);
  if (!Number.isFinite(crop) || crop < 0.05 || crop > 1) throw new Error(t("invalidConfig"));
  if (!Number.isFinite(threshold) || threshold < 0 || threshold > 255) throw new Error(t("invalidConfig"));
  config.ocr = {
    ...(config.ocr || {}),
    language: $("ocrLanguage").value,
    tesseract_config: $("ocrMode").value,
    confidence_threshold: Number.isFinite(confidence) ? confidence : 60,
    crop_bottom_ratio: crop,
    threshold,
    tesseract_cmd: $("ocrTesseractCmd").value.trim(),
  };
  const extensions = $("supportedExtensions").value
    .split(/[\s,]+/)
    .map((ext) => ext.trim())
    .filter(Boolean)
    .map((ext) => (ext.startsWith(".") ? ext.toLowerCase() : `.${ext.toLowerCase()}`));
  if (extensions.length === 0) throw new Error(t("invalidConfig"));
  config.supported_extensions = extensions;
  config.output = {
    ...(config.output || {}),
    mode: $("outputMode").value === "move" ? "move" : "copy",
    folder_name: config.output?.folder_name || "output",
    folder_path: state.outputFolder || "",
    unknown_department: config.output?.unknown_department || "Unknown",
  };
  return config;
}

async function saveSettings({ close = false } = {}) {
  state.config = readConfigFromForm();
  state.language = state.config.language;
  await window.pywebview.api.save_config(state.config);
  translate();
  addLog({ level: "info", label: t("configSaved") });
  if (close) closeSettings();
}

function openSettings() {
  $("settingsModal").removeAttribute("hidden");
  $("languageSelect").focus();
}

function closeSettings() {
  $("settingsModal").setAttribute("hidden", "");
}

function requireInputs() {
  if (!state.imageFolder || !state.excelFile) {
    addLog({ level: "error", label: t("chooseInputs") });
    return false;
  }
  return true;
}

async function startScan() {
  if (!requireInputs()) return;
  try {
    state.config = readConfigFromForm();
    state.language = state.config.language;
    await window.pywebview.api.save_config(state.config);
    state.logs = [];
    state.lastResult = null;
    renderLogs();
    renderProgress({ total: 0, processed: 0, success: 0, failed: 0, percent: 0 });
    $("scanStatus").textContent = t("processingStarted");
    setRoute("scanning");
    await loadSampleImage();
    const result = await window.pywebview.api.start_processing(state.imageFolder, state.excelFile, state.config);
    if (!result.ok) {
      addLog({ level: "error", label: result.error });
      setRoute("results");
      return;
    }
    addLog({ level: "info", label: t("processingStarted") });
  } catch (error) {
    addLog({ level: "error", label: error.message || t("invalidConfig") });
    setRoute("results");
  }
}

async function showResultPreview(result) {
  const success = result?.successes && result.successes[0];
  const failure = result?.errors && result.errors[0];
  const record = success || failure;
  if (!record) return;
  const path = record.target || record.image;
  await setPreviewImage(path, "resultImage");
  $("resultStudent").textContent = record.student_no || "-";
}

window.appEvents = async (event, payload) => {
  if (event === "progress") {
    renderProgress(payload);
    return;
  }
  if (event === "log") {
    const label = t(payload.message);
    addLog({ level: payload.level, label, image: payload.image, student_no: payload.student_no });
    if (payload.image) {
      $("scanStatus").textContent = `${label}: ${payload.image}`;
      await setPreviewImage(joinPath(state.imageFolder, payload.image), "scanImage");
    }
    if (payload.student_no) $("scanStudent").textContent = payload.student_no;
    return;
  }
  if (event === "done") {
    state.lastResult = payload;
    addLog({ level: payload.ok ? "info" : "error", label: payload.ok ? t("processingComplete") : payload.error });
    renderProgress(payload);
    await showResultPreview(payload);
    renderLogs();
    setRoute("results");
  }
};

async function boot() {
  state.config = await window.pywebview.api.get_config();
  state.language = state.config.language || "en";
  state.outputFolder = state.config.output?.folder_path || "";
  loadForm(state.config);
  translate();
  renderProgress();
  renderLogs();

  $("selectFolder").addEventListener("click", async () => {
    const path = await window.pywebview.api.select_image_folder();
    if (!path) return;
    state.imageFolder = path;
    translate();
    await loadSampleImage();
  });

  $("selectExcel").addEventListener("click", async () => {
    const path = await window.pywebview.api.select_excel_file();
    if (!path) return;
    state.excelFile = path;
    translate();
  });

  $("selectOutput").addEventListener("click", async () => {
    const path = await window.pywebview.api.select_output_folder();
    if (!path) return;
    state.outputFolder = path;
    translate();
  });

  $("setupStart").addEventListener("click", startScan);
  $("restartScan").addEventListener("click", startScan);
  $("stopScan").addEventListener("click", async () => {
    await window.pywebview.api.stop_processing();
    $("scanStatus").textContent = t("processingStopped");
    addLog({ level: "info", label: t("processingStopped") });
  });
  $("openOutput").addEventListener("click", async () => {
    const result = await window.pywebview.api.open_output_folder();
    if (!result.ok) addLog({ level: "error", label: result.error });
  });
  $("openSettings").addEventListener("click", openSettings);
  $("resultsSettings").addEventListener("click", openSettings);
  $("closeSettings").addEventListener("click", closeSettings);
  $("settingsBackdrop").addEventListener("click", closeSettings);
  $("saveConfig").addEventListener("click", () => saveSettings({ close: true }).catch((error) => addLog({ level: "error", label: error.message })));
  $("resetSettings").addEventListener("click", () => {
    state.config = clone(DEFAULT_CONFIG);
    state.language = state.config.language;
    state.outputFolder = "";
    loadForm(state.config);
    translate();
    addLog({ level: "info", label: t("defaultsLoaded") });
  });
  $("languageSelect").addEventListener("change", async () => {
    state.language = $("languageSelect").value;
    translate();
  });
  $("logSearch").addEventListener("input", renderLogs);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !$("settingsModal").hasAttribute("hidden")) closeSettings();
  });
}

window.addEventListener("pywebviewready", boot);
