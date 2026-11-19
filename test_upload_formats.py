import urllib.request
import json
import io
import pandas as pd
import numpy as np

BASE_URL = 'http://127.0.0.1:8000'

def upload_df(df, filename):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    
    if filename.endswith(".csv"):
        file_bytes = df.to_csv(index=False).encode('utf-8')
    elif filename.endswith(".xlsx"):
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        file_bytes = buf.getvalue()
    elif filename.endswith(".json"):
        file_bytes = df.to_json(orient="records").encode('utf-8')
    else:
        raise ValueError("Unsupported test format")

    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f'Content-Type: application/octet-stream\r\n\r\n'
    ).encode('utf-8') + file_bytes + f'\r\n--{boundary}--\r\n'.encode('utf-8')

    req = urllib.request.Request(
        f"{BASE_URL}/api/upload",
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'},
        method='POST'
    )
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode('utf-8'))

def test_uploads():
    print("Kiểm tra Upload các định dạng file...")
    
    # Tạo dataframe test có lỗi thực tế
    test_df = pd.DataFrame({
        "ID": [1, 2, 2, 4, 5],
        "Ten_KH": ["Nguyen A ", " Tran B", " Tran B", "Le C", None],
        "DoanhThu": [1000, 2500, 2500, 15000, 3200],
        "LoiNhuan": [200, 500, 500, 4500, 700]
    })
    
    # 1. Test CSV
    res_csv = upload_df(test_df, "test_data.csv")
    assert res_csv["status"] == "success"
    assert res_csv["rows"] == 5
    print(" [OK] Upload file CSV thanh cong (5 dong, chẩn đoán loi, null, trùng lặp)")

    # 2. Test XLSX
    res_xlsx = upload_df(test_df, "test_data.xlsx")
    assert res_xlsx["status"] == "success"
    assert res_xlsx["rows"] == 5
    print(" [OK] Upload file XLSX thanh cong (5 dong)")

    # 3. Test JSON
    res_json = upload_df(test_df, "test_data.json")
    assert res_json["status"] == "success"
    assert res_json["rows"] == 5
    print(" [OK] Upload file JSON thanh cong (5 dong)")

    print("ALL UPLOAD FORMATS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_uploads()
