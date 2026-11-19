"""
Data Cleaning & Quality Diagnostic Engine with Human-in-the-Loop Approval
"""
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Any, Tuple

class DataCleaner:
    def __init__(self):
        self.audit_log = []
        
    def diagnose(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Quét và chẩn đoán toàn diện chất lượng dữ liệu thô, tạo đề xuất để người dùng duyệt"""
        total_rows, total_cols = df.shape
        total_cells = total_rows * total_cols
        
        # 1. Trùng lặp (Duplicates)
        dup_count = int(df.duplicated().sum())
        dup_pct = round((dup_count / total_rows) * 100, 2) if total_rows > 0 else 0
        
        # 2. Khuyết thiếu (Missing values)
        null_counts = df.isnull().sum()
        total_null_cells = int(null_counts.sum())
        null_cell_pct = round((total_null_cells / total_cells) * 100, 2) if total_cells > 0 else 0
        
        missing_by_col = []
        for col in df.columns:
            cnt = int(null_counts[col])
            if cnt > 0:
                pct = round((cnt / total_rows) * 100, 2)
                col_type = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "categorical"
                missing_by_col.append({
                    "column": col,
                    "count": cnt,
                    "percentage": pct,
                    "type": col_type
                })
                
        # 3. Ngoại lai (Outliers) cho các cột số
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        outliers_by_col = []
        total_outlier_count = 0
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 5:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_mask = (series < lower_bound) | (series > upper_bound)
            outlier_cnt = int(outlier_mask.sum())
            if outlier_cnt > 0:
                total_outlier_count += outlier_cnt
                outliers_by_col.append({
                    "column": col,
                    "count": outlier_cnt,
                    "percentage": round((outlier_cnt / len(series)) * 100, 2),
                    "lower_bound": float(round(lower_bound, 2)),
                    "upper_bound": float(round(upper_bound, 2)),
                    "min_val": float(round(series.min(), 2)),
                    "max_val": float(round(series.max(), 2))
                })
                
        # 4. Cột chuỗi có khoảng trắng thừa hoặc không đồng nhất (Text formatting)
        string_cols = df.select_dtypes(include=["object"]).columns.tolist()
        text_issues = []
        for col in string_cols:
            series = df[col].dropna().astype(str)
            has_strip_issues = (series.str.strip() != series).sum()
            # Kiểm tra xem có phải chuỗi ngày tháng không
            is_date = False
            sample_val = series.iloc[0] if len(series) > 0 else ""
            if re.search(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{4}", sample_val):
                is_date = True
                
            if has_strip_issues > 0 or is_date:
                text_issues.append({
                    "column": col,
                    "strip_count": int(has_strip_issues),
                    "is_potential_date": is_date
                })

        # 5. Cột có phương sai bằng 0 (chỉ có 1 giá trị duy nhất)
        zero_var_cols = [col for col in df.columns if df[col].nunique(dropna=False) == 1]
        
        # 6. Tính điểm sức khỏe dữ liệu (Health Score: 0 - 100)
        # Giảm điểm dựa trên tỷ lệ thiếu hụt, trùng lặp và ngoại lai
        score = 100.0
        score -= min(null_cell_pct * 2.5, 40.0) # Tối đa trừ 40đ vì null
        score -= min(dup_pct * 2.0, 25.0)       # Tối đa trừ 25đ vì trùng lặp
        if total_rows > 0:
            outlier_pct = (total_outlier_count / total_rows) * 100
            score -= min(outlier_pct * 1.5, 20.0) # Tối đa trừ 20đ vì ngoại lai
        if len(text_issues) > 0:
            score -= min(len(text_issues) * 2.0, 10.0)
        health_score = max(5.0, round(score, 1))

        # 7. TẠO DANH SÁCH ĐỀ XUẤT LÀM SẠCH (Cleaning Proposals for User Approval)
        proposals = []
        
        # Đề xuất xóa trùng lặp
        if dup_count > 0:
            proposals.append({
                "action_id": "drop_duplicates",
                "category": "Trùng lặp",
                "target_col": "Toàn bộ bảng",
                "issue_desc": f"Phát hiện {dup_count} dòng trùng lặp 100% ({dup_pct}% dữ liệu).",
                "proposed_action": f"Xóa toàn bộ {dup_count} dòng trùng lặp, giữ lại bản ghi đầu tiên.",
                "options": [
                    {"id": "drop_first", "label": "Xóa bản ghi trùng (giữ bản đầu)"},
                    {"id": "ignore", "label": "Giữ nguyên (không xóa)"}
                ],
                "selected_option": "drop_first",
                "approved": True,
                "impact_estimate": f"-{dup_count} dòng"
            })
            
        # Đề xuất xử lý giá trị khuyết
        for item in missing_by_col:
            col = item["column"]
            cnt = item["count"]
            pct = item["percentage"]
            col_type = item["type"]
            
            if col_type == "numeric":
                median_val = float(round(df[col].median(), 2))
                mean_val = float(round(df[col].mean(), 2))
                opts = [
                    {"id": "median", "label": f"Điền Trung vị ({median_val}) - Khuyến nghị"},
                    {"id": "mean", "label": f"Điền Trung bình ({mean_val})"},
                    {"id": "drop_rows", "label": f"Xóa các dòng thiếu ({cnt} dòng)"},
                    {"id": "zero", "label": "Điền số 0"}
                ]
                sel = "median"
                prop_act = f"Điền giá trị trung vị ({median_val}) để tránh làm lệch phân phối."
            else:
                mode_series = df[col].mode()
                mode_val = str(mode_series.iloc[0]) if len(mode_series) > 0 else "Chưa xác định"
                opts = [
                    {"id": "mode", "label": f"Điền giá trị phổ biến nhất ('{mode_val}')"},
                    {"id": "constant", "label": "Điền nhãn 'Chưa xác định'"},
                    {"id": "drop_rows", "label": f"Xóa các dòng thiếu ({cnt} dòng)"}
                ]
                sel = "constant" if pct > 10 else "mode"
                prop_act = f"Điền nhãn '{sel == 'mode' and mode_val or 'Chưa xác định'}' cho {cnt} ô trống."

            proposals.append({
                "action_id": f"missing_{col}",
                "category": "Giá trị thiếu",
                "target_col": col,
                "issue_desc": f"Cột có {cnt} giá trị khuyết thiếu ({pct}%).",
                "proposed_action": prop_act,
                "options": opts,
                "selected_option": sel,
                "approved": True,
                "impact_estimate": f"{cnt} ô cần điền"
            })
            
        # Đề xuất xử lý Outliers
        for item in outliers_by_col:
            col = item["column"]
            cnt = item["count"]
            low = item["lower_bound"]
            high = item["upper_bound"]
            
            proposals.append({
                "action_id": f"outlier_{col}",
                "category": "Giá trị ngoại lai",
                "target_col": col,
                "issue_desc": f"Phát hiện {cnt} giá trị vượt ngưỡng IQR [{low} -> {high}].",
                "proposed_action": f"Cắt tỉa cận biên (Winsorize/Cap) về khoảng [{low}, {high}] để bảo toàn số lượng mẫu.",
                "options": [
                    {"id": "cap", "label": f"Cắt về cận biên [{low} - {high}] - Khuyến nghị"},
                    {"id": "drop", "label": f"Xóa các dòng chứa ngoại lai ({cnt} dòng)"},
                    {"id": "keep", "label": "Giữ nguyên (không xử lý)"}
                ],
                "selected_option": "cap",
                "approved": True,
                "impact_estimate": f"{cnt} giá trị điều chỉnh"
            })
            
        # Đề xuất xử lý văn bản và định dạng ngày
        for item in text_issues:
            col = item["column"]
            strip_cnt = item["strip_count"]
            is_date = item["is_potential_date"]
            
            if strip_cnt > 0:
                proposals.append({
                    "action_id": f"strip_{col}",
                    "category": "Định dạng chuỗi",
                    "target_col": col,
                    "issue_desc": f"{strip_cnt} dòng có khoảng trắng thừa ở đầu/cuối.",
                    "proposed_action": "Loại bỏ khoảng trắng thừa (Strip whitespace) và chuẩn hóa.",
                    "options": [
                        {"id": "strip_trim", "label": "Xóa khoảng trắng thừa (Trim)"},
                        {"id": "strip_title", "label": "Trim + Viết hoa chữ đầu từng từ (Title case)"},
                        {"id": "ignore", "label": "Bỏ qua"}
                    ],
                    "selected_option": "strip_trim",
                    "approved": True,
                    "impact_estimate": f"{strip_cnt} ô được làm sạch"
                })
            
            if is_date:
                proposals.append({
                    "action_id": f"date_{col}",
                    "category": "Chuyển đổi kiểu",
                    "target_col": col,
                    "issue_desc": "Dữ liệu có định dạng ngày tháng nhưng đang lưu dạng chuỗi văn bản.",
                    "proposed_action": "Chuyển đổi sang kiểu Datetime (YYYY-MM-DD chuẩn).",
                    "options": [
                        {"id": "convert_datetime", "label": "Chuyển sang Datetime chuẩn"},
                        {"id": "keep_string", "label": "Giữ nguyên dạng chuỗi"}
                    ],
                    "selected_option": "convert_datetime",
                    "approved": True,
                    "impact_estimate": f"Toàn bộ cột '{col}'"
                })

        # Đề xuất xóa cột hằng số
        for col in zero_var_cols:
            val = df[col].iloc[0] if len(df) > 0 else "N/A"
            proposals.append({
                "action_id": f"zero_var_{col}",
                "category": "Cột không biến thiên",
                "target_col": col,
                "issue_desc": f"Cột chỉ chứa 1 giá trị duy nhất ('{val}'), không đóng góp thông tin cho phân tích.",
                "proposed_action": "Xóa cột này để tối ưu hóa bộ nhớ và giảm nhiễu.",
                "options": [
                    {"id": "drop_col", "label": "Xóa cột này"},
                    {"id": "keep_col", "label": "Giữ lại"}
                ],
                "selected_option": "drop_col",
                "approved": True,
                "impact_estimate": "-1 cột"
            })

        return {
            "summary": {
                "total_rows": total_rows,
                "total_cols": total_cols,
                "total_cells": total_cells,
                "duplicate_rows": dup_count,
                "missing_cells": total_null_cells,
                "missing_percentage": null_cell_pct,
                "outlier_count": total_outlier_count,
                "health_score": health_score,
                "health_grade": "Tốt" if health_score >= 85 else ("Trung bình" if health_score >= 60 else "Kém")
            },
            "missing_details": missing_by_col,
            "outlier_details": outliers_by_col,
            "proposals": proposals
        }

    def execute_approved_cleaning(self, df_raw: pd.DataFrame, approved_actions: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Áp dụng các hành động làm sạch đã được người dùng duyệt"""
        df = df_raw.copy()
        audit_trail = []
        
        # Tạo map cấu hình từ danh sách duyệt
        action_map = {act["action_id"]: act for act in approved_actions}
        
        # 1. Trùng lặp
        if "drop_duplicates" in action_map and action_map["drop_duplicates"].get("approved", False):
            opt = action_map["drop_duplicates"].get("selected_option", "drop_first")
            if opt == "drop_first":
                initial_count = len(df)
                df = df.drop_duplicates(keep="first")
                removed = initial_count - len(df)
                audit_trail.append({
                    "action": "Xóa trùng lặp",
                    "details": f"Đã xóa {removed} dòng trùng lặp hoàn toàn (giữ bản ghi đầu).",
                    "rows_affected": removed
                })
                
        # 2. Xóa cột không biến thiên
        for action_id, act in action_map.items():
            if action_id.startswith("zero_var_") and act.get("approved", False):
                col = act.get("target_col")
                if col in df.columns and act.get("selected_option") == "drop_col":
                    df = df.drop(columns=[col])
                    audit_trail.append({
                        "action": f"Xóa cột '{col}'",
                        "details": f"Đã loại bỏ cột hằng số '{col}' theo phê duyệt.",
                        "rows_affected": 0
                    })

        # 3. Chuẩn hóa chuỗi và ngày tháng
        for action_id, act in action_map.items():
            if not act.get("approved", False):
                continue
            col = act.get("target_col")
            if col not in df.columns:
                continue
                
            if action_id.startswith("strip_"):
                opt = act.get("selected_option", "strip_trim")
                if opt in ["strip_trim", "strip_title"]:
                    s = df[col].astype(str).str.strip()
                    if opt == "strip_title":
                        s = s.str.title()
                    df[col] = s
                    audit_trail.append({
                        "action": f"Chuẩn hóa chuỗi '{col}'",
                        "details": f"Đã loại bỏ khoảng trắng thừa và chuẩn hóa ({opt}).",
                        "rows_affected": len(df)
                    })
                    
            elif action_id.startswith("date_"):
                opt = act.get("selected_option", "convert_datetime")
                if opt == "convert_datetime":
                    try:
                        df[col] = pd.to_datetime(df[col], errors="coerce", format="mixed")
                        audit_trail.append({
                            "action": f"Định dạng ngày '{col}'",
                            "details": f"Đã chuyển đổi cột '{col}' sang định dạng ngày tháng chuẩn (Datetime).",
                            "rows_affected": len(df)
                        })
                    except Exception as e:
                        pass

        # 4. Xử lý giá trị khuyết thiếu
        for action_id, act in action_map.items():
            if not act.get("approved", False):
                continue
            if not action_id.startswith("missing_"):
                continue
            col = act.get("target_col")
            if col not in df.columns:
                continue
                
            opt = act.get("selected_option", "median")
            missing_count = int(df[col].isnull().sum())
            if missing_count == 0:
                continue
                
            if opt == "median" and pd.api.types.is_numeric_dtype(df[col]):
                fill_val = df[col].median()
                df[col] = df[col].fillna(fill_val)
                audit_trail.append({
                    "action": f"Điền khuyết '{col}'",
                    "details": f"Đã điền {missing_count} ô trống bằng giá trị trung vị (Median: {round(fill_val, 2)}).",
                    "rows_affected": missing_count
                })
            elif opt == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                fill_val = df[col].mean()
                df[col] = df[col].fillna(fill_val)
                audit_trail.append({
                    "action": f"Điền khuyết '{col}'",
                    "details": f"Đã điền {missing_count} ô trống bằng giá trị trung bình (Mean: {round(fill_val, 2)}).",
                    "rows_affected": missing_count
                })
            elif opt == "zero" and pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(0)
                audit_trail.append({
                    "action": f"Điền khuyết '{col}'",
                    "details": f"Đã điền số 0 cho {missing_count} ô trống.",
                    "rows_affected": missing_count
                })
            elif opt == "mode":
                mode_val = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "Unknown"
                df[col] = df[col].fillna(mode_val)
                audit_trail.append({
                    "action": f"Điền khuyết '{col}'",
                    "details": f"Đã điền {missing_count} ô trống bằng giá trị phổ biến nhất ('{mode_val}').",
                    "rows_affected": missing_count
                })
            elif opt == "constant":
                df[col] = df[col].fillna("Chưa xác định")
                audit_trail.append({
                    "action": f"Điền khuyết '{col}'",
                    "details": f"Đã điền nhãn 'Chưa xác định' cho {missing_count} ô trống.",
                    "rows_affected": missing_count
                })
            elif opt == "drop_rows":
                prev_len = len(df)
                df = df.dropna(subset=[col])
                dropped = prev_len - len(df)
                audit_trail.append({
                    "action": f"Xóa hàng khuyết '{col}'",
                    "details": f"Đã xóa {dropped} hàng có giá trị trống tại cột '{col}'.",
                    "rows_affected": dropped
                })

        # 5. Xử lý giá trị ngoại lai (Outliers)
        for action_id, act in action_map.items():
            if not act.get("approved", False):
                continue
            if not action_id.startswith("outlier_"):
                continue
            col = act.get("target_col")
            if col not in df.columns or not pd.api.types.is_numeric_dtype(df[col]):
                continue
                
            opt = act.get("selected_option", "cap")
            series = df[col].dropna()
            if len(series) < 5:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            num_outliers = int(outlier_mask.sum())
            if num_outliers == 0:
                continue
                
            if opt == "cap":
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                audit_trail.append({
                    "action": f"Cắt cận biên ngoại lai '{col}'",
                    "details": f"Đã điều chỉnh {num_outliers} giá trị ngoại lai về khoảng an toàn [{round(lower_bound, 2)}, {round(upper_bound, 2)}].",
                    "rows_affected": num_outliers
                })
            elif opt == "drop":
                prev_len = len(df)
                df = df[~outlier_mask]
                dropped = prev_len - len(df)
                audit_trail.append({
                    "action": f"Xóa ngoại lai '{col}'",
                    "details": f"Đã xóa {dropped} dòng chứa giá trị ngoại lai tại cột '{col}'.",
                    "rows_affected": dropped
                })

        # Đánh giá lại sức khỏe dữ liệu sau khi làm sạch
        post_diag = self.diagnose(df)
        post_summary = post_diag["summary"]
        
        comparison = {
            "before": {
                "rows": len(df_raw),
                "cols": len(df_raw.columns),
                "null_cells": int(df_raw.isnull().sum().sum()),
                "duplicates": int(df_raw.duplicated().sum()),
                "health_score": round(self.diagnose(df_raw)["summary"]["health_score"], 1)
            },
            "after": {
                "rows": len(df),
                "cols": len(df.columns),
                "null_cells": int(df.isnull().sum().sum()),
                "duplicates": int(df.duplicated().sum()),
                "health_score": round(post_summary["health_score"], 1)
            },
            "audit_trail": audit_trail
        }
        
        return df, comparison
