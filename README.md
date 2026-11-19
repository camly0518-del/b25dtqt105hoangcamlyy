# 🧠 DataMind AI Agent - Hệ Thống Phân Tích Dữ Liệu Toàn Diện & Kiểm Định Human-in-the-Loop

**DataMind AI Agent** là một công cụ AI Agent phân tích dữ liệu chuyên sâu, tự động hóa toàn bộ quy trình từ khâu nạp dữ liệu thô, quét chẩn đoán chất lượng, **trả kết quả đề xuất để người dùng kiểm duyệt (Human-in-the-Loop)** trước khi xử lý, thực hiện phân tích khám phá (EDA) đa biến, tương tác hỏi đáp với AI và **xuất báo cáo HTML trực tiếp ngay trên giao diện**.

---

## 🌟 Các Tính Năng Nổi Bật

### 1. Quy Trình 4 Bước Chuẩn Hóa & Tối Ưu UX
* **Bước 1: Nạp & Quét Dữ Liệu (Data Ingestion)**
  - Hỗ trợ tải lên file định dạng `.csv`, `.xlsx`, `.xls`, `.json`.
  - Tích hợp sẵn **3 bộ dữ liệu mẫu thực tế** (Bán lẻ E-Commerce, Nhân sự & Nghỉ việc HR, Rủi ro Tín dụng Tài chính) chứa các lỗi thực tế (khuyết thiếu, trùng lặp, ngoại lai, định dạng chuỗi lộn xộn) để thử nghiệm tức thì chỉ với 1 click.
  - Xem trước dữ liệu thô (10 dòng đầu) cùng thống kê quy mô ban đầu.

* **Bước 2: AI Chẩn Đoán & Người Dùng Phê Duyệt Làm Sạch (Human-in-the-Loop Approval)**
  - **Quét toàn diện chất lượng dữ liệu**: Đo lường điểm sức khỏe (Data Health Score 0 - 100%), tỷ lệ ô trống, số dòng trùng lặp, ngoại lai theo thuật toán IQR & 3-Sigma Z-Score, lỗi định dạng ngày tháng và khoảng trắng.
  - **Bảng đề xuất làm sạch tương tác (Proposal Checklist)**: AI Agent lập kế hoạch chi tiết cho từng cột/lỗi. Người dùng có **toàn quyền kiểm duyệt**:
    - Bật/tắt duyệt từng hành động cụ thể.
    - Tùy chỉnh phương pháp thực thi: Điền Median / Mean / Mode / Xóa dòng; Cắt biên IQR (Winsorizing) / Xóa ngoại lai; Chuẩn hóa chuỗi (Trim, Title case); Chuyển đổi Datetime chuẩn.
    - Dự báo phạm vi tác động (số ô/dòng bị ảnh hưởng).
  - **Nút "Duyệt & Áp dụng Làm sạch"**: Thực thi các quy tắc đã được phê duyệt, lưu vết **Nhật ký biến đổi (Audit Trail)**.
  - **So sánh Trước vs Sau trực quan**: Bảng so sánh chỉ số trước & sau (số dòng, số trùng lặp đã xóa, số ô khuyết đã điền, điểm sức khỏe tăng vọt) cùng bảng dữ liệu sạch và nút tải `.csv` sạch.

* **Bước 3: Khám Phá EDA Tự Động & Trợ Lý AI Agent**
  - **KPI Cards tổng hợp**: Quy mô bản ghi, số biến định lượng, số biến phân loại, cặp tương quan mạnh nhất.
  - **Hệ thống biểu đồ tương tác Plotly**:
    - Ma trận nhiệt tương quan Pearson (Correlation Heatmap).
    - Phân phối tần suất & biểu đồ hộp ngoại lai (Histogram & Marginal Boxplot).
    - Cơ cấu phân khúc (Categorical Breakdown Bar Chart).
    - Mối quan hệ tương quan cốt lõi (Scatter Relationship Plot).
    - Xu hướng thời gian (Time-series Trend Line Chart nếu có cột ngày tháng).
  - **AI Agent Chatbot tương tác**: Hỏi đáp tự do về dữ liệu (ví dụ: *"Cột nào tương quan mạnh nhất?"*, *"Phân tích doanh thu theo khu vực"*, *"3 giải pháp chiến lược là gì?"*).

* **Bước 4: Báo Cáo HTML Trực Tiếp Trên Giao Diện & Xuất Bản (Live HTML Report)**
  - **Xem trực tiếp trên giao diện**: Báo cáo được render nguyên bản trong khung xem tương tác mượt mà, đầy đủ biểu đồ Plotly, tóm tắt điều hành, chứng nhận làm sạch và phụ lục thống kê.
  - **Nút "Tải Báo Cáo (.HTML)"**: Tải về file HTML độc lập (standalone), có thể mở trên mọi trình duyệt ngoại tuyến mà không cần server.
  - **Nút "In / Xuất PDF"**: Tích hợp CSS in ấn chuyên nghiệp, tự động căn chỉnh ngắt trang A4 chuẩn.
  - **Nút "Mở Tab Mới"**: Xem toàn màn hình báo cáo.

---

## 🤖 Động Cơ AI Agent Kép (Dual-Engine AI)
1. **Bộ Suy Luận Thống Kê Nội Bộ (Heuristic Statistical Reasoning Engine)**:
   - Tích hợp sẵn 100%, hoạt động tức thì **hoàn toàn offline/local** mà không cần bất kỳ API key nào.
   - Tự động phân tích các mối tương quan mạnh nhất, chỉ số biến thiên, độ lệch phân phối (skewness), bất thường và đề xuất lộ trình hành động 3 giai đoạn (Ngắn hạn / Trung hạn / Dài hạn).
2. **Bộ Tăng Cường Google Gemini LLM (Tùy chọn)**:
   - Nếu bạn có Gemini API Key, chỉ cần nhấn nút **"Cài đặt Gemini"** trên thanh tiêu đề để nhập khóa. AI Agent sẽ tự động kết nối API để nâng tầm báo cáo điều hành và trả lời các câu hỏi phức tạp bằng ngôn ngữ tự nhiên.

---

## 📁 Cấu Trúc Thư Mục Dự Án

```
AI Agent Cuối Môn/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI server & REST API endpoints
│   ├── cleaner.py           # Bộ chẩn đoán & thực thi làm sạch theo phê duyệt
│   ├── eda.py               # Phân tích thống kê & sinh biểu đồ tương tác Plotly
│   ├── agent.py             # Lõi AI Agent (Heuristic NLP + Gemini LLM bridge)
│   ├── report_generator.py  # Bộ sinh báo cáo HTML trực tiếp & độc lập
│   ├── sample_data.py       # Trình tạo 3 bộ dữ liệu mẫu thực tế có lỗi
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Giao diện tùy chỉnh, Stepper & Animations
│   │   └── js/
│   │       └── app.js       # Logic điều khiển luồng, phê duyệt, chat & preview
│   └── templates/
│       └── index.html       # Giao diện Single-Page Application (Tailwind CSS)
├── sample_datasets/         # Thư mục lưu các file CSV mẫu
├── run.bat                  # File khởi động 1-click cho Windows
├── start.py                 # File Python khởi chạy server & tự mở trình duyệt
├── test_pipeline.py         # Kiểm thử tự động End-to-End toàn bộ quy trình
├── requirements.txt         # Danh sách thư viện phụ thuộc
└── README.md                # Tài liệu hướng dẫn sử dụng chi tiết
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy

### Cách 1: Khởi Chạy Nhanh (Windows 1-Click)
Chỉ cần nhấp đúp chuột vào file:
```cmd
run.bat
```
Hệ thống sẽ khởi động máy chủ và tự động mở trình duyệt tại địa chỉ: `http://localhost:8000`.

### Cách 2: Khởi Chạy Bằng Lệnh Python
Mở terminal trong thư mục dự án và chạy:
```bash
# 1. Cài đặt các thư viện cần thiết (nếu chưa có)
pip install -r requirements.txt

# 2. Khởi chạy ứng dụng
python start.py
```

---

## 🧪 Chạy Kiểm Thử Toàn Trình (Pipeline Verification)
Để kiểm tra tính toàn vẹn của mọi module:
```bash
python test_pipeline.py
```
Kết quả kiểm thử sẽ hiển thị:
```text
[1] Sinh dữ liệu mẫu có lỗi thực tế... Raw Shape: (355, 13)
[2] Chẩn đoán dữ liệu (Diagnosis)... Health Score: 67.7/100
[3] Người dùng duyệt và áp dụng làm sạch... Cleaned Shape: (350, 12), New Health Score: 100.0/100
[4] Phân tích khám phá EDA... KPI cards: 4, Charts: 5
[5] AI Agent tổng hợp Insight... Findings: 3
[6] Sinh báo cáo HTML hoàn chỉnh... HTML Report: 106,050 characters
===> TOÀN BỘ QUY TRÌNH HOẠT ĐỘNG HOÀN HẢO 100%! <===
```

---

## 📋 Hướng Dẫn Sử Dụng Chi Tiết Trên Giao Diện

1. **Bước 1: Nạp Dữ Liệu**:
   - Chọn 1 trong 3 nút dữ liệu mẫu (ví dụ: *Bán lẻ & Thương mại Điện tử*) hoặc kéo thả file CSV/Excel của bạn vào ô tải lên.
   - Bảng xem trước 10 dòng đầu sẽ xuất hiện. Nhấn **"Tiếp tục: Duyệt Làm Sạch"**.
2. **Bước 2: Duyệt Làm Sạch Dữ Liệu**:
   - Xem điểm sức khỏe ban đầu và các lỗi phát hiện (trùng lặp, ô trống, ngoại lai).
   - Kiểm tra **Bảng Phê Duyệt Kế Hoạch Làm Sạch**: tích chọn các mục bạn đồng ý xử lý và chọn phương pháp mong muốn ở ô lựa chọn.
   - Nhấn nút xanh: **"Duyệt & Áp Dụng Làm Sạch Ngay"**.
   - Xem bảng so sánh Trước vs Sau và bảng dữ liệu sạch. Nhấn **"Bước 3: Khám Phá AI & EDA"**.
3. **Bước 3: Phân Tích & AI Chat**:
   - Khám phá các thẻ KPI và biểu đồ tương tác Plotly (zoom in/out, hover).
   - Tại khung chat ở dưới, nhập câu hỏi để trò chuyện với AI Agent hoặc bấm vào các nút câu hỏi gợi ý. Nhấn **"Bước 4: Báo Cáo HTML Trực Tiếp"**.
4. **Bước 4: Báo Cáo HTML Trực Tiếp**:
   - Xem toàn bộ báo cáo hoàn chỉnh được nhúng trực tiếp ngay trên màn hình.
   - Nhấn **"Tải Báo Cáo (.HTML)"** để lưu trữ offline.
   - Nhấn **"In / Xuất PDF"** để in hoặc lưu thành file PDF sắc nét.
