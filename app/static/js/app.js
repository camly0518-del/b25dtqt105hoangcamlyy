/**
 * NovaData AI Enterprise - Luminous Galaxy Client Logic
 * Powered by NovaTech Intelligence Group
 * 6-Stage Comprehensive Analytics Pipeline
 */

let currentTab = 1;
let currentDiagnosis = null;
let currentProposals = [];
let hasCleanedData = false;

// Bảng dữ liệu thô (Bước 1) - Quản lý 100% dữ liệu
let rawColumns = [];
let rawAllRecords = [];
let rawFilteredRecords = [];
let rawCurrentPage = 1;
let rawPageSize = 15;

// Bảng dữ liệu sạch (Bước 4) - Quản lý 100% dữ liệu
let cleanColumns = [];
let cleanAllRecords = [];
let cleanFilteredRecords = [];
let cleanCurrentPage = 1;
let cleanPageSize = 15;

// ================= HỆ THỐNG GIAO DIỆN SÁNG / TỐI (LIGHT / DARK THEME) =================
let currentTheme = localStorage.getItem("novadata_theme") || "dark";

function initTheme() {
    applyTheme(currentTheme);
}

function toggleTheme() {
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    showToast(`Đã chuyển sang ${nextTheme === "light" ? "Giao diện Sáng (Trắng)" : "Giao diện Tối (Đen/Galaxy)"}`, "info");
}

function applyTheme(theme) {
    currentTheme = theme;
    localStorage.setItem("novadata_theme", theme);

    const htmlEl = document.documentElement;
    const bodyEl = document.body;
    const themeBtn = document.getElementById("theme-toggle-btn");
    const themeIcon = document.getElementById("theme-toggle-icon");
    const themeText = document.getElementById("theme-toggle-text");

    htmlEl.setAttribute("data-theme", theme);
    if (bodyEl) bodyEl.setAttribute("data-theme", theme);

    if (theme === "light") {
        htmlEl.classList.add("light-mode");
        if (bodyEl) bodyEl.classList.add("light-mode");
        if (themeIcon) themeIcon.className = "fas fa-moon text-indigo-600";
        if (themeText) themeText.innerText = "Giao diện Tối";
        if (themeBtn) themeBtn.title = "Chuyển sang giao diện Tối (Đen)";
    } else {
        htmlEl.classList.remove("light-mode");
        if (bodyEl) bodyEl.classList.remove("light-mode");
        if (themeIcon) themeIcon.className = "fas fa-sun text-amber-300";
        if (themeText) themeText.innerText = "Giao diện Sáng";
        if (themeBtn) themeBtn.title = "Chuyển sang giao diện Sáng (Trắng)";
    }

    // Cập nhật lại các thẻ mẫu ngay khi đổi theme để màu sắc thích ứng tức thì
    initSampleDatasets();

    // Nếu biểu đồ EDA đã tải, vẽ lại biểu đồ tương thích màu
    if (window.lastChartsData) {
        renderCharts(window.lastChartsData);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initSampleDatasets();
    initDragAndDrop();
    checkInitialState();
});

// ================= GIAO DIỆN ĐẦU TIÊN & CHUYỂN BƯỚC QUY TRÌNH =================
function startProcessWorkflow(stepIndex = 1) {
    const welcomeHero = document.getElementById("welcome-hero-section");
    const stepperBar = document.getElementById("stepper-process-bar");
    const stepsContainer = document.getElementById("workflow-steps-container");
    const navStartBtn = document.getElementById("nav-btn-start");

    if (welcomeHero) welcomeHero.classList.add("hidden");
    if (stepperBar) stepperBar.classList.remove("hidden");
    if (stepsContainer) stepsContainer.classList.remove("hidden");
    if (navStartBtn) {
        navStartBtn.classList.add("opacity-50", "pointer-events-none");
    }

    switchTab(stepIndex, true);
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function showWelcomeScreen() {
    const welcomeHero = document.getElementById("welcome-hero-section");
    const stepperBar = document.getElementById("stepper-process-bar");
    const stepsContainer = document.getElementById("workflow-steps-container");
    const navStartBtn = document.getElementById("nav-btn-start");

    if (welcomeHero) welcomeHero.classList.remove("hidden");
    if (stepperBar) stepperBar.classList.add("hidden");
    if (stepsContainer) stepsContainer.classList.add("hidden");
    if (navStartBtn) {
        navStartBtn.classList.remove("opacity-50", "pointer-events-none");
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
}

// ================= STEPPER & TABS (QUY TRÌNH 6 BƯỚC) =================
function switchTab(tabIndex, force = false) {
    if (tabIndex === currentTab && !force) return;

    // Ẩn tất cả tabs (1 -> 6)
    for (let i = 1; i <= 6; i++) {
        const tabEl = document.getElementById(`tab-content-${i}`);
        const btnEl = document.getElementById(`step-btn-${i}`);
        if (tabEl) tabEl.classList.add("hidden");
        if (btnEl) btnEl.classList.remove("active");
    }

    // Hiển thị tab được chọn
    const targetTab = document.getElementById(`tab-content-${tabIndex}`);
    const targetBtn = document.getElementById(`step-btn-${tabIndex}`);

    if (targetTab) targetTab.classList.remove("hidden");
    if (targetBtn) targetBtn.classList.add("active");

    currentTab = tabIndex;

    // Cuộn nhẹ lên đầu thanh Stepper
    const stepperBar = document.getElementById("stepper-process-bar");
    if (stepperBar && !stepperBar.classList.contains("hidden")) {
        stepperBar.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    // Kích hoạt logic tự động theo từng bước
    if (tabIndex === 2) {
        if (!currentDiagnosis) fetchDiagnosis();
    } else if (tabIndex === 3) {
        if (!currentDiagnosis) fetchDiagnosis();
    } else if (tabIndex === 4) {
        // Đã ở trang đối soát sạch
    } else if (tabIndex === 5) {
        runDeepAnalysis();
    } else if (tabIndex === 6) {
        reloadReport();
    }
}

// ================= BƯỚC 1: NẠP & QUẢN LÝ TOÀN BỘ BẢNG DỮ LIỆU =================
let cachedSamples = null;

async function initSampleDatasets() {
    try {
        if (!cachedSamples) {
            const res = await fetch("/api/samples");
            cachedSamples = await res.json();
        }
        const container = document.getElementById("sample-dataset-cards");
        if (!container || !cachedSamples) return;

        container.innerHTML = cachedSamples.map(s => `
            <div onclick="loadSampleDataset('${s.id}')" class="sample-dataset-card p-4 rounded-2xl transition cursor-pointer flex flex-col justify-between group shadow-md">
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <div class="w-9 h-9 rounded-xl sample-card-icon shadow-sm flex items-center justify-center text-sm group-hover:scale-110 transition">
                            <i class="fas ${s.icon}"></i>
                        </div>
                        <span class="text-[10px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full sample-card-badge">${s.badge}</span>
                    </div>
                    <h4 class="font-bold sample-card-title text-sm mb-1 transition">${s.name}</h4>
                    <p class="text-xs sample-card-desc leading-relaxed">${s.desc}</p>
                </div>
                <div class="mt-3 pt-2.5 sample-card-action flex items-center justify-between text-xs font-bold">
                    <span>Nạp dữ liệu kinh doanh này</span>
                    <i class="fas fa-arrow-right text-[11px] group-hover:translate-x-1 transition"></i>
                </div>
            </div>
        `).join("");
    } catch (err) {
        console.error("Lỗi khi tải danh sách mẫu:", err);
    }
}

async function loadSampleDataset(sampleId) {
    startProcessWorkflow(1);
    showUploadSpinner(true);
    try {
        const res = await fetch(`/api/load-sample/${sampleId}`, { method: "POST" });
        const data = await res.json();
        if (data.status === "success") {
            handleDataLoaded(data);
            showToast(`Đã nạp toàn bộ bảng: ${data.dataset_name} (${data.rows} dòng)`, "success");
        } else {
            showToast(data.detail || "Không thể tải bộ mẫu", "error");
        }
    } catch (err) {
        showToast("Lỗi kết nối máy chủ: " + err.message, "error");
    } finally {
        showUploadSpinner(false);
    }
}

function initDragAndDrop() {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");

    if (!dropZone || !fileInput) return;

    ['dragenter', 'dragover'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            dropZone.classList.add("border-purple-300", "bg-[#1f2863]/90");
        });
    });

    ['dragleave', 'drop'].forEach(name => {
        dropZone.addEventListener(name, (e) => {
            e.preventDefault();
            dropZone.classList.remove("border-purple-300", "bg-[#1f2863]/90");
        });
    });

    dropZone.addEventListener("drop", (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) uploadFile(files[0]);
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files.length > 0) uploadFile(e.target.files[0]);
    });
}

async function uploadFile(file) {
    startProcessWorkflow(1);
    showUploadSpinner(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (res.ok && data.status === "success") {
            handleDataLoaded(data);
            showToast(`Đã nạp toàn bộ ${data.rows} dòng của tệp: ${file.name}`, "success");
        } else {
            showToast(data.detail || "Lỗi khi xử lý file tải lên", "error");
        }
    } catch (err) {
        showToast("Lỗi tải tệp: " + err.message, "error");
    } finally {
        showUploadSpinner(false);
    }
}

function handleDataLoaded(data) {
    // Cập nhật nhãn bộ dữ liệu
    const label = document.getElementById("current-dataset-label");
    if (label) label.innerText = data.dataset_name;
    const badge = document.getElementById("dataset-badge");
    if (badge) badge.classList.remove("hidden");

    // Đánh dấu bước 1 hoàn thành
    const btn1 = document.getElementById("step-btn-1");
    if (btn1) btn1.classList.add("completed");

    // Nạp toàn bộ dữ liệu thô (100% dòng, không cắt bớt)
    rawColumns = data.columns || [];
    rawAllRecords = data.all_data || data.preview || [];
    rawFilteredRecords = [...rawAllRecords];
    rawCurrentPage = 1;

    // Hiển thị bảng toàn bộ dữ liệu thô
    const previewContainer = document.getElementById("raw-preview-container");
    if (previewContainer) previewContainer.classList.remove("hidden");
    renderRawTable();

    // Chẩn đoán chất lượng cho Bước 2 & 3
    if (data.diagnosis) {
        currentDiagnosis = data.diagnosis;
        renderDiagnosis(data.diagnosis);
    }
}

// Render bảng dữ liệu thô với phân trang và tìm kiếm (Bước 1)
function renderRawTable() {
    const table = document.getElementById("raw-preview-table");
    const countTag = document.getElementById("raw-count-tag");
    const pageInfo = document.getElementById("raw-pagination-info");
    const pageControls = document.getElementById("raw-pagination-controls");
    if (!table || !countTag) return;

    const total = rawFilteredRecords.length;
    const pageSize = parseInt(rawPageSize);
    const totalPages = pageSize === -1 ? 1 : Math.max(1, Math.ceil(total / pageSize));

    if (rawCurrentPage > totalPages) rawCurrentPage = totalPages;
    if (rawCurrentPage < 1) rawCurrentPage = 1;

    const startIdx = pageSize === -1 ? 0 : (rawCurrentPage - 1) * pageSize;
    const endIdx = pageSize === -1 ? total : Math.min(startIdx + pageSize, total);
    const pageSlice = rawFilteredRecords.slice(startIdx, endIdx);

    countTag.innerText = `${total.toLocaleString()} dòng x ${rawColumns.length} cột (100% dữ liệu)`;
    if (pageInfo) {
        pageInfo.innerText = total === 0 ? "Không có dữ liệu phù hợp" : `Hiển thị dòng ${startIdx + 1} - ${endIdx} trên tổng số ${total.toLocaleString()} dòng (Trang ${rawCurrentPage}/${totalPages})`;
    }

    // Thead
    const ths = [
        `<th class="py-2.5 px-3 bg-[#1e255b] font-bold text-amber-300 border-b border-purple-500/35 text-center w-12">#</th>`,
        ...rawColumns.map(c => `<th class="py-2.5 px-3 bg-[#1e255b] font-bold text-slate-100 border-b border-purple-500/35 whitespace-nowrap">${c}</th>`)
    ].join("");

    // Tbody
    const trs = pageSlice.map((row, idx) => {
        const rowNum = startIdx + idx + 1;
        const tds = [
            `<td class="py-2 px-3 border-b border-purple-500/20 text-amber-300 font-mono text-center">${rowNum}</td>`,
            ...rawColumns.map(col => {
                const val = row[col];
                const isNull = val === null || val === "" || val === undefined;
                return `<td class="py-2 px-3 border-b border-purple-500/20 text-slate-200 whitespace-nowrap font-mono">${isNull ? '<span class="text-cyan-300 italic font-semibold">null</span>' : val}</td>`;
            })
        ].join("");
        return `<tr class="hover:bg-[#242d6d]/60 transition">${tds}</tr>`;
    }).join("");

    table.innerHTML = `<thead><tr>${ths}</tr></thead><tbody>${trs}</tbody>`;

    // Pagination controls
    if (!pageControls) return;
    if (pageSize === -1 || totalPages <= 1) {
        pageControls.innerHTML = "";
    } else {
        pageControls.innerHTML = `
            <button onclick="gotoRawPage(1)" ${rawCurrentPage === 1 ? 'disabled class="px-2.5 py-1 rounded-lg bg-[#18204d] text-pink-400/30 text-xs cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg bg-[#212b6b] hover:bg-[#2b388c] text-purple-200 text-xs transition"'} title="Trang đầu">
                <i class="fas fa-angles-left"></i>
            </button>
            <button onclick="gotoRawPage(${rawCurrentPage - 1})" ${rawCurrentPage === 1 ? 'disabled class="px-2.5 py-1 rounded-lg bg-[#18204d] text-pink-400/30 text-xs cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg bg-[#212b6b] hover:bg-[#2b388c] text-purple-200 text-xs transition"'}>
                <i class="fas fa-chevron-left"></i>
            </button>
            <span class="px-3 py-1 rounded-lg bg-[#161c47] text-white font-bold text-xs border border-purple-500/35">${rawCurrentPage} / ${totalPages}</span>
            <button onclick="gotoRawPage(${rawCurrentPage + 1})" ${rawCurrentPage === totalPages ? 'disabled class="px-2.5 py-1 rounded-lg bg-[#18204d] text-pink-400/30 text-xs cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg bg-[#212b6b] hover:bg-[#2b388c] text-purple-200 text-xs transition"'}>
                <i class="fas fa-chevron-right"></i>
            </button>
            <button onclick="gotoRawPage(${totalPages})" ${rawCurrentPage === totalPages ? 'disabled class="px-2.5 py-1 rounded-lg bg-[#18204d] text-pink-400/30 text-xs cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg bg-[#212b6b] hover:bg-[#2b388c] text-purple-200 text-xs transition"'} title="Trang cuối">
                <i class="fas fa-angles-right"></i>
            </button>
        `;
    }
}

function filterRawTable() {
    const q = (document.getElementById("raw-table-search")?.value || "").toLowerCase().trim();
    if (!q) {
        rawFilteredRecords = [...rawAllRecords];
    } else {
        rawFilteredRecords = rawAllRecords.filter(row => {
            return rawColumns.some(col => String(row[col] ?? "").toLowerCase().includes(q));
        });
    }
    rawCurrentPage = 1;
    renderRawTable();
}

function changeRawPageSize(size) {
    rawPageSize = parseInt(size);
    rawCurrentPage = 1;
    renderRawTable();
}

function gotoRawPage(p) {
    rawCurrentPage = p;
    renderRawTable();
}

// ================= BƯỚC 2: AI CHẨN ĐOÁN CHI TIẾT & ĐIỂM SỨC KHỎE =================
async function fetchDiagnosis() {
    try {
        const res = await fetch("/api/diagnose");
        const data = await res.json();
        if (data.status === "success") {
            currentDiagnosis = data.diagnosis;
            renderDiagnosis(data.diagnosis);
        }
    } catch (err) {
        console.error("Lỗi lấy chẩn đoán:", err);
    }
}

function renderDiagnosis(diag) {
    const summary = diag.summary;
    currentProposals = diag.proposals || [];

    // Health Score Circle
    const scoreVal = document.getElementById("health-score-val");
    const scoreCircle = document.getElementById("health-score-circle");
    const gradeText = document.getElementById("health-grade-text");

    if (scoreVal) scoreVal.innerText = `${summary.health_score}%`;
    if (scoreCircle) scoreCircle.setAttribute("stroke-dasharray", `${summary.health_score}, 100`);
    
    if (gradeText) {
        if (summary.health_score >= 80) {
            scoreCircle.className = "text-emerald-400";
            gradeText.innerText = "Chất Lượng Tốt";
            gradeText.className = "text-base font-extrabold text-emerald-300";
        } else if (summary.health_score >= 60) {
            scoreCircle.className = "text-amber-300";
            gradeText.innerText = "Chất Lượng Trung Bình";
            gradeText.className = "text-base font-extrabold text-amber-200";
        } else {
            scoreCircle.className = "text-pink-400";
            gradeText.innerText = "Chất Lượng Kém (Cần duyệt làm sạch)";
            gradeText.className = "text-base font-extrabold text-cyan-300";
        }
    }

    // 4 Thống kê sự cố
    const dupEl = document.getElementById("diag-dup-count");
    if (dupEl) dupEl.innerText = `${summary.duplicate_rows} dòng`;
    const nullEl = document.getElementById("diag-null-count");
    if (nullEl) nullEl.innerText = `${summary.missing_cells.toLocaleString()} ô`;
    const nullPctEl = document.getElementById("diag-null-pct");
    if (nullPctEl) nullPctEl.innerText = `${summary.missing_percentage}% tổng ô`;
    const outEl = document.getElementById("diag-outlier-count");
    if (outEl) outEl.innerText = `${summary.outlier_count} giá trị`;
    
    const textIssuesCount = currentProposals.filter(p => p.category.includes("chuỗi") || p.category.includes("kiểu")).length;
    const formatEl = document.getElementById("diag-format-count");
    if (formatEl) formatEl.innerText = `${textIssuesCount} vấn đề`;

    // Chi tiết Cột Thiếu (Bước 2)
    const missingCont = document.getElementById("diag-missing-container");
    if (missingCont) {
        if (!diag.missing_details || diag.missing_details.length === 0) {
            missingCont.innerHTML = `<div class="p-3 rounded-xl bg-emerald-950/40 text-emerald-300 font-medium"><i class="fas fa-check-circle mr-1"></i> Không có cột nào bị thiếu dữ liệu!</div>`;
        } else {
            missingCont.innerHTML = diag.missing_details.map(m => `
                <div class="diag-detail-item flex items-center justify-between p-2.5 rounded-xl transition">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-amber-400"></span>
                        <span class="font-bold text-xs diag-item-title">${m.column}</span>
                        <span class="text-[10px] px-2 py-0.5 rounded diag-item-badge">${m.type}</span>
                    </div>
                    <div class="text-right">
                        <span class="font-bold text-amber-500 text-xs">${m.count} ô thiếu</span>
                        <span class="text-[10px] diag-item-sub ml-1">(${m.percentage}%)</span>
                    </div>
                </div>
            `).join("");
        }
    }

    // Chi tiết Cột Ngoại Lai (Bước 2)
    const outlierCont = document.getElementById("diag-outlier-container");
    if (outlierCont) {
        if (!diag.outlier_details || diag.outlier_details.length === 0) {
            outlierCont.innerHTML = `<div class="p-3 rounded-xl bg-emerald-950/40 text-emerald-300 font-medium"><i class="fas fa-check-circle mr-1"></i> Không phát hiện giá trị ngoại lai vượt ngưỡng IQR!</div>`;
        } else {
            outlierCont.innerHTML = diag.outlier_details.map(o => `
                <div class="diag-detail-item flex items-center justify-between p-2.5 rounded-xl transition">
                    <div class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-pink-500"></span>
                        <span class="font-bold text-xs diag-item-title">${o.column}</span>
                        <span class="text-[10px] diag-item-sub font-mono">[${o.lower_bound} ➔ ${o.upper_bound}]</span>
                    </div>
                    <div class="text-right">
                        <span class="font-bold text-pink-500 text-xs">${o.count} ngoại lai</span>
                        <span class="text-[10px] diag-item-sub ml-1">(${o.percentage}%)</span>
                    </div>
                </div>
            `).join("");
        }
    }

    // Render danh sách đề xuất cho Bước 3
    renderProposalChecklist(currentProposals);
}

// ================= BƯỚC 3: TRẠM KIỂM DUYỆT PHÊ DUYỆT LÀM SẠCH (HITL) =================
function renderProposalChecklist(proposals) {
    const container = document.getElementById("proposals-list");
    if (!container) return;

    if (!proposals || proposals.length === 0) {
        container.innerHTML = `
            <div class="p-6 rounded-2xl bg-emerald-950/50 border border-emerald-400/40 text-emerald-200 text-center text-xs font-semibold">
                <i class="fas fa-check-circle text-base mb-1 block text-emerald-300"></i>
                Dữ liệu hoàn hảo! Không phát hiện lỗi cần làm sạch.
            </div>
        `;
        return;
    }

    container.innerHTML = proposals.map((p) => {
        let badgeColor = "bg-purple-950/70 text-purple-200 border-red-500/45";
        if (p.category.includes("Trùng lặp")) badgeColor = "bg-rose-500/25 text-purple-200 border-rose-400/40";
        else if (p.category.includes("khuyết")) badgeColor = "bg-amber-500/25 text-amber-200 border-amber-400/40";
        else if (p.category.includes("ngoại lai")) badgeColor = "bg-red-600/25 text-purple-200 border-red-500/45";
        else if (p.category.includes("chuỗi") || p.category.includes("kiểu")) badgeColor = "bg-amber-500/25 text-purple-200 border-amber-400/40";

        const optionsHtml = p.options.map(opt => `
            <option value="${opt.id}" ${opt.id === p.selected_option ? 'selected' : ''}>${opt.label}</option>
        `).join("");

        return `
            <div class="proposal-card p-4 rounded-2xl transition space-y-3" id="prop-card-${p.action_id}">
                <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div class="flex items-start gap-3">
                        <input type="checkbox" id="check-${p.action_id}" ${p.approved ? 'checked' : ''} onchange="onProposalToggle('${p.action_id}', this.checked)" class="mt-1 w-4 h-4 text-purple-600 rounded border-purple-400 focus:ring-purple-400 cursor-pointer">
                        <div>
                            <div class="flex items-center gap-2 mb-1">
                                <span class="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${badgeColor}">${p.category}</span>
                                <h4 class="font-bold text-xs prop-title">${p.target_col ? `Cột [${p.target_col}]` : 'Toàn tập dữ liệu'}</h4>
                            </div>
                            <p class="text-xs prop-desc">${p.issue_desc}</p>
                            <p class="text-xs prop-proposed font-semibold mt-0.5"><i class="fas fa-brain text-pink-400 mr-1"></i>Đề xuất DataMind AI: ${p.proposed_action}</p>
                        </div>
                    </div>
                    <div class="text-right shrink-0">
                        <span class="inline-block px-3 py-1 rounded-lg prop-impact text-[11px] font-mono font-bold shadow-sm">
                            ${p.impact_estimate}
                        </span>
                    </div>
                </div>

                <div class="pt-2 border-t prop-divider flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                    <label class="prop-label font-medium flex items-center gap-1.5">
                        <i class="fas fa-sliders text-cyan-400"></i> Phương pháp thực thi phê duyệt:
                    </label>
                    <select onchange="onProposalOptionChange('${p.action_id}', this.value)" class="prop-select px-3 py-1.5 rounded-xl border text-xs font-semibold focus:outline-none focus:ring-2 focus:ring-purple-400">
                        ${optionsHtml}
                    </select>
                </div>
            </div>
        `;
    }).join("");
}

function onProposalToggle(actionId, checked) {
    const item = currentProposals.find(p => p.action_id === actionId);
    if (item) item.approved = checked;
}

function onProposalOptionChange(actionId, newOption) {
    const item = currentProposals.find(p => p.action_id === actionId);
    if (item) item.selected_option = newOption;
}

function toggleAllProposals(state) {
    currentProposals.forEach(p => {
        p.approved = state;
        const cb = document.getElementById(`check-${p.action_id}`);
        if (cb) cb.checked = state;
    });
}

// ================= BƯỚC 4: THỰC THI & ĐỐI SOÁT SAU LÀM SẠCH =================
async function executeApprovedCleaning() {
    const btn = document.getElementById("btn-approve-clean");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-1"></i> Đang áp dụng các hành động đã duyệt...`;
    }

    try {
        const payload = { actions: currentProposals };
        const res = await fetch("/api/clean/approve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok && data.status === "success") {
            hasCleanedData = true;
            document.getElementById("step-btn-2").classList.add("completed");
            document.getElementById("step-btn-3").classList.add("completed");
            document.getElementById("step-btn-4").classList.add("completed");
            showToast("Đã duyệt và làm sạch dữ liệu thành công!", "success");

            // Nạp toàn bộ dữ liệu sạch (100% dòng)
            cleanColumns = data.columns || [];
            cleanAllRecords = data.all_data || data.preview || [];
            cleanFilteredRecords = [...cleanAllRecords];
            cleanCurrentPage = 1;

            // Render so sánh trước vs sau, nhật ký kiểm toán và bảng sạch
            renderCleaningComparison(data.comparison, cleanColumns);
            renderCleanedTable();

            // Chuyển sang Bước 4 (Đối soát sạch)
            switchTab(4);
        } else {
            showToast(data.detail || "Lỗi khi áp dụng làm sạch", "error");
        }
    } catch (err) {
        showToast("Lỗi: " + err.message, "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-circle-check text-base"></i> Phê Duyệt & Thực Thi Làm Sạch Ngay`;
        }
    }
}

function renderCleaningComparison(comp, columns) {
    const container = document.getElementById("cleaning-result-container");
    if (container) container.classList.remove("hidden");

    const before = comp.before;
    const after = comp.after;

    const cardsContainer = document.getElementById("before-after-cards");
    if (cardsContainer) {
        cardsContainer.innerHTML = `
            <div class="before-after-card p-4 rounded-2xl shadow-md transition">
                <div class="text-[11px] card-meta-label font-semibold mb-1">Số Dòng Dữ Liệu</div>
                <div class="text-xl font-black card-meta-val">${after.rows.toLocaleString()}</div>
                <div class="text-[11px] card-meta-sub mt-0.5">Trước: ${before.rows.toLocaleString()} dòng</div>
            </div>
            <div class="before-after-card p-4 rounded-2xl shadow-md transition">
                <div class="text-[11px] card-meta-label font-semibold mb-1">Trùng Lặp Đã Xóa</div>
                <div class="text-xl font-black text-emerald-500">${before.duplicates} &rarr; ${after.duplicates}</div>
                <div class="text-[11px] text-emerald-600 font-bold mt-0.5"><i class="fas fa-check mr-1"></i>Sạch 100%</div>
            </div>
            <div class="before-after-card p-4 rounded-2xl shadow-md transition">
                <div class="text-[11px] card-meta-label font-semibold mb-1">Ô Khuyết Đã Xử Lý</div>
                <div class="text-xl font-black text-emerald-500">${before.null_cells} &rarr; ${after.null_cells}</div>
                <div class="text-[11px] text-emerald-600 font-bold mt-0.5"><i class="fas fa-check mr-1"></i>Đã chuẩn hóa hoàn toàn</div>
            </div>
            <div class="before-after-card p-4 rounded-2xl shadow-md transition">
                <div class="text-[11px] card-meta-label font-semibold mb-1">Điểm Sức Khỏe Mới</div>
                <div class="text-xl font-black text-emerald-500">${after.health_score}/100</div>
                <div class="text-[11px] text-cyan-600 font-bold mt-0.5">+${Math.round((after.health_score - before.health_score) * 10) / 10}đ sau làm sạch</div>
            </div>
        `;
    }

    // Render Nhật Ký Kiểm Toán Audit Trail
    const auditCont = document.getElementById("audit-trail-container");
    if (auditCont && comp.audit_trail) {
        if (comp.audit_trail.length === 0) {
            auditCont.innerHTML = `<div class="p-3 text-slate-400">Không có thay đổi nào cần thực hiện.</div>`;
        } else {
            auditCont.innerHTML = comp.audit_trail.map(item => `
                <div class="audit-item flex items-center justify-between p-2 rounded-xl transition">
                    <div class="flex items-center gap-2">
                        <i class="fas fa-check-circle text-emerald-500"></i>
                        <span class="font-bold text-xs audit-action">${item.action}</span>
                        <span class="text-xs audit-details">${item.details}</span>
                    </div>
                    <span class="text-[10px] font-mono px-2 py-0.5 rounded audit-tag">${item.rows_affected} bản ghi</span>
                </div>
            `).join("");
        }
    }
}

// Render bảng dữ liệu sạch với phân trang và tìm kiếm (Bước 4)
function renderCleanedTable() {
    const table = document.getElementById("cleaned-preview-table");
    const countTag = document.getElementById("clean-count-tag");
    const pageInfo = document.getElementById("clean-pagination-info");
    const pageControls = document.getElementById("clean-pagination-controls");
    if (!table) return;

    const total = cleanFilteredRecords.length;
    const pageSize = parseInt(cleanPageSize);
    const totalPages = pageSize === -1 ? 1 : Math.max(1, Math.ceil(total / pageSize));

    if (cleanCurrentPage > totalPages) cleanCurrentPage = totalPages;
    if (cleanCurrentPage < 1) cleanCurrentPage = 1;

    const startIdx = pageSize === -1 ? 0 : (cleanCurrentPage - 1) * pageSize;
    const endIdx = pageSize === -1 ? total : Math.min(startIdx + pageSize, total);
    const pageSlice = cleanFilteredRecords.slice(startIdx, endIdx);

    if (countTag) {
        countTag.innerText = `${total.toLocaleString()} dòng x ${cleanColumns.length} cột (100% dữ liệu sạch)`;
    }
    if (pageInfo) {
        pageInfo.innerText = total === 0 ? "Không có dữ liệu phù hợp" : `Hiển thị dòng ${startIdx + 1} - ${endIdx} trên tổng số ${total.toLocaleString()} dòng (Trang ${cleanCurrentPage}/${totalPages})`;
    }

    const ths = [
        `<th class="py-2.5 px-3 bg-[#1e255b] font-bold text-emerald-300 border-b border-purple-500/35 text-center w-12">#</th>`,
        ...cleanColumns.map(c => `<th class="py-2.5 px-3 bg-[#1e255b] font-bold text-slate-100 border-b border-purple-500/35 whitespace-nowrap">${c}</th>`)
    ].join("");

    const trs = pageSlice.map((row, idx) => {
        const rowNum = startIdx + idx + 1;
        const tds = [
            `<td class="py-2 px-3 border-b border-purple-500/20 text-emerald-300 font-mono text-center">${rowNum}</td>`,
            ...cleanColumns.map(col => {
                const val = row[col];
                return `<td class="py-2 px-3 border-b border-purple-500/20 text-slate-200 whitespace-nowrap font-mono">${val !== null ? val : ""}</td>`;
            })
        ].join("");
        return `<tr class="hover:bg-[#242d6d]/60 transition">${tds}</tr>`;
    }).join("");

    table.innerHTML = `<thead><tr>${ths}</tr></thead><tbody>${trs}</tbody>`;

    if (!pageControls) return;
    if (pageSize === -1 || totalPages <= 1) {
        pageControls.innerHTML = "";
    } else {
        pageControls.innerHTML = `
            <button onclick="gotoCleanPage(1)" ${cleanCurrentPage === 1 ? 'disabled class="px-2.5 py-1 rounded-lg bg-[#18204d] text-pink-400/30 text-xs cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg bg-[#212b6b] hover:bg-[#2b388c] text-purple-200 text-xs transition"'} title="Trang đầu">
                <i class="fas fa-angles-left"></i>
            </button>
            <button onclick="gotoCleanPage(${cleanCurrentPage - 1})" ${cleanCurrentPage === 1 ? 'disabled class="px-2.5 py-1 rounded-lg bg-[#18204d] text-pink-400/30 text-xs cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg bg-[#212b6b] hover:bg-[#2b388c] text-purple-200 text-xs transition"'}>
                <i class="fas fa-chevron-left"></i>
            </button>
            <span class="px-3 py-1 rounded-lg bg-[#161c47] text-white font-bold text-xs border border-purple-500/35">${cleanCurrentPage} / ${totalPages}</span>
            <button onclick="gotoCleanPage(${cleanCurrentPage + 1})" ${cleanCurrentPage === totalPages ? 'disabled class="px-2.5 py-1 rounded-lg bg-[#18204d] text-pink-400/30 text-xs cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg bg-[#212b6b] hover:bg-[#2b388c] text-purple-200 text-xs transition"'}>
                <i class="fas fa-chevron-right"></i>
            </button>
            <button onclick="gotoCleanPage(${totalPages})" ${cleanCurrentPage === totalPages ? 'disabled class="px-2.5 py-1 rounded-lg bg-[#18204d] text-pink-400/30 text-xs cursor-not-allowed"' : 'class="px-2.5 py-1 rounded-lg bg-[#212b6b] hover:bg-[#2b388c] text-purple-200 text-xs transition"'} title="Trang cuối">
                <i class="fas fa-angles-right"></i>
            </button>
        `;
    }
}

function filterCleanTable() {
    const q = (document.getElementById("clean-table-search")?.value || "").toLowerCase().trim();
    if (!q) {
        cleanFilteredRecords = [...cleanAllRecords];
    } else {
        cleanFilteredRecords = cleanAllRecords.filter(row => {
            return cleanColumns.some(col => String(row[col] ?? "").toLowerCase().includes(q));
        });
    }
    cleanCurrentPage = 1;
    renderCleanedTable();
}

function changeCleanPageSize(size) {
    cleanPageSize = parseInt(size);
    cleanCurrentPage = 1;
    renderCleanedTable();
}

function gotoCleanPage(p) {
    cleanCurrentPage = p;
    renderCleanedTable();
}

// ================= BƯỚC 5: KHÁM PHÁ THỐNG KÊ & TRỢ LÝ AI EDA =================
async function runDeepAnalysis() {
    const btn = document.getElementById("btn-re-analyze");
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-1"></i> Đang phân tích...`;
    }

    try {
        const res = await fetch("/api/analyze", { method: "POST" });
        const data = await res.json();

        if (res.ok && data.status === "success") {
            const btn5 = document.getElementById("step-btn-5");
            if (btn5) btn5.classList.add("completed");
            renderKpiCards(data.kpi_cards);
            renderCharts(data.charts);
        } else {
            showToast(data.detail || "Không thể thực hiện phân tích", "error");
        }
    } catch (err) {
        console.error("Lỗi phân tích sâu:", err);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-rotate text-amber-300"></i> Phân Tích Lại`;
        }
    }
}

function renderKpiCards(kpis) {
    const container = document.getElementById("kpi-cards-container");
    if (!container || !kpis) return;

    // Growth badges mẫu tương tự bảng điều khiển tham chiếu Screen ③
    const growthTags = ["+12.3%", "+8.9%", "+4.5%", "92.1%"];

    container.innerHTML = kpis.map((k, idx) => {
        const growth = growthTags[idx % growthTags.length];
        const isCyan = idx % 2 === 0;
        const iconBg = isCyan 
            ? "bg-gradient-to-tr from-cyan-500/25 to-sky-500/25 text-cyan-300 border-cyan-400/35"
            : "bg-gradient-to-tr from-pink-500/25 to-rose-500/25 text-pink-300 border-pink-400/35";
        const badgeColor = isCyan
            ? "bg-cyan-500/20 text-cyan-300 border-cyan-400/35"
            : "bg-pink-500/20 text-pink-300 border-pink-400/35";

        return `
        <div class="galaxy-card rounded-2xl p-5 flex flex-col justify-between border border-cyan-500/20 shadow-md">
            <div class="flex items-center justify-between mb-2">
                <div class="w-10 h-10 rounded-xl ${iconBg} border flex items-center justify-center text-lg shrink-0 shadow-md">
                    <i class="fas ${k.icon}"></i>
                </div>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${badgeColor} flex items-center gap-1">
                    <i class="fas fa-arrow-trend-up text-[9px]"></i> ${growth}
                </span>
            </div>
            <div>
                <div class="text-xs font-semibold kpi-title">${k.title}</div>
                <div class="text-2xl font-black mt-0.5 tracking-tight kpi-val">${k.value}</div>
                <div class="text-[11px] mt-1 kpi-sub flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 rounded-full ${isCyan ? 'bg-cyan-400' : 'bg-pink-400'}"></span>
                    <span>${k.sub}</span>
                </div>
            </div>
        </div>
        `;
    }).join("");
}

function renderCharts(charts) {
    window.lastChartsData = charts;
    const isLight = (currentTheme === "light");

    const chartMap = {
        "correlation_heatmap": "chart-tab3-corr",
        "distribution": "chart-tab3-dist",
        "categorical_breakdown": "chart-tab3-cat",
        "scatter_relation": "chart-tab3-scatter"
    };

    Object.entries(chartMap).forEach(([chartKey, elId]) => {
        const el = document.getElementById(elId);
        if (!el) return;

        if (charts[chartKey]) {
            const data = charts[chartKey].data;
            const layout = charts[chartKey].layout;
            layout.autosize = true;
            layout.height = 300;
            layout.margin = { l: 30, r: 20, t: 30, b: 30 };
            
            // TÙY BIẾN THEO CHẾ ĐỘ SÁNG / TỐI
            layout.paper_bgcolor = "rgba(0,0,0,0)";
            layout.plot_bgcolor = isLight ? "rgba(241, 245, 249, 0.75)" : "rgba(22, 28, 70, 0.45)";
            layout.font = { 
                color: isLight ? "#0f172a" : "#e2e8f0", 
                family: "Plus Jakarta Sans, sans-serif", 
                size: 11 
            };
            
            if (layout.xaxis) {
                layout.xaxis.gridcolor = isLight ? "rgba(203, 213, 225, 0.6)" : "rgba(192, 132, 252, 0.18)";
                layout.xaxis.zerolinecolor = isLight ? "rgba(148, 163, 184, 0.6)" : "rgba(192, 132, 252, 0.35)";
            }
            if (layout.yaxis) {
                layout.yaxis.gridcolor = isLight ? "rgba(203, 213, 225, 0.6)" : "rgba(192, 132, 252, 0.18)";
                layout.yaxis.zerolinecolor = isLight ? "rgba(148, 163, 184, 0.6)" : "rgba(192, 132, 252, 0.35)";
            }

            Plotly.newPlot(el, data, layout, { responsive: true, displayModeBar: false });
        } else {
            el.innerHTML = `<div class="h-full flex items-center justify-center text-xs text-purple-200/70 italic">Không đủ dữ liệu cho biểu đồ này</div>`;
        }
    });
}

// ================= AI CHAT COCKPIT =================
async function handleChatSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const msg = input.value.trim();
    if (!msg) return;

    appendChatMessage("user", msg);
    input.value = "";

    const btn = document.getElementById("btn-chat-send");
    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i>`;

    try {
        const res = await fetch("/api/agent/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg })
        });
        const data = await res.json();
        appendChatMessage("agent", data.reply || "Xin lỗi, không có phản hồi.");
    } catch (err) {
        appendChatMessage("agent", "Lỗi kết nối: " + err.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>Gửi</span> <i class="fas fa-paper-plane text-[10px]"></i>`;
    }
}

function sendQuickPrompt(promptText) {
    const input = document.getElementById("chat-input");
    if (input) {
        input.value = promptText;
        input.focus();
    }
}

function appendChatMessage(sender, text) {
    const chatContainer = document.getElementById("chat-messages");
    if (!chatContainer) return;

    const formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong class="text-amber-300 font-bold">$1</strong>').replace(/\n/g, '<br>');

    const bubble = document.createElement("div");
    bubble.className = "flex items-start gap-3 " + (sender === "user" ? "flex-row-reverse" : "");

    if (sender === "user") {
        bubble.innerHTML = `
            <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-violet-600 via-purple-600 to-cyan-400 text-white flex items-center justify-center text-xs shrink-0 mt-0.5 shadow-sm">
                <i class="fas fa-user"></i>
            </div>
            <div class="bg-gradient-to-r from-violet-600 via-purple-600 to-cyan-500 text-white p-3.5 rounded-2xl rounded-tr-none text-xs shadow-lg shadow-purple-950/40 max-w-xl leading-relaxed font-medium">
                ${formatted}
            </div>
        `;
    } else {
        bubble.innerHTML = `
            <div class="w-7 h-7 rounded-lg bg-gradient-to-tr from-purple-600 to-cyan-400 text-white flex items-center justify-center text-xs shrink-0 mt-0.5 shadow-sm">
                <i class="fas fa-robot"></i>
            </div>
            <div class="chat-bot-bubble p-3.5 rounded-2xl rounded-tl-none border text-xs shadow-md max-w-xl leading-relaxed">
                ${formatted}
            </div>
        `;
    }

    chatContainer.appendChild(bubble);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ================= BƯỚC 6: BÁO CÁO HTML TRỰC TIẾP & XUẤT BẢN =================
function reloadReport() {
    const iframe = document.getElementById("report-iframe");
    const spinner = document.getElementById("iframe-spinner");
    if (!iframe) return;

    if (spinner) spinner.classList.remove("hidden");
    iframe.src = "/api/report/html?t=" + new Date().getTime();

    iframe.onload = () => {
        if (spinner) spinner.classList.add("hidden");
        const btn6 = document.getElementById("step-btn-6");
        if (btn6) btn6.classList.add("completed");
    };
}

function printReportIframe() {
    const iframe = document.getElementById("report-iframe");
    if (iframe && iframe.contentWindow) {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
    }
}

// ================= MODAL API KEY =================
function openApiKeyModal() {
    document.getElementById("apikey-modal").classList.remove("hidden");
}

function closeApiKeyModal() {
    document.getElementById("apikey-modal").classList.add("hidden");
}

async function saveApiKey() {
    const input = document.getElementById("modal-api-key-input");
    const key = input.value.trim();

    try {
        const res = await fetch("/api/settings/apikey", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ api_key: key })
        });
        const data = await res.json();
        if (res.ok) {
            showToast("Đã lưu API Key thành công!", "success");
            closeApiKeyModal();
            updateApiKeyBadge(data.has_api_key);
        }
    } catch (err) {
        showToast("Lỗi lưu API Key: " + err.message, "error");
    }
}

function updateApiKeyBadge(hasKey) {
    const badge = document.getElementById("api-status-text");
    if (!badge) return;
    if (hasKey) {
        badge.innerHTML = `<span class="text-amber-300 font-bold"><i class="fas fa-check-circle mr-1"></i>Gemini Bật</span>`;
    } else {
        badge.innerText = "Cài đặt Gemini";
    }
}

// ================= UTILITIES =================
function showUploadSpinner(show) {
    const spinner = document.getElementById("upload-spinner");
    if (spinner) {
        if (show) spinner.classList.remove("hidden");
        else spinner.classList.add("hidden");
    }
}

function showToast(message, type = "info") {
    const toast = document.getElementById("toast");
    const toastMsg = document.getElementById("toast-msg");
    const toastIcon = document.getElementById("toast-icon");
    if (!toast || !toastMsg) return;

    toastMsg.innerText = message;
    const isLight = (document.documentElement.getAttribute("data-theme") === "light" || document.documentElement.classList.contains("light-mode") || currentTheme === "light");

    if (isLight) {
        toast.style.setProperty("background-color", "#ffffff", "important");
        toast.style.setProperty("color", "#0f172a", "important");
        toast.style.setProperty("border", "1px solid #cbd5e1", "important");
        toast.style.setProperty("box-shadow", "0 15px 35px rgba(79, 70, 229, 0.20)", "important");
        toastMsg.style.setProperty("color", "#0f172a", "important");
    } else {
        toast.style.setProperty("background-color", "#0f153a", "important");
        toast.style.setProperty("color", "#ffffff", "important");
        toast.style.setProperty("border", "1px solid rgba(56, 189, 248, 0.50)", "important");
        toast.style.setProperty("box-shadow", "0 10px 35px rgba(0, 0, 0, 0.75), 0 0 20px rgba(56, 189, 248, 0.35)", "important");
        toastMsg.style.setProperty("color", "#ffffff", "important");
    }

    if (type === "success") {
        toastIcon.className = `fas fa-circle-check ${isLight ? 'text-emerald-600' : 'text-emerald-400'} text-base shrink-0`;
    } else if (type === "error") {
        toastIcon.className = `fas fa-circle-exclamation ${isLight ? 'text-rose-600' : 'text-pink-400'} text-base shrink-0`;
    } else {
        toastIcon.className = `fas fa-circle-info ${isLight ? 'text-indigo-600' : 'text-cyan-300'} text-base shrink-0`;
    }

    toast.classList.remove("hidden");
    if (window.toastTimer) clearTimeout(window.toastTimer);
    window.toastTimer = setTimeout(() => {
        toast.classList.add("hidden");
    }, 3500);
}

function checkInitialState() {
    // Check if server already has dataset loaded
    fetch("/api/diagnose").then(r => r.json()).then(data => {
        if (data.status === "success" && data.diagnosis) {
            handleDataLoaded({
                dataset_name: data.dataset_name,
                diagnosis: data.diagnosis,
                columns: [],
                all_data: [],
                preview: [],
                rows: data.diagnosis.summary.total_rows,
                cols: data.diagnosis.summary.total_cols
            });
        }
    }).catch(() => {});
}
