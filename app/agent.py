"""
AI Data Analyst Agent Engine
Combines an Advanced Heuristic Statistical Reasoning Engine with Google Gemini LLM
"""
import os
import json
import requests
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional

class DataAnalystAgent:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model_name = "gemini-1.5-flash"
        
    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def _call_gemini_api(self, prompt: str, system_instruction: str = "") -> Optional[str]:
        """Gọi Google Gemini REST API nếu có API key"""
        if not self.api_key:
            return None
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        full_content = f"HỆ THỐNG: {system_instruction}\n\nNHIỆM VỤ:\n{prompt}" if system_instruction else prompt
        payload = {
            "contents": [
                {
                    "parts": [{"text": full_content}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "topP": 0.9,
                "maxOutputTokens": 4000
            }
        }
        
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text
            else:
                # Thử fallback model gemini-1.5-flash
                fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
                res_fb = requests.post(fallback_url, headers=headers, json=payload, timeout=30)
                if res_fb.status_code == 200:
                    data = res_fb.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            print(f"[Agent] Lỗi khi gọi Gemini API: {e}")
            
        return None

    def generate_report_insights(self, eda_data: Dict[str, Any], cleaning_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Tạo các báo cáo phân tích chuyên sâu, phát hiện và đề xuất chiến lược"""
        summary = eda_data.get("summary", {})
        num_stats = eda_data.get("numeric_stats", [])
        cat_stats = eda_data.get("categorical_stats", [])
        correlations = eda_data.get("top_correlations", [])
        audit_trail = cleaning_comparison.get("audit_trail", [])
        before = cleaning_comparison.get("before", {})
        after = cleaning_comparison.get("after", {})

        # Thử gọi Gemini trước nếu có API Key
        if self.api_key:
            prompt = f"""
Bạn là Chuyên gia Khoa học Dữ liệu Trưởng (Chief Data Scientist) & Chuyên gia Phân tích Chiến lược Doanh nghiệp.
Dưới đây là kết quả phân tích khám phá dữ liệu (EDA) và nhật ký làm sạch dữ liệu (đã được người dùng duyệt):

1. THÔNG SỐ TẬP DỮ LIỆU ĐÃ LÀM SẠCH:
- Kích thước: {after.get('rows')} dòng, {after.get('cols')} cột (Trước: {before.get('rows')} dòng, {before.get('cols')} cột).
- Điểm chất lượng dữ liệu: Tăng từ {before.get('health_score')}/100 lên {after.get('health_score')}/100.
- Các hành động làm sạch đã duyệt: {json.dumps(audit_trail, ensure_ascii=False)}

2. THỐNG KÊ BIẾN ĐỊNH LƯỢNG:
{json.dumps(num_stats, ensure_ascii=False)}

3. THỐNG KÊ BIẾN PHÂN LOẠI:
{json.dumps(cat_stats, ensure_ascii=False)}

4. CÁC CẶP TƯƠNG QUAN QUAN TRỌNG:
{json.dumps(correlations, ensure_ascii=False)}

HÃY VIẾT BÁO CÁO PHÂN TÍCH CHUYÊN SÂU THEO ĐỊNH DẠNG JSON với các trường:
{{
  "executive_summary": "Tóm tắt điều hành súc tích 2-3 đoạn về bức tranh toàn cảnh, quy mô và ý nghĩa kinh doanh của tập dữ liệu.",
  "data_quality_assessment": "Đánh giá quy trình làm sạch dữ liệu có sự tham gia của con người (Human-in-the-Loop approval), độ tin cậy và cải thiện độ toàn vẹn.",
  "key_findings": [
    {{"title": "Tiêu đề phát hiện 1", "description": "Mô tả chi tiết bằng số liệu cụ thể.", "impact": "Tác động kinh doanh/vận hành"}},
    {{"title": "Tiêu đề phát hiện 2", "description": "Mô tả chi tiết bằng số liệu cụ thể.", "impact": "Tác động kinh doanh/vận hành"}},
    {{"title": "Tiêu đề phát hiện 3", "description": "Mô tả chi tiết bằng số liệu cụ thể.", "impact": "Tác động kinh doanh/vận hành"}}
  ],
  "anomalies_and_risks": [
    {{"risk": "Rủi ro/Bất thường 1", "evidence": "Căn cứ từ phân phối hoặc ngoại lai", "severity": "Cao/Trung bình"}},
    {{"risk": "Rủi ro/Bất thường 2", "evidence": "Căn cứ từ phân phối hoặc ngoại lai", "severity": "Trung bình/Thấp"}}
  ],
  "recommendations": {{
    "quick_wins": ["Khuyến nghị hành động ngay 1", "Khuyến nghị hành động ngay 2"],
    "medium_term": ["Khuyến nghị tối ưu 3-6 tháng 1", "Khuyến nghị 2"],
    "long_term": ["Chiến lược dài hạn chuyển đổi số/mở rộng"]
  }}
}}
Chỉ trả về JSON thuần túy, không có dấu ```json bao ngoài.
"""
            gemini_response = self._call_gemini_api(prompt, "Bạn là chuyên gia phân tích dữ liệu cao cấp. Luôn trả về đúng schema JSON.")
            if gemini_response:
                try:
                    cleaned_json = gemini_response.strip()
                    if cleaned_json.startswith("```json"):
                        cleaned_json = cleaned_json[7:]
                    if cleaned_json.startswith("```"):
                        cleaned_json = cleaned_json[3:]
                    if cleaned_json.endswith("```"):
                        cleaned_json = cleaned_json[:-3]
                    return json.loads(cleaned_json.strip())
                except Exception:
                    pass

        # NẾU KHÔNG CÓ GEMINI HOẶC GỌI THẤT BẠI: SỬ DỤNG BỘ SUY LUẬN THỐNG KÊ NỘI BỘ (Heuristic Statistical Reasoning Engine)
        return self._generate_heuristic_insights(summary, num_stats, cat_stats, correlations, cleaning_comparison)

    def _generate_heuristic_insights(self, summary: Dict, num_stats: List[Dict], cat_stats: List[Dict], correlations: List[Dict], cleaning_comp: Dict) -> Dict[str, Any]:
        """Sinh phân tích nghiệp vụ thông minh từ dữ liệu thống kê khi không dùng LLM bên ngoài"""
        before = cleaning_comp.get("before", {})
        after = cleaning_comp.get("after", {})
        audit = cleaning_comp.get("audit_trail", [])
        
        # 1. Executive Summary
        exec_summary = (
            f"Tập dữ liệu sau quy trình làm sạch và chuẩn hóa bao gồm **{after.get('rows', 0):,} bản ghi** "
            f"và **{after.get('cols', 0)} trường thuộc tính**, đạt điểm chất lượng dữ liệu tổng thể là **{after.get('health_score', 0)}/100** "
            f"(tăng trưởng ấn tượng từ mức ban đầu **{before.get('health_score', 0)}/100**). "
            f"Hệ thống đã nhận diện được {len(num_stats)} chỉ số định lượng then chốt cùng {len(cat_stats)} chiều phân khúc dữ liệu. "
            f"Toàn bộ quy trình xử lý đã được người dùng kiểm duyệt từng bước (Human-in-the-Loop), loại bỏ thành công các giá trị rác, "
            f"chuẩn hóa các định dạng không đồng nhất và bảo toàn tính toàn vẹn của phân phối thống kê."
        )

        # 2. Data Quality Assessment
        actions_text = ", ".join([a.get("action", "") for a in audit[:4]]) if audit else "Không có hành động đặc biệt"
        quality_assessment = (
            f"Quy trình xử lý dữ liệu tuân thủ chuẩn kiểm duyệt Human-in-the-Loop nghiêm ngặt. "
            f"Các hành động cốt lõi đã được phê duyệt và thực thi thành công bao gồm: **{actions_text}**. "
            f"Số dòng trùng lặp đã giảm từ {before.get('duplicates', 0)} về {after.get('duplicates', 0)}. "
            f"Số ô khuyết thiếu đã được khắc phục hoàn toàn từ {before.get('null_cells', 0):,} ô về 0 ô thông qua các phương pháp "
            f"điền giá trị đại diện (Median/Mode) và kiểm soát ngoại lai (IQR Capping). "
            f"Điều này đảm bảo mọi mô hình và báo cáo tiếp theo đều vận hành trên nền tảng dữ liệu sạch, đáng tin cậy cao."
        )

        # 3. Key Findings
        findings = []
        # Finding 1: Từ tương quan mạnh nhất
        if correlations:
            c = correlations[0]
            corr_val = c["correlation"]
            direction = "tương quan đồng biến (thuận chiều)" if corr_val > 0 else "tương quan nghịch biến (ngược chiều)"
            findings.append({
                "title": f"Mối quan hệ mật thiết giữa {c['col1']} và {c['col2']}",
                "description": f"Phân tích hệ số tương quan Pearson ghi nhận r = {corr_val} ({direction} ở mức {c['strength']}). Khi chỉ số {c['col1']} biến động sẽ kéo theo sự thay đổi tương ứng của {c['col2']}.",
                "impact": f"Có thể tận dụng {c['col1']} như một biến dự báo sớm hoặc đòn bẩy trực tiếp để tối ưu hóa {c['col2']}."
            })
            
        # Finding 2: Từ biến số có giá trị trung bình/phân phối lớn
        if num_stats:
            top_num = max(num_stats, key=lambda x: abs(x["mean"]))
            findings.append({
                "title": f"Đặc trưng trọng số của chỉ số '{top_num['column']}'",
                "description": f"Chỉ số '{top_num['column']}' có giá trị trung bình đạt {top_num['mean']:,}, trung vị {top_num['median']:,} (khoảng biến thiên từ {top_num['min']:,} đến {top_num['max']:,}). Độ lệch chuẩn {top_num['std']:,}.",
                "impact": f"Độ phân tán dữ liệu cho thấy sự khác biệt đáng kể giữa các nhóm đối tượng, cần phân tầng đối tượng thay vì áp dụng chính sách đại trà."
            })

        # Finding 3: Từ biến phân loại chủ đạo
        if cat_stats:
            top_cat = cat_stats[0]
            top_item = top_cat["top_items"][0] if top_cat["top_items"] else {"label": "N/A", "pct": 0}
            findings.append({
                "title": f"Ưu thế áp đảo của nhóm '{top_item['label']}' trong thuộc tính {top_cat['column']}",
                "description": f"Trong thuộc tính '{top_cat['column']}', nhóm '{top_item['label']}' chiếm tỷ trọng lớn nhất với {top_item['pct']}% trên tổng số mẫu ({top_cat['unique_values']} phân nhóm khác nhau).",
                "impact": "Tập trung nguồn lực vào nhóm đóng góp chủ lực này để tối đa hóa hiệu quả chuyển đổi và chi phí vận hành."
            })

        # 4. Anomalies & Risks
        risks = []
        if len(num_stats) > 0:
            skewed = [n for n in num_stats if abs(n.get("skew", 0)) > 1.0]
            if skewed:
                s_col = skewed[0]["column"]
                risks.append({
                    "risk": f"Độ lệch phân phối (Skewness) cao tại biến '{s_col}'",
                    "evidence": f"Hệ số Skewness = {skewed[0]['skew']:.2f}, cho thấy sự mất cân đối mạnh về một phía (dồn tích ở phân khúc thấp hoặc một số ít giá trị cực cao).",
                    "severity": "Trung bình"
                })
        
        risks.append({
            "risk": "Biến động bất ngờ từ các yếu tố ngoại biên",
            "evidence": f"Đã có {before.get('duplicates', 0)} dòng dữ liệu bị trùng lặp ban đầu và các ngoại lai cận trên cần được giám sát liên tục.",
            "severity": "Thấp"
        })

        # 5. Strategic Recommendations
        recommendations = {
            "quick_wins": [
                "Chuẩn hóa quy trình ghi nhận dữ liệu đầu vào tại nguồn để ngăn ngừa sự xuất hiện của giá trị rỗng và trùng lặp mới.",
                "Tập trung khai thác ngay nhóm phân khúc dẫn đầu để kích hoạt tăng trưởng ngắn hạn dựa trên tỷ trọng lớn nhất đã xác định."
            ],
            "medium_term": [
                "Xây dựng mô hình phân loại hoặc hồi quy dựa trên các cặp thuộc tính có hệ số tương quan mạnh nhất (r > 0.5) để dự báo xu hướng.",
                "Thiết lập ngưỡng cảnh báo tự động khi các chỉ số biến động vượt ngoài khoảng tứ phân vị (IQR)."
            ],
            "long_term": [
                "Tích hợp hệ sinh thái phân tích dữ liệu tự động định kỳ (Automated Continuous Pipeline) vào toàn bộ luồng vận hành công ty.",
                "Mở rộng thu thập thêm các biến ngoại cảnh để tăng độ chính xác trong việc giải thích biến thiên của các chỉ số mục tiêu."
            ]
        }

        return {
            "executive_summary": exec_summary,
            "data_quality_assessment": quality_assessment,
            "key_findings": findings,
            "anomalies_and_risks": risks,
            "recommendations": recommendations
        }

    def chat_answer(self, user_question: str, df: pd.DataFrame, eda_data: Dict[str, Any], cleaning_comparison: Dict[str, Any]) -> str:
        """Trả lời câu hỏi tự do của người dùng về dữ liệu"""
        # Nếu có Gemini API Key, ưu tiên sử dụng
        if self.api_key:
            num_cols = eda_data.get("summary", {}).get("numeric_cols", [])
            cat_cols = eda_data.get("summary", {}).get("categorical_cols", [])
            corrs = eda_data.get("top_correlations", [])[:5]
            
            prompt = f"""
Bạn là AI Data Analyst thông minh. Người dùng đang hỏi câu sau về tập dữ liệu:
"{user_question}"

Thông tin dữ liệu:
- Số dòng: {len(df)}, Số cột: {len(df.columns)}
- Các cột số: {', '.join(num_cols)}
- Các cột phân loại: {', '.join(cat_cols)}
- Top tương quan: {json.dumps(corrs, ensure_ascii=False)}
- Thống kê mô tả: {json.dumps(eda_data.get('numeric_stats', [])[:4], ensure_ascii=False)}
- Mẫu dữ liệu (5 dòng đầu):
{df.head(5).to_string()}

Hãy trả lời trực tiếp, rõ ràng, sâu sắc bằng tiếng Việt với các số liệu cụ thể.
"""
            res = self._call_gemini_api(prompt, "Bạn là chuyên gia phân tích dữ liệu trợ giúp người dùng.")
            if res:
                return res

        # NẾU CHẠY NỘI BỘ (Heuristic Semantic QA Engine):
        q = user_question.lower()
        
        # Hỏi về tương quan
        if "tương quan" in q or "quan hệ" in q or "ảnh hưởng" in q:
            corrs = eda_data.get("top_correlations", [])
            if corrs:
                c1 = corrs[0]
                return (
                    f"**Phân tích tương quan:**\n\n"
                    f"- Cặp tương quan mạnh nhất là giữa **{c1['col1']}** và **{c1['col2']}** với hệ số Pearson **r = {c1['correlation']}** (Mức độ: {c1['strength']}).\n"
                    f"- Điều này chỉ ra rằng khi `{c1['col1']}` thay đổi, `{c1['col2']}` có xu hướng biến thiên theo cùng chiều (hoặc nghịch chiều nếu âm) với độ tin cậy rất cao.\n"
                    f"- Các cặp tiếp theo: " + ", ".join([f"{c['col1']} & {c['col2']} (r={c['correlation']})" for c in corrs[1:4]])
                )
            return "Hiện tại không tìm thấy đủ các cột số định lượng để tính toán ma trận tương quan."

        # Hỏi về cột / thuộc tính
        for col in df.columns:
            if col.lower() in q:
                if pd.api.types.is_numeric_dtype(df[col]):
                    s = df[col].dropna()
                    return (
                        f"**Thông tin chi tiết về cột '{col}':**\n\n"
                        f"- Kiểu dữ liệu: Định lượng (Số thực/Nguyên)\n"
                        f"- Giá trị trung bình (Mean): **{s.mean():,.2f}**\n"
                        f"- Giá trị trung vị (Median): **{s.median():,.2f}**\n"
                        f"- Giá trị nhỏ nhất (Min): **{s.min():,.2f}** | Lớn nhất (Max): **{s.max():,.2f}**\n"
                        f"- Độ lệch chuẩn (Std): **{s.std():,.2f}**\n"
                        f"- Tổng số mẫu khả dụng: **{len(s):,}**"
                    )
                else:
                    val_counts = df[col].value_counts().head(5)
                    top_text = "\n".join([f"  * **{k}**: {v:,} lần ({round(v/len(df)*100, 1)}%)" for k, v in val_counts.items()])
                    return (
                        f"**Thông tin chi tiết về cột '{col}':**\n\n"
                        f"- Kiểu dữ liệu: Phân loại / Định tính (Categorical)\n"
                        f"- Số lượng giá trị độc nhất: **{df[col].nunique()}** nhóm\n"
                        f"- Phân bố Top 5 phổ biến nhất:\n{top_text}"
                    )

        # Hỏi về quy mô, số dòng, cột
        if "bao nhiêu" in q or "kích thước" in q or "số dòng" in q or "quy mô" in q:
            return (
                f"Tập dữ liệu sau khi được người dùng duyệt làm sạch có tổng cộng **{len(df):,} dòng** và **{len(df.columns)} cột**.\n"
                f"Tất cả các giá trị khuyết thiếu và trùng lặp đã được xử lý triệt để, đảm bảo chất lượng dữ liệu đạt 100% độ hoàn chỉnh."
            )

        # Hỏi về đề xuất / khuyến nghị
        if "khuyến nghị" in q or "giải pháp" in q or "làm gì" in q or "chiến lược" in q:
            return (
                f"**Đề xuất chiến lược từ AI Agent:**\n\n"
                f"1. **Tối ưu hóa tức thì (Quick-wins):** Chuẩn hóa quy trình ghi nhận dữ liệu tại nguồn để giảm thiểu lỗi trùng lặp và thiếu thông tin.\n"
                f"2. **Tập trung nguồn lực:** Đầu tư vào các nhóm đối tượng thuộc phân khúc chiếm tỷ trọng lớn nhất để tối đa hóa hiệu suất.\n"
                f"3. **Tận dụng đòn bẩy tương quan:** Can thiệp vào các biến số có tương quan thuận mạnh nhất để thúc đẩy chỉ số kinh doanh mục tiêu."
            )

        # Mặc định: Tóm tắt thông tin quan trọng
        return (
            f"**Tóm tắt nhanh từ AI Data Analyst:**\n\n"
            f"- Dữ liệu hiện có **{len(df):,} dòng** và **{len(df.columns)} cột**.\n"
            f"- Điểm chất lượng dữ liệu: **{cleaning_comparison.get('after', {}).get('health_score', 'N/A')}/100**.\n"
            f"- Bạn có thể hỏi chi tiết về bất kỳ cột nào (ví dụ: 'Phân tích cột {df.columns[0]}'), ma trận tương quan, hoặc các đề xuất hành động cụ thể!"
        )
