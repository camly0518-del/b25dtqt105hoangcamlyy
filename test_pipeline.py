"""
End-to-End Pipeline Verification Test
"""
import sys
from app.sample_data import generate_sample_ecommerce
from app.cleaner import DataCleaner
from app.eda import EDAEngine
from app.agent import DataAnalystAgent
from app.report_generator import ReportGenerator

def test_full_pipeline():
    print("[1] Sinh dữ liệu mẫu có lỗi thực tế...")
    df_raw = generate_sample_ecommerce()
    print(f"    Raw Shape: {df_raw.shape}")

    print("[2] Chẩn đoán dữ liệu (Diagnosis)...")
    cleaner = DataCleaner()
    diag = cleaner.diagnose(df_raw)
    print(f"    Health Score: {diag['summary']['health_score']}/100")
    print(f"    Proposals count: {len(diag['proposals'])}")

    print("[3] Người dùng duyệt và áp dụng làm sạch...")
    # Giả lập người dùng duyệt toàn bộ đề xuất
    approved_actions = diag['proposals']
    df_clean, comparison = cleaner.execute_approved_cleaning(df_raw, approved_actions)
    print(f"    Cleaned Shape: {df_clean.shape}")
    print(f"    New Health Score: {comparison['after']['health_score']}/100")
    print(f"    Audit Trail items: {len(comparison['audit_trail'])}")

    print("[4] Phân tích khám phá EDA...")
    eda_engine = EDAEngine()
    eda_data = eda_engine.run_eda(df_clean)
    print(f"    KPI cards count: {len(eda_data['kpi_cards'])}")
    print(f"    Charts generated: {list(eda_data['charts'].keys())}")

    print("[5] AI Agent tổng hợp Insight...")
    agent = DataAnalystAgent()
    insights = agent.generate_report_insights(eda_data, comparison)
    print(f"    Findings count: {len(insights.get('key_findings', []))}")
    print(f"    Executive Summary length: {len(insights.get('executive_summary', ''))}")

    print("[6] Sinh báo cáo HTML hoàn chỉnh...")
    report_gen = ReportGenerator()
    html = report_gen.generate_html_report("Doanh thu Bán lẻ & Thương mại Điện tử", df_clean, eda_data, comparison, insights)
    print(f"    HTML Report length: {len(html)} characters")
    
    assert len(html) > 1000
    assert "Báo Cáo Phân Tích Dữ Liệu Chuyên Sâu" in html
    assert "plotly-2.30.0.min.js" in html
    print("\n===> TOÀN BỘ QUY TRÌNH HOẠT ĐỘNG HOÀN HẢO 100%! <===")

if __name__ == "__main__":
    test_full_pipeline()
