"""
FastAPI Server & API Endpoints for NovaData AI Enterprise (NovaTech Intelligence)
"""
import os
import io
import json
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.sample_data import generate_sample_ecommerce, generate_sample_hr, generate_sample_finance, ensure_sample_files
from app.cleaner import DataCleaner
from app.eda import EDAEngine
from app.agent import DataAnalystAgent
from app.report_generator import ReportGenerator

app = FastAPI(title="NovaData AI Enterprise", description="Nền tảng Phân tích Dữ liệu Doanh nghiệp - NovaTech Intelligence")

# Mount static files and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Khởi tạo các module
cleaner = DataCleaner()
eda_engine = EDAEngine()
agent = DataAnalystAgent()
report_gen = ReportGenerator()

# Bộ nhớ trạng thái phiên làm việc (In-memory Session State)
session_state = {
    "dataset_name": "Chưa tải dữ liệu",
    "raw_df": None,
    "cleaned_df": None,
    "diagnosis": None,
    "cleaning_comparison": None,
    "eda_data": None,
    "insights": None,
    "html_report": None,
    "gemini_api_key": os.environ.get("GEMINI_API_KEY", "")
}

# Đảm bảo file mẫu có sẵn
sample_paths = ensure_sample_files()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Trang chủ ứng dụng"""
    context = {
        "request": request,
        "dataset_name": session_state["dataset_name"],
        "has_data": session_state["raw_df"] is not None,
        "is_cleaned": session_state["cleaned_df"] is not None,
        "has_api_key": bool(session_state["gemini_api_key"])
    }
    return templates.TemplateResponse(request=request, name="index.html", context=context)

@app.get("/api/samples")
async def list_samples():
    """Danh sách các tập dữ liệu báo cáo kinh doanh mẫu chuẩn doanh nghiệp"""
    return [
        {
            "id": "ecommerce",
            "name": "Báo Cáo Doanh Thu & Thương Mại (Sales Report)",
            "desc": "Dữ liệu đơn hàng, doanh thu, lợi nhuận gộp, tỷ lệ chiết khấu và tuổi khách hàng (chứa lỗi khuyết, trùng lặp và ngoại lai thực tế).",
            "badge": "Khuyên dùng",
            "icon": "fa-chart-line"
        },
        {
            "id": "hr",
            "name": "Báo Cáo Nhân Sự & Hiệu Suất (HR Analytics)",
            "desc": "Dữ liệu nhân viên, kinh nghiệm, thang bảng lương, giờ làm thêm, mức độ hài lòng và tỷ lệ biến động nhân sự.",
            "badge": "Nhân sự",
            "icon": "fa-users"
        },
        {
            "id": "finance",
            "name": "Báo Cáo Tài Chính & Rủi Ro Tín Dụng (Financial Risk)",
            "desc": "Dữ liệu hồ sơ tài chính, quy mô vốn vay, thu nhập, điểm xếp hạng tín dụng và phân loại rủi ro doanh nghiệp.",
            "badge": "Tài chính",
            "icon": "fa-wallet"
        }
    ]

@app.post("/api/load-sample/{sample_id}")
async def load_sample(sample_id: str):
    """Tải bộ dữ liệu mẫu nhanh"""
    if sample_id == "ecommerce":
        df = generate_sample_ecommerce()
        name = "Doanh thu Bán lẻ & Thương mại Điện tử"
    elif sample_id == "hr":
        df = generate_sample_hr()
        name = "Nhân sự & Tỷ lệ Nghỉ việc"
    elif sample_id == "finance":
        df = generate_sample_finance()
        name = "Tín dụng & Đánh giá Rủi ro"
    else:
        raise HTTPException(status_code=404, detail="Không tìm thấy tập dữ liệu mẫu")

    session_state["raw_df"] = df
    session_state["cleaned_df"] = None
    session_state["dataset_name"] = name
    session_state["diagnosis"] = None
    session_state["cleaning_comparison"] = None
    session_state["eda_data"] = None
    session_state["insights"] = None
    session_state["html_report"] = None

    # Tự động chẩn đoán luôn
    diag = cleaner.diagnose(df)
    session_state["diagnosis"] = diag

    # Trả về toàn bộ dữ liệu của bảng (100% dòng) kèm kiểu dữ liệu từng cột
    records = df.fillna("").to_dict(orient="records")
    dtypes = {col: str(df[col].dtype) for col in df.columns}

    return {
        "status": "success",
        "dataset_name": name,
        "rows": len(df),
        "cols": len(df.columns),
        "columns": df.columns.tolist(),
        "dtypes": dtypes,
        "preview": records,
        "all_data": records,
        "diagnosis": diag
    }

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Tải lên file dữ liệu người dùng (CSV, Excel, JSON)"""
    contents = await file.read()
    filename = file.filename
    
    try:
        fname = filename.lower()
        if fname.endswith(".csv"):
            for enc in ["utf-8", "utf-8-sig", "latin1", "cp1252", "windows-1258"]:
                try:
                    df = pd.read_csv(io.BytesIO(contents), encoding=enc)
                    break
                except Exception:
                    continue
            else:
                df = pd.read_csv(io.BytesIO(contents), encoding="utf-8", errors="replace")
        elif fname.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(contents))
        elif fname.endswith(".json"):
            try:
                df = pd.read_json(io.BytesIO(contents))
            except Exception:
                data = json.loads(contents.decode("utf-8", errors="replace"))
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
                            df = pd.DataFrame(v)
                            break
                    else:
                        df = pd.DataFrame([data])
                else:
                    raise ValueError("Cấu trúc JSON không hợp lệ để tạo bảng dữ liệu")
        else:
            raise HTTPException(status_code=400, detail="Định dạng file không hỗ trợ. Vui lòng tải lên CSV, Excel (.xlsx, .xls) hoặc JSON.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Không thể đọc file: {str(e)}")

    if len(df) == 0:
        raise HTTPException(status_code=400, detail="File dữ liệu trống rỗng!")

    session_state["raw_df"] = df
    session_state["cleaned_df"] = None
    session_state["dataset_name"] = filename
    session_state["diagnosis"] = None
    session_state["cleaning_comparison"] = None
    session_state["eda_data"] = None
    session_state["insights"] = None
    session_state["html_report"] = None

    # Chẩn đoán ngay
    diag = cleaner.diagnose(df)
    session_state["diagnosis"] = diag

    records = df.fillna("").to_dict(orient="records")
    dtypes = {col: str(df[col].dtype) for col in df.columns}

    return {
        "status": "success",
        "dataset_name": filename,
        "rows": len(df),
        "cols": len(df.columns),
        "columns": df.columns.tolist(),
        "dtypes": dtypes,
        "preview": records,
        "all_data": records,
        "diagnosis": diag
    }

@app.get("/api/diagnose")
async def get_diagnosis():
    """Lấy kết quả chẩn đoán chất lượng dữ liệu và danh sách đề xuất làm sạch"""
    df = session_state.get("raw_df")
    if df is None:
        raise HTTPException(status_code=400, detail="Chưa có dữ liệu nào được nạp.")

    if session_state.get("diagnosis") is None:
        session_state["diagnosis"] = cleaner.diagnose(df)

    return {
        "status": "success",
        "dataset_name": session_state["dataset_name"],
        "diagnosis": session_state["diagnosis"]
    }

class ApprovedActionsPayload(BaseModel):
    actions: List[Dict[str, Any]]

@app.post("/api/clean/approve")
async def approve_and_clean(payload: ApprovedActionsPayload):
    """
    Điểm cốt lõi: Người dùng duyệt danh sách đề xuất làm sạch và hệ thống thực thi
    """
    raw_df = session_state.get("raw_df")
    if raw_df is None:
        raise HTTPException(status_code=400, detail="Chưa có dữ liệu thô để làm sạch.")

    approved_actions = payload.actions
    cleaned_df, comparison = cleaner.execute_approved_cleaning(raw_df, approved_actions)

    session_state["cleaned_df"] = cleaned_df
    session_state["cleaning_comparison"] = comparison

    cleaned_records = cleaned_df.fillna("").to_dict(orient="records")

    return {
        "status": "success",
        "message": f"Đã áp dụng thành công {len(comparison['audit_trail'])} hành động làm sạch theo phê duyệt!",
        "comparison": comparison,
        "preview": cleaned_records,
        "all_data": cleaned_records,
        "columns": cleaned_df.columns.tolist()
    }

@app.post("/api/analyze")
async def run_analysis():
    """
    Chạy toàn bộ quy trình EDA và AI Agent tổng hợp Insight sau khi dữ liệu đã được làm sạch
    """
    df = session_state.get("cleaned_df")
    if df is None:
        df = session_state.get("raw_df")
        if df is None:
            raise HTTPException(status_code=400, detail="Chưa có dữ liệu để phân tích.")
        # Nếu chưa duyệt, thực thi chẩn đoán mặc định
        diag = cleaner.diagnose(df)
        df, comp = cleaner.execute_approved_cleaning(df, diag["proposals"])
        session_state["cleaned_df"] = df
        session_state["cleaning_comparison"] = comp

    comp = session_state.get("cleaning_comparison", {
        "before": {"rows": len(df), "cols": len(df.columns), "health_score": 75},
        "after": {"rows": len(df), "cols": len(df.columns), "health_score": 98},
        "audit_trail": []
    })

    # 1. Chạy EDA
    eda_data = eda_engine.run_eda(df)
    session_state["eda_data"] = eda_data

    # 2. Chạy AI Agent sinh Insights
    insights = agent.generate_report_insights(eda_data, comp)
    session_state["insights"] = insights

    # 3. Tạo sẵn Báo cáo HTML hoàn chỉnh
    html_report = report_gen.generate_html_report(
        session_state["dataset_name"],
        df,
        eda_data,
        comp,
        insights
    )
    session_state["html_report"] = html_report

    return {
        "status": "success",
        "summary": eda_data["summary"],
        "kpi_cards": eda_data["kpi_cards"],
        "charts": eda_data["charts"],
        "insights": insights,
        "comparison": comp
    }

class ChatPayload(BaseModel):
    message: str

@app.post("/api/agent/chat")
async def chat_with_agent(payload: ChatPayload):
    """Tương tác hỏi đáp trực tiếp với AI Data Analyst về tập dữ liệu"""
    df = session_state.get("cleaned_df")
    if df is None:
        df = session_state.get("raw_df")
    if df is None:
        return {"reply": "Vui lòng nạp và duyệt làm sạch dữ liệu trước khi trò chuyện với AI Agent."}

    eda_data = session_state.get("eda_data") or eda_engine.run_eda(df)
    comp = session_state.get("cleaning_comparison") or {}

    reply = agent.chat_answer(payload.message, df, eda_data, comp)
    return {"reply": reply}

@app.get("/api/report/html", response_class=HTMLResponse)
async def view_html_report():
    """Xem trực tiếp báo cáo HTML trên giao diện (trong iframe hoặc container)"""
    html = session_state.get("html_report")
    if not html:
        # Nếu chưa tạo, thử tạo nếu đã có dữ liệu
        df = session_state.get("cleaned_df")
        if df is None:
            df = session_state.get("raw_df")
        if df is not None:
            eda_data = session_state.get("eda_data")
            if eda_data is None:
                eda_data = eda_engine.run_eda(df)
            comp = session_state.get("cleaning_comparison") or {
                "before": {"rows": len(df), "cols": len(df.columns), "health_score": 70},
                "after": {"rows": len(df), "cols": len(df.columns), "health_score": 95},
                "audit_trail": []
            }
            insights = session_state.get("insights") or agent.generate_report_insights(eda_data, comp)
            html = report_gen.generate_html_report(session_state["dataset_name"], df, eda_data, comp, insights)
            session_state["html_report"] = html
        else:
            return HTMLResponse(content="<div style='font-family:sans-serif;text-align:center;padding:50px;color:#64748b;'><h3>Chưa có báo cáo nào được khởi tạo</h3><p>Vui lòng tải dữ liệu và tiến hành phân tích.</p></div>")

    return HTMLResponse(content=html)

def get_safe_ascii_name(name: str) -> str:
    """Loại bỏ ký tự có dấu để đảm bảo tương thích HTTP Header ASCII chuẩn 100%"""
    import unicodedata
    import re
    name = name.replace('Đ', 'D').replace('đ', 'd')
    nfkd = unicodedata.normalize('NFKD', name)
    ascii_str = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    ascii_str = ascii_str.encode('ascii', 'ignore').decode('ascii')
    ascii_str = re.sub(r'[^\w\s-]', '', ascii_str).strip().replace(' ', '_')
    return ascii_str or "dataset"

@app.get("/api/report/download")
async def download_html_report():
    """Tải xuống file báo cáo HTML độc lập"""
    html = session_state.get("html_report")
    if not html:
        raise HTTPException(status_code=400, detail="Chưa có báo cáo nào để tải về.")

    safe_name = get_safe_ascii_name(session_state['dataset_name'])
    filename = f"Bao_Cao_AI_{safe_name}.html"
    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@app.get("/api/data/download-clean")
async def download_cleaned_data():
    """Tải xuống file dữ liệu đã được làm sạch và người dùng duyệt (.csv)"""
    df = session_state.get("cleaned_df")
    if df is None:
        raise HTTPException(status_code=400, detail="Chưa có dữ liệu đã làm sạch để tải về.")

    stream = io.StringIO()
    df.to_csv(stream, index=False, encoding="utf-8-sig")
    safe_name = get_safe_ascii_name(session_state['dataset_name'])
    filename = f"Cleaned_{safe_name}.csv"

    return Response(
        content=stream.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

class SettingsPayload(BaseModel):
    api_key: str

@app.post("/api/settings/apikey")
async def update_api_key(payload: SettingsPayload):
    """Cập nhật Gemini API Key cho AI Agent"""
    key = payload.api_key.strip()
    session_state["gemini_api_key"] = key
    agent.set_api_key(key)
    return {
        "status": "success",
        "message": "Đã lưu cài đặt API Key thành công!",
        "has_api_key": bool(key)
    }
