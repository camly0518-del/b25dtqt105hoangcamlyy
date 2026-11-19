"""
HTML Report Generator
Generates self-contained, publication-grade interactive HTML reports with Galaxy Cosmic styling
"""
import json
from datetime import datetime
from typing import Dict, Any

class ReportGenerator:
    def __init__(self):
        pass

    def generate_html_report(self, dataset_name: str, df_cleaned, eda_data: Dict[str, Any], cleaning_comparison: Dict[str, Any], insights: Dict[str, Any]) -> str:
        """Tạo file báo cáo HTML hoàn chỉnh, độc lập và mang phong cách Galaxy Cosmic sang trọng"""
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        before = cleaning_comparison.get("before", {})
        after = cleaning_comparison.get("after", {})
        audit = cleaning_comparison.get("audit_trail", [])
        charts = eda_data.get("charts", {})
        kpis = eda_data.get("kpi_cards", [])
        num_stats = eda_data.get("numeric_stats", [])
        correlations = eda_data.get("top_correlations", [])

        # Chuyển đổi dữ liệu biểu đồ sang chuỗi JSON an toàn
        charts_json = json.dumps(charts, ensure_ascii=False)

        # Xây dựng các hàng của bảng nhật ký làm sạch đã duyệt (Galaxy Dark Theme)
        audit_rows_html = ""
        for idx, item in enumerate(audit, 1):
            audit_rows_html += f"""
            <tr class="border-b border-purple-500/15 hover:bg-purple-950/30 transition">
                <td class="py-2.5 px-4 text-xs font-semibold text-purple-300/70">{idx}</td>
                <td class="py-2.5 px-4 text-sm font-medium text-white">
                    <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 mr-2">
                        <i class="fas fa-check mr-1 text-emerald-400"></i> Đã duyệt
                    </span>
                    {item.get('action', '')}
                </td>
                <td class="py-2.5 px-4 text-sm text-slate-300">{item.get('details', '')}</td>
                <td class="py-2.5 px-4 text-xs font-mono font-semibold text-cyan-400 text-right">{item.get('rows_affected', 0):,} bản ghi/ô</td>
            </tr>
            """

        # Xây dựng các thẻ phát hiện chính từ AI
        findings_html = ""
        for idx, f in enumerate(insights.get("key_findings", []), 1):
            findings_html += f"""
            <div class="bg-[#12142d]/85 rounded-2xl p-5 border border-purple-500/20 shadow-md hover:border-purple-400/40 transition">
                <div class="flex items-center gap-3 mb-2.5">
                    <span class="w-7 h-7 rounded-xl bg-gradient-to-tr from-purple-600 to-pink-500 text-white flex items-center justify-center text-xs font-bold shadow-md shadow-purple-500/30">{idx}</span>
                    <h4 class="font-bold text-white text-base">{f.get('title', '')}</h4>
                </div>
                <p class="text-slate-300 text-sm mb-3 leading-relaxed">{f.get('description', '')}</p>
                <div class="bg-purple-950/50 rounded-xl px-3.5 py-2 text-xs text-purple-200 border border-purple-500/20 flex items-start gap-2">
                    <i class="fas fa-lightbulb text-amber-400 mt-0.5"></i>
                    <span><strong class="text-white">Tác động chiến lược:</strong> {f.get('impact', '')}</span>
                </div>
            </div>
            """

        # Xây dựng các thẻ rủi ro & bất thường
        risks_html = ""
        for r in insights.get("anomalies_and_risks", []):
            sev = r.get("severity", "Trung bình")
            badge_color = "bg-rose-500/20 text-cyan-300 border-rose-500/30" if sev == "Cao" else "bg-amber-500/20 text-amber-300 border-amber-500/30"
            risks_html += f"""
            <div class="bg-[#12142d]/85 rounded-2xl p-4 border border-purple-500/20 shadow-md flex items-start gap-3">
                <div class="w-8 h-8 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-400 flex items-center justify-center shrink-0">
                    <i class="fas fa-triangle-exclamation"></i>
                </div>
                <div class="flex-1">
                    <div class="flex items-center justify-between gap-2 mb-1">
                        <h5 class="font-semibold text-white text-sm">{r.get('risk', '')}</h5>
                        <span class="px-2 py-0.5 rounded-full text-xs font-semibold border {badge_color}">{sev}</span>
                    </div>
                    <p class="text-xs text-slate-300">{r.get('evidence', '')}</p>
                </div>
            </div>
            """

        # Khuyến nghị 3 giai đoạn (Galaxy Style)
        recs = insights.get("recommendations", {})
        qw_items = "".join([f"<li class='flex items-start gap-2 text-xs text-slate-200 mb-2'><i class='fas fa-circle-check text-emerald-400 mt-0.5'></i><span>{it}</span></li>" for it in recs.get("quick_wins", [])])
        mt_items = "".join([f"<li class='flex items-start gap-2 text-xs text-slate-200 mb-2'><i class='fas fa-circle-arrow-right text-cyan-400 mt-0.5'></i><span>{it}</span></li>" for it in recs.get("medium_term", [])])
        lt_items = "".join([f"<li class='flex items-start gap-2 text-xs text-slate-200 mb-2'><i class='fas fa-rocket text-purple-400 mt-0.5'></i><span>{it}</span></li>" for it in recs.get("long_term", [])])

        # Bảng thống kê mô tả
        num_stats_rows = ""
        for s in num_stats:
            num_stats_rows += f"""
            <tr class="border-b border-purple-500/15 hover:bg-purple-950/30">
                <td class="py-2 px-3 text-xs font-medium text-white">{s['column']}</td>
                <td class="py-2 px-3 text-xs text-slate-300 text-right">{s['mean']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-slate-300 text-right">{s['median']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-slate-300 text-right">{s['std']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-slate-300 text-right">{s['min']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-slate-300 text-right">{s['max']:,.2f}</td>
                <td class="py-2 px-3 text-xs text-slate-300 text-right">{s['skew']:,.2f}</td>
            </tr>
            """

        # Mẫu HTML Báo cáo Độc lập (Phong cách Báo Cáo Kinh Doanh Cyber Cyan & Neon Pink)
        html_content = f"""<!DOCTYPE html>
<html lang="vi" class="bg-[#080d1a]">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo Cáo Kinh Doanh DataMind AI - {dataset_name}</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome 6 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- Plotly.js -->
    <script src="https://cdn.plot.ly/plotly-2.30.0.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');
        body {{
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #080d1a;
            background-image: 
                radial-gradient(circle at 10% 10%, rgba(6, 182, 212, 0.25) 0%, transparent 45%),
                radial-gradient(circle at 90% 15%, rgba(236, 72, 153, 0.22) 0%, transparent 45%),
                radial-gradient(circle at 50% 80%, rgba(14, 165, 233, 0.18) 0%, transparent 55%),
                linear-gradient(180deg, #090f24 0%, #050814 100%);
            background-attachment: fixed;
            color: #f1f5f9;
        }}
        .galaxy-card {{
            background: rgba(13, 20, 42, 0.85);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(6, 182, 212, 0.30);
            box-shadow: 0 10px 35px 0 rgba(0, 0, 0, 0.65), 0 0 25px rgba(236, 72, 153, 0.15);
        }}
        .galaxy-title {{
            background: linear-gradient(135deg, #ffffff 0%, #38bdf8 35%, #ec4899 75%, #f43f5e 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        @media print {{
            .no-print {{
                display: none !important;
            }}
            body {{
                background: #ffffff !important;
                color: #0f172a !important;
            }}
            .galaxy-card {{
                background: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                box-shadow: none !important;
                color: #0f172a !important;
            }}
            .text-white {{
                color: #0f172a !important;
            }}
            .text-slate-300, .text-purple-200, .text-slate-200, .text-purple-200 {{
                color: #334155 !important;
            }}
            .page-break {{
                page-break-before: always;
            }}
        }}
    </style>
</head>
<body class="p-4 sm:p-8 md:p-12">
    <div class="max-w-6xl mx-auto space-y-8">
        
        <!-- TOP TOOLBAR (CHỈ HIỂN THỊ KHI XEM, ẨN KHI IN) -->
        <div class="no-print flex flex-wrap items-center justify-between gap-4 galaxy-card p-4 rounded-2xl">
            <div class="flex items-center gap-2">
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/20 text-cyan-200 border border-cyan-400/35">
                    <i class="fas fa-check-double mr-1.5 text-pink-400"></i> Báo Cáo Kinh Doanh Chuẩn Doanh Nghiệp
                </span>
                <span class="text-xs text-cyan-100/80">Công Ty Cổ Phần DataMind Intelligence • Nền Tảng Phân Tích Thông Minh</span>
            </div>
            <div class="flex items-center gap-2">
                <button onclick="window.print()" class="px-4 py-2 bg-slate-900/80 hover:bg-slate-800 text-cyan-200 border border-cyan-400/40 rounded-xl text-xs font-semibold flex items-center gap-2 transition shadow-sm">
                    <i class="fas fa-print text-pink-400"></i> In / Xuất PDF
                </button>
                <button onclick="downloadHtmlFile()" class="px-4 py-2 bg-gradient-to-r from-cyan-500 via-sky-500 to-pink-500 hover:from-cyan-400 hover:to-pink-400 text-white rounded-xl text-xs font-bold flex items-center gap-2 transition shadow-lg shadow-pink-900/30">
                    <i class="fas fa-download"></i> Tải file HTML Độc Lập
                </button>
            </div>
        </div>

        <!-- HEADER BANNER BÁO CÁO KINH DOANH -->
        <div class="bg-gradient-to-r from-[#0c2a4d] via-[#103a63] to-[#4a1532] text-white rounded-3xl p-8 sm:p-10 shadow-2xl relative overflow-hidden border border-cyan-500/35">
            <div class="absolute -right-10 -bottom-10 w-72 h-72 bg-pink-500/20 rounded-full blur-3xl pointer-events-none"></div>
            <div class="absolute -left-10 -top-10 w-72 h-72 bg-cyan-500/20 rounded-full blur-3xl pointer-events-none"></div>
            
            <div class="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div>
                    <div class="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-white/15 text-cyan-100 text-xs font-bold mb-3 border border-white/25">
                        <i class="fas fa-brain text-pink-400"></i> CÔNG TY CỔ PHẦN DATAMIND INTELLIGENCE
                    </div>
                    <h1 class="text-2xl sm:text-4xl font-extrabold tracking-tight mb-2 uppercase galaxy-title">BÁO CÁO KINH DOANH & PHÂN TÍCH DỮ LIỆU</h1>
                    <p class="text-cyan-100/90 text-sm max-w-2xl">
                        Tập dữ liệu: <strong class="text-white">{dataset_name}</strong> | Quy trình: Chẩn đoán &rarr; Người dùng duyệt &rarr; Làm sạch chuẩn &rarr; AI Khám phá EDA
                    </p>
                </div>
                <div class="flex flex-col sm:flex-row md:flex-col items-start md:items-end gap-3">
                    <div class="bg-white/15 backdrop-blur-md px-5 py-3 rounded-2xl border border-white/20 text-left md:text-right shadow-lg">
                        <div class="text-[10px] uppercase tracking-wider text-cyan-200">Điểm Chất Lượng Dữ Liệu</div>
                        <div class="text-3xl font-black text-pink-400 flex items-center md:justify-end gap-1.5">
                            {after.get('health_score', 0)}<span class="text-base text-cyan-200">/100</span>
                        </div>
                        <div class="text-[10px] text-cyan-100/80">Ban đầu: {before.get('health_score', 0)}/100 (Đã kiểm định)</div>
                    </div>
                    <div class="text-xs text-cyan-200/80">
                        <i class="far fa-clock mr-1"></i> {now_str}
                    </div>
                </div>
            </div>
        </div>

        <!-- 1. TỔNG QUAN ĐIỀU HÀNH (EXECUTIVE SUMMARY) -->
        <section class="galaxy-card rounded-3xl p-6 sm:p-8">
            <div class="flex items-center gap-3 mb-4 pb-3 border-b border-purple-500/20">
                <div class="w-9 h-9 rounded-xl bg-purple-600/25 text-cyan-300 border border-purple-500/35 flex items-center justify-center font-bold text-lg">
                    <i class="fas fa-compass"></i>
                </div>
                <div>
                    <h2 class="text-lg font-bold text-white">1. Bản Tóm Tắt Điều Hành (Executive Summary)</h2>
                    <p class="text-xs text-purple-200/80">Bức tranh toàn cảnh về tập dữ liệu và kết luận tổng thể từ AI Agent</p>
                </div>
            </div>
            <div class="text-slate-200 text-sm sm:text-base leading-relaxed space-y-3">
                <p>{insights.get('executive_summary', '')}</p>
            </div>
        </section>

        <!-- 2. CHỨNG NHẬN & NHẬT KÝ LÀM SẠCH (DATA AUDIT & APPROVAL LOG) -->
        <section class="galaxy-card rounded-3xl p-6 sm:p-8">
            <div class="flex items-center justify-between gap-4 mb-4 pb-3 border-b border-purple-500/15">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-lg">
                        <i class="fas fa-certificate"></i>
                    </div>
                    <div>
                        <h2 class="text-lg font-bold text-white">2. Chứng Nhận Xử Lý & Làm Sạch Dữ Liệu (Human-in-the-Loop)</h2>
                        <p class="text-xs text-slate-400">Mọi hành động đều được AI lập đề xuất và người dùng trực tiếp phê duyệt</p>
                    </div>
                </div>
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    <i class="fas fa-shield-halved mr-1"></i> Chuẩn kiểm định 100%
                </span>
            </div>

            <!-- Thẻ So Sánh Trước vs Sau Galaxy -->
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div class="bg-[#12142d]/80 rounded-2xl p-4 border border-purple-500/20">
                    <div class="text-xs text-purple-300/80 mb-1">Số Dòng Dữ Liệu</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-xl font-bold text-white">{after.get('rows', 0):,}</span>
                        <span class="text-xs text-slate-500 line-through">({before.get('rows', 0):,})</span>
                    </div>
                    <div class="text-[11px] text-emerald-400 font-medium mt-1">Đã tối ưu cấu trúc</div>
                </div>
                <div class="bg-[#12142d]/80 rounded-2xl p-4 border border-purple-500/20">
                    <div class="text-xs text-purple-300/80 mb-1">Dòng Trùng Lặp</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-xl font-bold text-emerald-400">{after.get('duplicates', 0)}</span>
                        <span class="text-xs text-rose-400 line-through">({before.get('duplicates', 0)})</span>
                    </div>
                    <div class="text-[11px] text-emerald-400 font-medium mt-1">Đã loại bỏ hoàn toàn</div>
                </div>
                <div class="bg-[#12142d]/80 rounded-2xl p-4 border border-purple-500/20">
                    <div class="text-xs text-purple-300/80 mb-1">Ô Khuyết Thiếu (Null)</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-xl font-bold text-emerald-400">{after.get('null_cells', 0)}</span>
                        <span class="text-xs text-rose-400 line-through">({before.get('null_cells', 0):,})</span>
                    </div>
                    <div class="text-[11px] text-emerald-400 font-medium mt-1">Đã điền đại diện</div>
                </div>
                <div class="bg-[#12142d]/80 rounded-2xl p-4 border border-purple-500/20">
                    <div class="text-xs text-purple-300/80 mb-1">Sức Khỏe Dữ Liệu</div>
                    <div class="flex items-baseline gap-2">
                        <span class="text-xl font-bold text-emerald-400">+{round(after.get('health_score', 0) - before.get('health_score', 0), 1)}đ</span>
                        <span class="text-xs text-slate-400">(&rarr; {after.get('health_score', 0)}%)</span>
                    </div>
                    <div class="text-[11px] text-cyan-300 font-medium mt-1">Cải thiện vượt bậc</div>
                </div>
            </div>

            <!-- Bảng Nhật Ký Phê Duyệt Galaxy -->
            <div class="overflow-x-auto rounded-xl border border-purple-500/20 bg-[#0b0d26]/80">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-[#131633] border-b border-purple-500/20 text-xs font-semibold text-purple-200 uppercase">
                            <th class="py-3 px-4 w-12">#</th>
                            <th class="py-3 px-4">Hành Động Đã Duyệt</th>
                            <th class="py-3 px-4">Chi Tiết Biến Đổi & Thuật Toán</th>
                            <th class="py-3 px-4 text-right">Phạm Vi Tác Động</th>
                        </tr>
                    </thead>
                    <tbody>
                        {audit_rows_html}
                    </tbody>
                </table>
            </div>

            <div class="mt-4 p-4 rounded-xl bg-purple-950/40 border border-purple-500/25 text-xs text-purple-200 flex items-start gap-2">
                <i class="fas fa-circle-info text-cyan-400 mt-0.5"></i>
                <div>
                    <strong class="text-white">Nhận xét từ AI Agent:</strong> {insights.get('data_quality_assessment', '')}
                </div>
            </div>
        </section>

        <!-- 3. CHỈ SỐ KPI CHÍNH (KEY PERFORMANCE INDICATORS) -->
        <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {"".join([f'''
            <div class="galaxy-card rounded-2xl p-5 flex items-center gap-4">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-purple-600/30 to-cyan-500/30 text-cyan-300 border border-purple-500/30 flex items-center justify-center text-xl shrink-0 shadow-lg shadow-purple-950/30">
                    <i class="fas {card.get('icon', 'fa-chart-pie')}"></i>
                </div>
                <div>
                    <div class="text-xs text-purple-300/80 font-medium">{card.get('title')}</div>
                    <div class="text-2xl font-bold text-white mt-0.5">{card.get('value')}</div>
                    <div class="text-[11px] text-slate-400 mt-0.5">{card.get('sub')}</div>
                </div>
            </div>
            ''' for card in kpis])}
        </section>

        <!-- 4. KHÁM PHÁ TRỰC QUAN HÓA (INTERACTIVE PLOTLY EDA CHARTS) -->
        <section class="galaxy-card rounded-3xl p-6 sm:p-8 space-y-6">
            <div class="flex items-center gap-3 pb-3 border-b border-purple-500/15">
                <div class="w-9 h-9 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center justify-center font-bold text-lg">
                    <i class="fas fa-chart-line text-cyan-400"></i>
                </div>
                <div>
                    <h2 class="text-lg font-bold text-white">3. Trực Quan Hóa Dữ Liệu Tương Tác (Automated EDA)</h2>
                    <p class="text-xs text-slate-400">Biểu đồ động Plotly cho phép phóng to, thu nhỏ và hover xem chi tiết</p>
                </div>
            </div>

            <!-- Khung lưới biểu đồ -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <!-- Heatmap Tương Quan -->
                <div class="bg-[#0b0d26]/80 rounded-2xl p-4 border border-purple-500/20" id="chart-corr-container">
                    <div id="plot-correlation_heatmap" class="w-full h-96"></div>
                </div>

                <!-- Phân phối / Outlier Box -->
                <div class="bg-[#0b0d26]/80 rounded-2xl p-4 border border-purple-500/20" id="chart-dist-container">
                    <div id="plot-distribution" class="w-full h-96"></div>
                </div>

                <!-- Phân loại / Category Breakdown -->
                <div class="bg-[#0b0d26]/80 rounded-2xl p-4 border border-purple-500/20" id="chart-cat-container">
                    <div id="plot-categorical_breakdown" class="w-full h-96"></div>
                </div>

                <!-- Scatter Relationship / Phân tán -->
                <div class="bg-[#0b0d26]/80 rounded-2xl p-4 border border-purple-500/20" id="chart-scatter-container">
                    <div id="plot-scatter_relation" class="w-full h-96"></div>
                </div>
            </div>

            <!-- Biểu đồ Xu Hướng Thời Gian nếu có -->
            <div class="bg-[#0b0d26]/80 rounded-2xl p-4 border border-purple-500/20 hidden" id="chart-trend-container">
                <div id="plot-time_trend" class="w-full h-80"></div>
            </div>
        </section>

        <!-- 5. CÁC PHÁT HIỆN CỐT LÕI TỪ AI (AI KEY FINDINGS & RISKS) -->
        <section class="space-y-6">
            <div class="galaxy-card rounded-3xl p-6 sm:p-8">
                <div class="flex items-center gap-3 mb-6 pb-3 border-b border-purple-500/15">
                    <div class="w-9 h-9 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center justify-center font-bold text-lg">
                        <i class="fas fa-lightbulb"></i>
                    </div>
                    <div>
                        <h2 class="text-lg font-bold text-white">4. Các Phát Hiện Trọng Yếu Từ AI Agent (Key Discoveries)</h2>
                        <p class="text-xs text-slate-400">Phân tích đa chiều về tương quan, phân khúc chủ lực và đòn bẩy tăng trưởng</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
                    {findings_html}
                </div>
            </div>

            <!-- Cảnh Báo Rủi Ro & Dị Thường -->
            <div class="galaxy-card rounded-3xl p-6 sm:p-8">
                <div class="flex items-center gap-3 mb-4 pb-3 border-b border-purple-500/15">
                    <div class="w-9 h-9 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center justify-center font-bold text-lg">
                        <i class="fas fa-shield-virus"></i>
                    </div>
                    <div>
                        <h2 class="text-lg font-bold text-white">5. Cảnh Báo Rủi Ro & Biến Động Bất Thường</h2>
                        <p class="text-xs text-slate-400">Các điểm dị biệt, độ lệch chuẩn và khuyến nghị phòng ngừa rủi ro</p>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {risks_html}
                </div>
            </div>
        </section>

        <!-- 6. KHUYẾN NGHỊ CHIẾN LƯỢC HÀNH ĐỘNG (ACTIONABLE RECOMMENDATIONS ROADMAP) -->
        <section class="galaxy-card rounded-3xl p-6 sm:p-8">
            <div class="flex items-center gap-3 mb-6 pb-3 border-b border-purple-500/15">
                <div class="w-9 h-9 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-bold text-lg">
                    <i class="fas fa-road"></i>
                </div>
                <div>
                    <h2 class="text-lg font-bold text-white">6. Lộ Trình Hành Động Chiến Lược (Strategic Roadmap)</h2>
                    <p class="text-xs text-slate-400">Đề xuất các bước thực thi cụ thể phân bổ theo 3 mốc thời gian</p>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <!-- Quick Wins -->
                <div class="rounded-2xl p-5 border border-emerald-500/30 bg-emerald-950/30">
                    <div class="flex items-center gap-2 mb-3 text-emerald-300 font-bold text-sm">
                        <i class="fas fa-bolt"></i>
                        <span>Ngắn Hạn: Quick-Wins (1-3 Tháng)</span>
                    </div>
                    <ul class="space-y-2">
                        {qw_items}
                    </ul>
                </div>

                <!-- Medium Term -->
                <div class="rounded-2xl p-5 border border-cyan-500/30 bg-cyan-950/30">
                    <div class="flex items-center gap-2 mb-3 text-cyan-300 font-bold text-sm">
                        <i class="fas fa-tasks"></i>
                        <span>Trung Hạn: Tối Ưu (3-6 Tháng)</span>
                    </div>
                    <ul class="space-y-2">
                        {mt_items}
                    </ul>
                </div>

                <!-- Long Term -->
                <div class="rounded-2xl p-5 border border-purple-500/30 bg-purple-950/30">
                    <div class="flex items-center gap-2 mb-3 text-purple-300 font-bold text-sm">
                        <i class="fas fa-chess-queen"></i>
                        <span>Dài Hạn: Chuyển Đổi (6-12 Tháng)</span>
                    </div>
                    <ul class="space-y-2">
                        {lt_items}
                    </ul>
                </div>
            </div>
        </section>

        <!-- 7. BẢNG PHỤ LỤC THỐNG KÊ CHI TIẾT (APPENDIX) -->
        <section class="galaxy-card rounded-3xl p-6 sm:p-8">
            <div class="flex items-center gap-3 mb-4 pb-3 border-b border-purple-500/15">
                <div class="w-9 h-9 rounded-xl bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center justify-center font-bold text-lg">
                    <i class="fas fa-table-cells"></i>
                </div>
                <div>
                    <h2 class="text-lg font-bold text-white">7. Phụ Lục Thống Kê Mô Tả Chi Tiết</h2>
                    <p class="text-xs text-slate-400">Thông số kỹ thuật toàn diện của các biến số định lượng sau chuẩn hóa</p>
                </div>
            </div>

            <div class="overflow-x-auto rounded-xl border border-purple-500/20 bg-[#0b0d26]/80">
                <table class="w-full text-left border-collapse">
                    <thead>
                        <tr class="bg-[#131633] border-b border-purple-500/20 text-xs font-semibold text-purple-200 uppercase">
                            <th class="py-2.5 px-3">Cột Dữ Liệu</th>
                            <th class="py-2.5 px-3 text-right">Trung Bình (Mean)</th>
                            <th class="py-2.5 px-3 text-right">Trung Vị (Median)</th>
                            <th class="py-2.5 px-3 text-right">Độ Lệch Chuẩn (Std)</th>
                            <th class="py-2.5 px-3 text-right">Nhỏ Nhất (Min)</th>
                            <th class="py-2.5 px-3 text-right">Lớn Nhất (Max)</th>
                            <th class="py-2.5 px-3 text-right">Độ Lệch (Skew)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {num_stats_rows}
                    </tbody>
                </table>
            </div>
        </section>

        <!-- FOOTER -->
        <footer class="pt-6 border-t border-cyan-400/20 text-center text-xs text-cyan-200/70 space-y-1">
            <p>Báo cáo được khởi tạo tự động bởi <strong class="text-pink-400">DataMind AI Agent • Công Ty Cổ Phần DataMind Intelligence</strong> &bull; Đã kiểm duyệt và bảo vệ quyền sở hữu dữ liệu</p>
            <p>Thời gian phát hành: {now_str} &bull; Hệ thống phân tích kinh doanh thông minh DataMind Enterprise</p>
        </footer>

    </div>

    <!-- SCRIPT RENDER PLOTLY & DOWNLOAD -->
    <script>
        const chartData = {charts_json};

        // Render Plotly charts in Luminous Galaxy Theme
        window.addEventListener('DOMContentLoaded', () => {{
            const chartKeys = ['correlation_heatmap', 'distribution', 'categorical_breakdown', 'scatter_relation', 'time_trend'];
            chartKeys.forEach(key => {{
                const el = document.getElementById('plot-' + key);
                if (el && chartData[key]) {{
                    const cfg = {{ responsive: true, displayModeBar: false }};
                    const layout = chartData[key].layout || {{}};
                    layout.paper_bgcolor = "rgba(0,0,0,0)";
                    layout.plot_bgcolor = "rgba(22, 28, 70, 0.45)";
                    layout.font = {{ color: "#e2e8f0", family: "Plus Jakarta Sans, sans-serif" }};
                    Plotly.newPlot(el, chartData[key].data, layout, cfg);
                    if (key === 'time_trend') {{
                        const tc = document.getElementById('chart-trend-container');
                        if (tc) tc.classList.remove('hidden');
                    }}
                }} else if (el) {{
                    const container = el.parentElement;
                    if (container && key !== 'time_trend') {{
                        container.innerHTML = '<div class="h-64 flex items-center justify-center text-xs text-purple-300/60 italic">Không đủ dữ liệu biến số để vẽ biểu đồ này</div>';
                    }}
                }}
            }});
        }});

        // Download HTML File function
        function downloadHtmlFile() {{
            const blob = new Blob([document.documentElement.outerHTML], {{ type: 'text/html;charset=utf-8' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Bao_Cao_Galaxy_AI_${{new Date().toISOString().slice(0,10)}}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>
"""
        return html_content
