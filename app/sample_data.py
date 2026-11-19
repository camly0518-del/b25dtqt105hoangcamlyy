"""
Sample Datasets with Realistic Dirty Data for Instant Testing
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

def generate_sample_ecommerce():
    """Tạo bộ dữ liệu Doanh thu & Bán lẻ Thương mại điện tử có lỗi thực tế"""
    np.random.seed(42)
    n_rows = 350

    order_ids = [f"ORD-{1000 + i}" for i in range(n_rows)]
    customers = [f"KH_{np.random.randint(100, 180)}" for _ in range(n_rows)]
    
    categories = ["Điện tử", "Thời trang", "Gia dụng", "Sách", "Làm đẹp"]
    cat_choices = np.random.choice(categories, size=n_rows, p=[0.25, 0.30, 0.20, 0.15, 0.10])
    
    cities = ["Hà Nội", "Hà Nội ", "TP. Hồ Chí Minh", "tp hồ chí minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng", None]
    city_choices = np.random.choice(cities, size=n_rows)
    
    base_date = datetime(2025, 1, 1)
    dates = [(base_date + timedelta(days=int(np.random.randint(0, 360)))).strftime("%Y-%m-%d") for _ in range(n_rows)]
    # Đôi khi date có định dạng dd/mm/yyyy hoặc chuỗi rác
    for i in range(15):
        idx = np.random.randint(0, n_rows)
        dates[idx] = (base_date + timedelta(days=idx)).strftime("%d/%m/%Y")
        
    quantities = np.random.randint(1, 12, size=n_rows)
    prices = np.random.choice([150000, 250000, 490000, 890000, 1500000, 3200000], size=n_rows)
    
    discounts = np.round(np.random.uniform(0.0, 0.35, size=n_rows), 2)
    
    # Tạo missing values có chủ đích
    ages = np.random.randint(18, 65, size=n_rows).astype(float)
    ages[np.random.choice(n_rows, size=35, replace=False)] = np.nan
    
    ratings = np.random.choice([1.0, 2.0, 3.0, 4.0, 5.0, np.nan], size=n_rows, p=[0.05, 0.08, 0.15, 0.35, 0.30, 0.07])
    
    df = pd.DataFrame({
        "Mã Đơn Hàng": order_ids,
        "Mã Khách Hàng": customers,
        "Tuổi KH": ages,
        "Khu Vực": city_choices,
        "Danh Mục": cat_choices,
        "Ngày Đặt": dates,
        "Số Lượng": quantities,
        "Đơn Giá (VNĐ)": prices,
        "Chiết Khấu (%)": discounts,
        "Đánh Giá": ratings
    })
    
    # Tính doanh thu
    df["Doanh Thu (VNĐ)"] = df["Số Lượng"] * df["Đơn Giá (VNĐ)"] * (1 - df["Chiết Khấu (%)"])
    # Thêm chi phí và lợi nhuận
    df["Lợi Nhuận (VNĐ)"] = df["Doanh Thu (VNĐ)"] * np.random.uniform(0.15, 0.45, size=n_rows)
    
    # Tạo giá trị ngoại lai (Outliers) cực đoan
    outlier_indices = [12, 45, 88, 142, 210]
    df.loc[outlier_indices[0], "Số Lượng"] = 250  # Số lượng bất thường
    df.loc[outlier_indices[1], "Đơn Giá (VNĐ)"] = 45000000  # Đơn giá đột biến
    df.loc[outlier_indices[2], "Doanh Thu (VNĐ)"] = 180000000  # Doanh thu cực lớn
    df.loc[outlier_indices[3], "Tuổi KH"] = 145  # Tuổi bất hợp lý
    df.loc[outlier_indices[4], "Chiết Khấu (%)"] = 1.8  # Chiết khấu > 100%
    
    # Tạo hàng trùng lặp (Duplicates)
    dup_rows = df.iloc[[5, 10, 15, 20, 25]].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    # Tạo cột vô nghĩa (Hằng số)
    df["Mã Quốc Gia"] = "VN"
    
    return df

def generate_sample_hr():
    """Tạo bộ dữ liệu Nhân sự & Nghỉ việc (HR Attrition)"""
    np.random.seed(101)
    n = 280
    
    departments = ["Kỹ thuật", "Kinh doanh", "Marketing", "Nhân sự", "Tài chính"]
    dept_choice = np.random.choice(departments, size=n, p=[0.35, 0.25, 0.15, 0.12, 0.13])
    
    salary = np.random.normal(22000000, 6000000, size=n).round(-5)
    salary[salary < 8000000] = 8000000
    
    years_exp = np.random.randint(1, 18, size=n).astype(float)
    satisfaction = np.random.choice([1, 2, 3, 4, 5, np.nan], size=n, p=[0.1, 0.15, 0.25, 0.35, 0.1, 0.05])
    overtime_hours = np.random.poisson(12, size=n)
    
    # Xác suất nghỉ việc dựa trên độ hài lòng và làm thêm giờ
    prob_leave = 0.1 + (overtime_hours > 18) * 0.3 - (satisfaction == 5) * 0.15
    prob_leave = np.clip(prob_leave, 0.05, 0.85)
    attrition = [np.random.choice(["Nghỉ việc", "Ở lại"], p=[p, 1-p]) for p in prob_leave]
    
    df = pd.DataFrame({
        "Mã Nhân Viên": [f"NV-{2000+i}" for i in range(n)],
        "Phòng Ban": dept_choice,
        "Năm Kinh Nghiệm": years_exp,
        "Lương Tháng (VNĐ)": salary,
        "Giờ Làm Thêm/Tháng": overtime_hours,
        "Mức Hài Lòng (1-5)": satisfaction,
        "Trạng Thái": attrition
    })
    
    # Missing values
    df.loc[np.random.choice(n, size=20, replace=False), "Lương Tháng (VNĐ)"] = np.nan
    df.loc[np.random.choice(n, size=15, replace=False), "Năm Kinh Nghiệm"] = np.nan
    
    # Outliers
    df.loc[5, "Lương Tháng (VNĐ)"] = 280000000 # Lương ngoại lai cực cao
    df.loc[18, "Giờ Làm Thêm/Tháng"] = 120 # Làm thêm bất thường
    
    # Duplicates
    df = pd.concat([df, df.iloc[[2, 8, 14]].copy()], ignore_index=True)
    return df

def generate_sample_finance():
    """Tạo bộ dữ liệu Rủi ro Tín dụng & Khách hàng Tài chính"""
    np.random.seed(202)
    n = 300
    
    income = np.random.lognormal(mean=16.8, sigma=0.5, size=n).round(-4)
    loan_amount = (income * np.random.uniform(1.2, 5.0, size=n)).round(-4)
    credit_score = np.random.normal(680, 75, size=n).round()
    credit_score = np.clip(credit_score, 300, 850)
    
    late_payments = np.random.poisson(0.8, size=n)
    risk_level = []
    for cs, lp in zip(credit_score, late_payments):
        if cs < 580 or lp >= 3:
            risk_level.append("Cao")
        elif cs < 680 or lp >= 1:
            risk_level.append("Trung bình")
        else:
            risk_level.append("Thấp")
            
    df = pd.DataFrame({
        "Mã Hồ Sơ": [f"HS-{5000+i}" for i in range(n)],
        "Thu Nhập Hàng Năm": income,
        "Số Tiền Vay": loan_amount,
        "Điểm Tín Dụng": credit_score,
        "Số Lần Trễ Hạn": late_payments,
        "Thời Gian Vay (Tháng)": np.random.choice([12, 24, 36, 48, 60], size=n),
        "Mức Độ Rủi Ro": risk_level
    })
    
    # Dirty elements
    df.loc[np.random.choice(n, size=25, replace=False), "Thu Nhập Hàng Năm"] = np.nan
    df.loc[np.random.choice(n, size=18, replace=False), "Điểm Tín Dụng"] = np.nan
    df.loc[8, "Số Tiền Vay"] = 15000000000 # Ngoại lai
    df = pd.concat([df, df.iloc[[7, 21, 35]].copy()], ignore_index=True)
    return df

def ensure_sample_files(save_dir=None):
    """Lưu sẵn các file mẫu để người dùng có thể tải hoặc dùng ngay (an toàn 100% trên Localhost & Vercel Serverless)"""
    import tempfile
    
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_datasets")
        
    try:
        os.makedirs(save_dir, exist_ok=True)
    except (OSError, PermissionError):
        save_dir = os.path.join(tempfile.gettempdir(), "sample_datasets")
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception:
            pass
    
    ecom_path = os.path.join(save_dir, "ecommerce_sales_raw.csv")
    hr_path = os.path.join(save_dir, "hr_attrition_raw.csv")
    fin_path = os.path.join(save_dir, "financial_risk_raw.csv")
    
    try:
        if not os.path.exists(ecom_path):
            generate_sample_ecommerce().to_csv(ecom_path, index=False, encoding="utf-8-sig")
        if not os.path.exists(hr_path):
            generate_sample_hr().to_csv(hr_path, index=False, encoding="utf-8-sig")
        if not os.path.exists(fin_path):
            generate_sample_finance().to_csv(fin_path, index=False, encoding="utf-8-sig")
    except Exception:
        # Nếu trên môi trường read-only không ghi được, hệ thống vẫn dùng in-memory dataframe hoàn toàn bình thường
        pass
        
    return {
        "ecommerce": ecom_path,
        "hr": hr_path,
        "finance": fin_path
    }
