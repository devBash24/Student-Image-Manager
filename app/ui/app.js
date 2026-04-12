const i18n = {
  en: {
    eyebrow: "VANTIX",
    title: "Student Image Organizer",
    language: "Language",
    inputs: "Inputs",
    selectFolder: "Select image folder",
    selectExcel: "Select Excel file",
    noFolder: "No image folder selected",
    noExcel: "No Excel file selected",
    dropHint: "Use the buttons above to select files.",
    config: "Matching & columns",
    regexPatterns: "Student number regex patterns, one per line",
    departmentRules: "Department rules as JSON",
    colStudent: "Student number column",
    colFirst: "First name column",
    colLast: "Last name column",
    colPassport: "Passport number column",
    saveConfig: "Save config",
    saveSettings: "Save settings",
    settingsTitle: "Settings",
    settingsGeneral: "General",
    settingsClose: "Close",
    settingsAdvanced: "Advanced (OCR & output)",
    ocrCropRatio: "OCR crop bottom ratio (0.05–1)",
    ocrThreshold: "OCR binarization threshold (0–255)",
    ocrTesseractCmd:
      "Tesseract executable path (optional — auto-detects common installs if empty)",
    ocrTesseract: "Tesseract config string",
    outputMode: "Output mode",
    outputModeCopy: "Copy files",
    outputModeMove: "Move files",
    outputFolderName: "Output folder name",
    outputUnknownDept: "Unknown department label",
    supportedExtensions: "Image extensions (comma-separated)",
    settingsOpenAria: "Open settings",
    settingsCloseAria: "Close settings",
    invalidCrop: "Crop ratio must be between 0.05 and 1",
    invalidThreshold: "Threshold must be between 0 and 255",
    invalidExtensions: "Add at least one file extension",
    processing: "Processing",
    start: "Start",
    stop: "Stop",
    total: "Total",
    processed: "Processed",
    success: "Success",
    failed: "Failed",
    results: "Results",
    openOutput: "Open output folder",
    logs: "Logs",
    configSaved: "Config saved",
    chooseInputs: "Select both an image folder and an Excel file first.",
    processingStarted: "Processing started",
    processingStopped: "Stop requested",
    processingComplete: "Processing complete",
    processing_image: "Processing image",
    image_success: "Image processed",
    processing_stopped: "Processing stopped",
    validation_failed: "Validation failed",
    ocr_failed: "OCR failed",
    excel_match_failed: "No Excel match",
    copy_failed: "Copy failed",
    noFailures: "No failed images",
  },
  "zh-CN": {
    eyebrow: "VANTIX",
    title: "学生照片整理工具",
    language: "语言",
    inputs: "输入",
    selectFolder: "选择照片文件夹",
    selectExcel: "选择 Excel 文件",
    noFolder: "尚未选择照片文件夹",
    noExcel: "尚未选择 Excel 文件",
    dropHint: "请使用上方按钮选择文件。",
    config: "匹配与列名",
    regexPatterns: "学生编号正则规则，每行一个",
    departmentRules: "院系规则 JSON",
    colStudent: "学生编号列",
    colFirst: "名字列",
    colLast: "姓氏列",
    colPassport: "护照号码列",
    saveConfig: "保存配置",
    saveSettings: "保存设置",
    settingsTitle: "设置",
    settingsGeneral: "常规",
    settingsClose: "关闭",
    settingsAdvanced: "高级（OCR 与输出）",
    ocrCropRatio: "OCR 底部裁剪比例（0.05–1）",
    ocrThreshold: "OCR 二值化阈值（0–255）",
    ocrTesseractCmd: "Tesseract 可执行文件路径（可留空，将自动检测常见安装位置）",
    ocrTesseract: "Tesseract 参数字符串",
    outputMode: "输出模式",
    outputModeCopy: "复制文件",
    outputModeMove: "移动文件",
    outputFolderName: "输出文件夹名称",
    outputUnknownDept: "未知院系显示名称",
    supportedExtensions: "图片扩展名（逗号分隔）",
    settingsOpenAria: "打开设置",
    settingsCloseAria: "关闭设置",
    invalidCrop: "裁剪比例必须在 0.05 到 1 之间",
    invalidThreshold: "阈值必须在 0 到 255 之间",
    invalidExtensions: "请至少填写一个扩展名",
    processing: "处理",
    start: "开始",
    stop: "停止",
    total: "总数",
    processed: "已处理",
    success: "成功",
    failed: "失败",
    results: "结果",
    openOutput: "打开输出文件夹",
    logs: "日志",
    configSaved: "配置已保存",
    chooseInputs: "请先选择照片文件夹和 Excel 文件。",
    processingStarted: "开始处理",
    processingStopped: "已请求停止",
    processingComplete: "处理完成",
    processing_image: "正在处理照片",
    image_success: "照片处理完成",
    processing_stopped: "处理已停止",
    validation_failed: "验证失败",
    ocr_failed: "OCR 失败",
    excel_match_failed: "没有匹配的 Excel 记录",
    copy_failed: "复制失败",
    noFailures: "没有失败的照片",
  },
};

const state = {
  config: null,
  language: "en",
  imageFolder: "",
  excelFile: "",
};

const $ = (id) => document.getElementById(id);
const t = (key) => (i18n[state.language] && i18n[state.language][key]) || i18n.en[key] || key;

function languageDisplayName() {
  return state.language === "zh-CN" ? "简体中文" : "English";
}

function translate() {
  document.documentElement.lang = state.language;
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  $("imageFolder").textContent = state.imageFolder || t("noFolder");
  $("excelFile").textContent = state.excelFile || t("noExcel");
  const hint = $("localeHint");
  if (hint) {
    hint.textContent = `${t("language")}: ${languageDisplayName()}`;
  }
  const openBtn = $("openSettings");
  if (openBtn) {
    openBtn.setAttribute("aria-label", t("settingsOpenAria"));
  }
  const closeIcon = $("closeSettings");
  if (closeIcon) {
    closeIcon.setAttribute("aria-label", t("settingsCloseAria"));
  }
  const outputMode = $("outputMode");
  if (outputMode && outputMode.options.length >= 2) {
    outputMode.options[0].textContent = t("outputModeCopy");
    outputMode.options[1].textContent = t("outputModeMove");
  }
}

function addLog(message, level = "info", detail = "") {
  const item = document.createElement("li");
  item.className = level;
  item.textContent = detail ? `${message}: ${detail}` : message;
  $("logs").prepend(item);
}

function requireInputs() {
  if (!state.imageFolder || !state.excelFile) {
    addLog(t("chooseInputs"), "error");
    return false;
  }
  return true;
}

function readConfigFromForm() {
  const config = JSON.parse(JSON.stringify(state.config));
  config.language = state.language;
  config.student_number_patterns = $("patterns").value
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  config.department_rules = JSON.parse($("departments").value);
  config.excel_columns = {
    student_no: $("colStudent").value.trim(),
    first_name: $("colFirst").value.trim(),
    last_name: $("colLast").value.trim(),
    passport_number: $("colPassport").value.trim(),
  };

  const crop = parseFloat($("ocrCrop").value);
  if (!Number.isFinite(crop) || crop < 0.05 || crop > 1) {
    throw new Error(t("invalidCrop"));
  }
  const threshold = parseInt($("ocrThreshold").value, 10);
  if (!Number.isFinite(threshold) || threshold < 0 || threshold > 255) {
    throw new Error(t("invalidThreshold"));
  }
  const tesseract = $("ocrTesseract").value.trim() || "--psm 6";
  const tesseractCmd = $("ocrTesseractCmd").value.trim();
  config.ocr = {
    ...(config.ocr || {}),
    crop_bottom_ratio: crop,
    threshold,
    tesseract_config: tesseract,
    tesseract_cmd: tesseractCmd,
  };

  const mode = $("outputMode").value === "move" ? "move" : "copy";
  const folderName = $("outputFolder").value.trim() || "output";
  const unknownDept = $("outputUnknown").value.trim() || "Unknown";
  config.output = {
    ...(config.output || {}),
    mode,
    folder_name: folderName,
    unknown_department: unknownDept,
  };

  const exts = $("supportedExtensions").value
    .split(/[\s,]+/)
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => (s.startsWith(".") ? s.toLowerCase() : `.${s.toLowerCase()}`));
  if (exts.length === 0) {
    throw new Error(t("invalidExtensions"));
  }
  config.supported_extensions = exts;

  return config;
}

function loadForm(config) {
  $("patterns").value = (config.student_number_patterns || []).join("\n");
  $("departments").value = JSON.stringify(config.department_rules || {}, null, 2);
  $("colStudent").value = config.excel_columns?.student_no || "student_no";
  $("colFirst").value = config.excel_columns?.first_name || "first_name";
  $("colLast").value = config.excel_columns?.last_name || "last_name";
  $("colPassport").value = config.excel_columns?.passport_number || "passport_number";

  const ocr = config.ocr || {};
  $("ocrCrop").value = ocr.crop_bottom_ratio ?? 0.28;
  $("ocrThreshold").value = ocr.threshold ?? 150;
  $("ocrTesseractCmd").value = ocr.tesseract_cmd ?? "";
  $("ocrTesseract").value = ocr.tesseract_config ?? "--psm 6";

  const out = config.output || {};
  $("outputMode").value = out.mode === "move" ? "move" : "copy";
  $("outputFolder").value = out.folder_name ?? "output";
  $("outputUnknown").value = out.unknown_department ?? "Unknown";

  $("supportedExtensions").value = (config.supported_extensions || []).join(", ");
}

function updateProgress(payload) {
  $("total").textContent = payload.total ?? 0;
  $("processed").textContent = payload.processed ?? 0;
  $("success").textContent = payload.success ?? 0;
  $("failed").textContent = payload.failed ?? 0;
  $("bar").style.width = `${payload.percent ?? 0}%`;
  $("percent").textContent = `${payload.percent ?? 0}%`;
}

window.appEvents = (event, payload) => {
  if (event === "log") {
    const label = t(payload.message);
    addLog(payload.image ? `${label}: ${payload.image}` : label, payload.level || "info");
  }
  if (event === "progress") {
    updateProgress(payload);
  }
  if (event === "done") {
    addLog(t("processingComplete"));
    const list = $("failedList");
    list.innerHTML = "";
    if (!payload.errors || payload.errors.length === 0) {
      const item = document.createElement("li");
      item.textContent = t("noFailures");
      list.appendChild(item);
      return;
    }
    payload.errors.forEach((error) => {
      const item = document.createElement("li");
      item.className = "error";
      item.textContent = `${t(error.reason)}: ${error.image}`;
      list.appendChild(item);
    });
  }
};

function isSettingsModalOpen() {
  const modal = $("settingsModal");
  return modal && !modal.hasAttribute("hidden");
}

function openSettingsModal() {
  const modal = $("settingsModal");
  if (!modal) return;
  state._modalPreviousFocus = document.activeElement;
  modal.removeAttribute("hidden");
  document.body.classList.add("modal-open");
  $("openSettings").setAttribute("aria-expanded", "true");
  $("languageSelect").focus();
}

function closeSettingsModal() {
  const modal = $("settingsModal");
  if (!modal) return;
  modal.setAttribute("hidden", "");
  document.body.classList.remove("modal-open");
  $("openSettings").setAttribute("aria-expanded", "false");
  const prev = state._modalPreviousFocus;
  if (prev && typeof prev.focus === "function") {
    prev.focus();
  } else {
    $("openSettings").focus();
  }
}

async function boot() {
  state.config = await window.pywebview.api.get_config();
  state.language = state.config.language || "en";
  $("languageSelect").value = state.language;
  loadForm(state.config);
  translate();

  $("openSettings").addEventListener("click", () => {
    openSettingsModal();
  });

  $("closeSettings").addEventListener("click", () => {
    closeSettingsModal();
  });

  $("dismissSettings").addEventListener("click", () => {
    closeSettingsModal();
  });

  $("settingsBackdrop").addEventListener("click", () => {
    closeSettingsModal();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    if (!isSettingsModalOpen()) return;
    event.preventDefault();
    closeSettingsModal();
  });

  $("languageSelect").addEventListener("change", async (event) => {
    state.language = event.target.value;
    translate();
    try {
      state.config = readConfigFromForm();
    } catch {
      state.config = JSON.parse(JSON.stringify(state.config));
      state.config.language = state.language;
    }
    await window.pywebview.api.save_config(state.config);
  });

  $("selectFolder").addEventListener("click", async () => {
    const path = await window.pywebview.api.select_image_folder();
    if (path) {
      state.imageFolder = path;
      translate();
    }
  });

  $("selectExcel").addEventListener("click", async () => {
    const path = await window.pywebview.api.select_excel_file();
    if (path) {
      state.excelFile = path;
      translate();
    }
  });

  $("saveConfig").addEventListener("click", async () => {
    try {
      state.config = readConfigFromForm();
      await window.pywebview.api.save_config(state.config);
      addLog(t("configSaved"));
    } catch (error) {
      addLog(error.message, "error");
    }
  });

  $("start").addEventListener("click", async () => {
    if (!requireInputs()) return;
    try {
      state.config = readConfigFromForm();
      await window.pywebview.api.save_config(state.config);
      const result = await window.pywebview.api.start_processing(state.imageFolder, state.excelFile, state.config);
      if (!result.ok) {
        addLog(result.error, "error");
        return;
      }
      addLog(t("processingStarted"));
    } catch (error) {
      addLog(error.message, "error");
    }
  });

  $("stop").addEventListener("click", async () => {
    await window.pywebview.api.stop_processing();
    addLog(t("processingStopped"));
  });

  $("openOutput").addEventListener("click", async () => {
    const result = await window.pywebview.api.open_output_folder();
    if (!result.ok) addLog(result.error, "error");
  });
}

window.addEventListener("pywebviewready", boot);
