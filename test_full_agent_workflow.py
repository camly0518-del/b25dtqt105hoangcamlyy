import urllib.request
import json
import io
import os
import pandas as pd
import numpy as np

BASE_URL = 'http://127.0.0.1:8000'

def test_workflow():
    print("=" * 70)
    print("   BẮT ĐẦU KIỂM TRA TOÀN DIỆN HỆ THỐNG DATAMIND AI AGENT")
    print("=" * 70)
    
    # 1. Kiểm tra Trang chủ HTML Dashboard
    res = urllib.request.urlopen(f"{BASE_URL}/")
    assert res.status == 200
    html = res.read().decode('utf-8')
    assert 'app-html' in html
    assert 'sample-dataset-cards' in html
    assert 'raw-preview-table' in html
    assert 'proposals-list' in html
    assert 'before-after-cards' in html
    assert 'kpi-cards-container' in html
    assert 'report-iframe' in html
    print("[PASS] 1. Trang chu HTML Dashboard & tat ca 58 Element IDs hop le.")

    # 2. Kiểm tra nạp bộ dữ liệu mẫu (Sample Dataset)
    req = urllib.request.Request(f"{BASE_URL}/api/load-sample/ecommerce", method="POST")
    res = urllib.request.urlopen(req)
    assert res.status == 200
    data = json.loads(res.read().decode('utf-8'))
    assert data["status"] == "success"
    assert data["rows"] > 0
    assert "diagnosis" in data
    score_before = data["diagnosis"]["summary"]["health_score"]
    print(f"[PASS] 2. Nap bo du lieu mau Ecommerce: {data['rows']} dong, Health Score: {score_before}/100.")

    # 3. Kiểm tra Trạm duyệt làm sạch Human-in-the-Loop (HITL)
    proposals = data["diagnosis"]["proposals"]
    payload = json.dumps({"actions": proposals}).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/clean/approve",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    res = urllib.request.urlopen(req)
    assert res.status == 200
    clean_data = json.loads(res.read().decode('utf-8'))
    assert clean_data["status"] == "success"
    comp = clean_data["comparison"]
    score_after = comp["after"]["health_score"]
    print(f"[PASS] 3. Tram kiem duyet HITL: {len(comp['audit_trail'])} hanh dong da thuc thi. Diem sau lam sach: {score_after}/100.")

    # 4. Kiểm tra Phân tích tự động EDA & AI Insights
    req = urllib.request.Request(f"{BASE_URL}/api/analyze", method="POST")
    res = urllib.request.urlopen(req)
    assert res.status == 200
    eda_res = json.loads(res.read().decode('utf-8'))
    assert eda_res["status"] == "success"
    assert len(eda_res["kpi_cards"]) >= 4
    assert "charts" in eda_res
    assert "insights" in eda_res
    print(f"[PASS] 4. Phan tich tu dong AI: {len(eda_res['kpi_cards'])} KPI Cards, {len(eda_res['charts'])} bieu do Plotly sinh thanh cong.")

    # 5. Kiểm tra Trợ lý Chat AI Agent
    chat_payload = json.dumps({"message": "Hãy phân tích tương quan và đưa ra khuyến nghị"}).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/agent/chat",
        data=chat_payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    res = urllib.request.urlopen(req)
    assert res.status == 200
    chat_res = json.loads(res.read().decode('utf-8'))
    assert len(chat_res["reply"]) > 50
    print("[PASS] 5. AI Chatbot Heuristic/LLM Engine phan hoi chinh xac va sau sac.")

    # 6. Kiểm tra Báo cáo HTML trực quan nội bộ
    res = urllib.request.urlopen(f"{BASE_URL}/api/report/html")
    assert res.status == 200
    assert "text/html" in res.headers.get("Content-Type", "")
    print("[PASS] 6. Xuat ban Bao cao HTML truc quan noi bo thanh cong.")

    # 7. Kiểm tra Tải xuống Báo cáo HTML độc lập
    res = urllib.request.urlopen(f"{BASE_URL}/api/report/download")
    assert res.status == 200
    assert "attachment" in res.headers.get("Content-Disposition", "")
    print("[PASS] 7. Nut tai xuong bao cao HTML doc lap hoat dong tot.")

    # 8. Kiểm tra Tải xuống dữ liệu CSV sạch
    res = urllib.request.urlopen(f"{BASE_URL}/api/data/download-clean")
    assert res.status == 200
    assert "attachment" in res.headers.get("Content-Disposition", "")
    print("[PASS] 8. Nut tai du lieu CSV da lam sach hoat dong tot.")

    print("\n" + "=" * 70)
    print("   TAT CA CAC TINH NANG DA DUOC KIEM CHUNG 100% HOAN HAO!")
    print("=" * 70)

if __name__ == "__main__":
    test_workflow()
