"""
Exploratory Data Analysis (EDA) and Interactive Plotly Chart Generator
"""
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

class EDAEngine:
    def __init__(self):
        pass

    def run_eda(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Thực hiện phân tích khám phá dữ liệu toàn diện và tạo biểu đồ Plotly"""
        total_rows, total_cols = df.shape
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime", "datetime64[ns]"]).columns.tolist()

        # 1. Thống kê mô tả số học (Descriptive Statistics)
        numeric_stats = []
        for col in numeric_cols:
            s = df[col].dropna()
            if len(s) == 0:
                continue
            numeric_stats.append({
                "column": col,
                "mean": float(round(s.mean(), 2)),
                "std": float(round(s.std(), 2)) if len(s) > 1 else 0.0,
                "median": float(round(s.median(), 2)),
                "min": float(round(s.min(), 2)),
                "max": float(round(s.max(), 2)),
                "q25": float(round(s.quantile(0.25), 2)),
                "q75": float(round(s.quantile(0.75), 2)),
                "skew": float(round(s.skew(), 2)) if len(s) > 2 else 0.0
            })

        # 2. Thống kê phân loại (Categorical Statistics)
        categorical_stats = []
        for col in categorical_cols:
            s = df[col].dropna().astype(str)
            val_counts = s.value_counts()
            top_3 = [{"label": str(k), "count": int(v), "pct": round((v / len(s)) * 100, 1)} 
                     for k, v in val_counts.head(3).items()]
            categorical_stats.append({
                "column": col,
                "unique_values": int(s.nunique()),
                "top_category": str(val_counts.index[0]) if len(val_counts) > 0 else "N/A",
                "top_count": int(val_counts.iloc[0]) if len(val_counts) > 0 else 0,
                "top_items": top_3
            })

        # 3. Phân tích Tương quan (Correlation Analysis)
        correlations = []
        corr_matrix_data = None
        if len(numeric_cols) >= 2:
            corr_df = df[numeric_cols].corr().round(2)
            corr_matrix_data = {
                "columns": numeric_cols,
                "values": corr_df.values.tolist()
            }
            # Lọc các cặp tương quan mạnh nhất (|r| >= 0.3)
            for i in range(len(numeric_cols)):
                for j in range(i + 1, len(numeric_cols)):
                    c1 = numeric_cols[i]
                    c2 = numeric_cols[j]
                    val = corr_df.loc[c1, c2]
                    if not np.isnan(val) and abs(val) > 0.01:
                        correlations.append({
                            "col1": c1,
                            "col2": c2,
                            "correlation": float(val),
                            "abs_corr": abs(float(val)),
                            "strength": "Rất mạnh" if abs(val) >= 0.7 else ("Trung bình" if abs(val) >= 0.4 else "Yếu")
                        })
            correlations = sorted(correlations, key=lambda x: x["abs_corr"], reverse=True)

        # 4. TẠO BIỂU ĐỒ PLOTLY CHUYÊN NGHIỆP (CYAN & PINK THEME)
        charts = {}
        cyan_pink_palette = ["#06b6d4", "#ec4899", "#0ea5e9", "#f43f5e", "#38bdf8", "#fb7185", "#10b981", "#fbbf24"]

        # 4.1. Biểu đồ Heatmap Tương quan (Cyan - Navy - Pink Colorscale)
        if corr_matrix_data and len(numeric_cols) >= 2:
            fig_corr = go.Figure(data=go.Heatmap(
                z=corr_matrix_data["values"],
                x=corr_matrix_data["columns"],
                y=corr_matrix_data["columns"],
                colorscale=[[0, "#06b6d4"], [0.5, "#0f172a"], [1, "#ec4899"]],
                zmin=-1, zmax=1,
                text=corr_matrix_data["values"],
                texttemplate="%{text}",
                textfont={"size": 11, "color": "#ffffff"},
                hoverongaps=False
            ))
            fig_corr.update_layout(
                template="plotly_dark",
                title="Ma Trận Tương Quan Tuyến Tính (Correlation Heatmap)",
                height=420,
                margin=dict(l=40, r=40, t=50, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(10, 15, 30, 0.45)",
                font=dict(color="#cbd5e1", family="Plus Jakarta Sans, sans-serif")
            )
            charts["correlation_heatmap"] = json.loads(fig_corr.to_json())

        # 4.2. Biểu đồ Phân phối (Distribution Histogram) cho cột số quan trọng
        if len(numeric_cols) > 0:
            target_num = None
            priority_names = ["doanh thu", "revenue", "sales", "lương", "salary", "lợi nhuận", "profit", "income", "thu nhập"]
            for col in numeric_cols:
                if any(p in col.lower() for p in priority_names):
                    target_num = col
                    break
            if not target_num:
                target_num = numeric_cols[0]

            fig_dist = px.histogram(
                df, x=target_num,
                nbins=25,
                marginal="box",
                title=f"Phân Phối Tần Suất & Hộp Ngoại Lai ({target_num})",
                color_discrete_sequence=["#06b6d4"],
                opacity=0.88,
                template="plotly_dark"
            )
            fig_dist.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=50, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(10, 15, 30, 0.45)",
                bargap=0.08,
                font=dict(color="#cbd5e1", family="Plus Jakarta Sans, sans-serif")
            )
            charts["distribution"] = json.loads(fig_dist.to_json())

        # 4.3. Biểu đồ Phân loại (Categorical Bar / Donut)
        if len(categorical_cols) > 0:
            cat_target = None
            for col in categorical_cols:
                n_uniq = df[col].nunique()
                if 2 <= n_uniq <= 12:
                    cat_target = col
                    break
            if not cat_target:
                cat_target = categorical_cols[0]

            top_cat_counts = df[cat_target].astype(str).value_counts().head(8).reset_index()
            top_cat_counts.columns = [cat_target, "Số lượng"]
            
            fig_cat = px.bar(
                top_cat_counts,
                x=cat_target,
                y="Số lượng",
                title=f"Cơ Cấu Số Lượng Theo Phân Khúc: {cat_target}",
                color=cat_target,
                color_discrete_sequence=cyan_pink_palette,
                text="Số lượng",
                template="plotly_dark"
            )
            fig_cat.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=50, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(10, 15, 30, 0.45)",
                showlegend=False,
                font=dict(color="#cbd5e1", family="Plus Jakarta Sans, sans-serif")
            )
            fig_cat.update_traces(textposition='outside')
            charts["categorical_breakdown"] = json.loads(fig_cat.to_json())

        # 4.4. Biểu đồ Phân tán (Scatter Plot) giữa 2 biến số mạnh nhất
        if len(correlations) > 0:
            top_pair = correlations[0]
            c_x = top_pair["col1"]
            c_y = top_pair["col2"]
            color_col = categorical_cols[0] if len(categorical_cols) > 0 and df[categorical_cols[0]].nunique() <= 8 else None
            
            fig_scatter = px.scatter(
                df, x=c_x, y=c_y,
                color=color_col,
                title=f"Mối Quan Hệ Tương Quan: {c_x} vs {c_y} (r = {top_pair['correlation']})",
                color_discrete_sequence=["#06b6d4", "#ec4899", "#38bdf8", "#f43f5e", "#10b981"],
                opacity=0.88,
                template="plotly_dark"
            )
            fig_scatter.update_layout(
                height=400,
                margin=dict(l=40, r=40, t=50, b=40),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(10, 15, 30, 0.45)",
                font=dict(color="#cbd5e1", family="Plus Jakarta Sans, sans-serif")
            )
            charts["scatter_relation"] = json.loads(fig_scatter.to_json())

        # 4.5. Biểu đồ Chuỗi Thời Gian (Time Trend) nếu có cột Datetime
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            date_col = datetime_cols[0]
            val_col = target_num if 'target_num' in locals() else numeric_cols[0]
            
            try:
                temp_df = df.copy()
                temp_df[date_col] = pd.to_datetime(temp_df[date_col], errors="coerce")
                temp_df = temp_df.dropna(subset=[date_col])
                if len(temp_df) > 5:
                    temp_df["Period"] = temp_df[date_col].dt.to_period("M").dt.to_timestamp()
                    trend_df = temp_df.groupby("Period")[val_col].agg(["sum", "mean"]).reset_index()
                    
                    fig_trend = px.line(
                        trend_df, x="Period", y="sum",
                        title=f"Xu Hướng Tổng {val_col} Theo Thời Gian",
                        markers=True,
                        line_shape="spline",
                        color_discrete_sequence=["#ec4899"],
                        template="plotly_dark"
                    )
                    fig_trend.update_layout(
                        height=380,
                        margin=dict(l=40, r=40, t=50, b=40),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(10, 12, 28, 0.45)",
                        font=dict(color="#cbd5e1", family="Plus Jakarta Sans, sans-serif")
                    )
                    charts["time_trend"] = json.loads(fig_trend.to_json())
            except Exception:
                pass

        # 5. TỔNG HỢP KPI CARDS
        kpi_cards = [
            {"title": "Tổng Số Bản Ghi", "value": f"{total_rows:,}", "sub": f"{total_cols} thuộc tính", "icon": "fa-database", "color": "blue"},
            {"title": "Trường Dữ Liệu Số", "value": f"{len(numeric_cols)}", "sub": "Biến định lượng", "icon": "fa-calculator", "color": "indigo"},
            {"title": "Trường Phân Loại", "value": f"{len(categorical_cols)}", "sub": "Biến phân khúc", "icon": "fa-tags", "color": "emerald"},
            {"title": "Cặp Tương Quan Đáng Chú Ý", "value": f"{len(correlations)}", "sub": f"Mạnh nhất: r={correlations[0]['correlation'] if len(correlations) > 0 else '0'}", "icon": "fa-project-diagram", "color": "purple"}
        ]

        return {
            "summary": {
                "rows": total_rows,
                "cols": total_cols,
                "numeric_cols": numeric_cols,
                "categorical_cols": categorical_cols,
                "datetime_cols": datetime_cols
            },
            "kpi_cards": kpi_cards,
            "numeric_stats": numeric_stats,
            "categorical_stats": categorical_stats,
            "top_correlations": correlations[:8],
            "charts": charts
        }
