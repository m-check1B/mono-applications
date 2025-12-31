from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


BACKEND_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BACKEND_ROOT / "templates"
DATA_DIR = BACKEND_ROOT / "data"
STATIC_DIR = BACKEND_ROOT / "static"

DATA_DIR.mkdir(exist_ok=True, parents=True)
STATIC_DIR.mkdir(exist_ok=True, parents=True)

app = FastAPI(
    title="AI Readiness Tests",
    description="Stack-2026 compatible AI readiness test backend",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# CORS for SvelteKit dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5177",
        "http://127.0.0.1:5177",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _write_csv_row(path: Path, header: List[str], row: Dict[str, str]) -> None:
    import csv

    file_exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


@app.get("/health")
async def health_check() -> Dict[str, str]:
    return {
        "status": "healthy",
        "service": "impact-tests",
        "version": "0.1.0",
    }


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/business", response_class=HTMLResponse)
async def business_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("business_test.html", {"request": request})


@app.post("/business", response_class=HTMLResponse)
async def business_post(
    request: Request,
    company_name: str = Form(...),
    website: str = Form(""),
    country: str = Form(""),
    industry: str = Form(""),
    employees: str = Form(""),
    contact_name: str = Form(...),
    contact_role: str = Form(""),
    email: str = Form(...),
    consent_marketing: bool = Form(False),
    priority_sales: bool = Form(False),
    priority_support: bool = Form(False),
    priority_operations: bool = Form(False),
    priority_finance: bool = Form(False),
    priority_hr: bool = Form(False),
    q1: int = Form(...),
    q2: int = Form(...),
    q3: int = Form(...),
    q4: int = Form(...),
    q5: int = Form(...),
    q6: int = Form(...),
    q7: int = Form(...),
    q8: int = Form(...),
    q9: int = Form(...),
    q10: int = Form(...),
    q11: int = Form(...),
    q12: int = Form(...),
) -> HTMLResponse:
    scores = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12]
    total = sum(scores)

    if total <= 29:
        bucket = "low"
        title = "Low AI Readiness – Big Upside if You Start Structured"
        recommendation = "AI Impact Audit (primary) + optional intro training."
    elif total <= 44:
        bucket = "medium"
        title = "Medium AI Readiness – Time to Consolidate and Train"
        recommendation = "AI Impact Staff Training + focused implementation on 2–3 workflows."
    else:
        bucket = "high"
        title = "High AI Readiness – Ready to Turn AI into Revenue"
        recommendation = "AI Sales in Practice (build outbound/inside-sales machine) and portfolio deployment."

    priorities = []
    if priority_sales:
        priorities.append("sales")
    if priority_support:
        priorities.append("support")
    if priority_operations:
        priorities.append("operations")
    if priority_finance:
        priorities.append("finance")
    if priority_hr:
        priorities.append("hr")

    csv_path = DATA_DIR / "business_results.csv"
    header = [
        "timestamp",
        "company_name",
        "website",
        "country",
        "industry",
        "employees",
        "contact_name",
        "contact_role",
        "email",
        "consent_marketing",
        "priorities",
        "q1",
        "q2",
        "q3",
        "q4",
        "q5",
        "q6",
        "q7",
        "q8",
        "q9",
        "q10",
        "q11",
        "q12",
        "total_score",
        "bucket",
        "recommendation",
    ]
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "company_name": company_name,
        "website": website,
        "country": country,
        "industry": industry,
        "employees": employees,
        "contact_name": contact_name,
        "contact_role": contact_role,
        "email": email,
        "consent_marketing": "yes" if consent_marketing else "no",
        "priorities": ",".join(priorities),
        "q1": str(q1),
        "q2": str(q2),
        "q3": str(q3),
        "q4": str(q4),
        "q5": str(q5),
        "q6": str(q6),
        "q7": str(q7),
        "q8": str(q8),
        "q9": str(q9),
        "q10": str(q10),
        "q11": str(q11),
        "q12": str(q12),
        "total_score": str(total),
        "bucket": bucket,
        "recommendation": recommendation,
    }
    _write_csv_row(csv_path, header, row)

    return templates.TemplateResponse(
        "business_result.html",
        {
            "request": request,
            "company_name": company_name,
            "total_score": total,
            "bucket": bucket,
            "title": title,
            "recommendation": recommendation,
            "priorities": priorities,
        },
    )


@app.get("/human", response_class=HTMLResponse)
async def human_get(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("human_test.html", {"request": request})


@app.post("/human", response_class=HTMLResponse)
async def human_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    country: str = Form(""),
    city: str = Form(""),
    role: str = Form(""),
    languages: str = Form(""),
    interest_operations: bool = Form(False),
    interest_sales: bool = Form(False),
    interest_marketing: bool = Form(False),
    interest_tech: bool = Form(False),
    interest_other: bool = Form(False),
    consent_marketing: bool = Form(False),
    hq1: int = Form(...),
    hq2: int = Form(...),
    hq3: int = Form(...),
    hq4: int = Form(...),
    hq5: int = Form(...),
    hq6: int = Form(...),
    hq7: int = Form(...),
    hq8: int = Form(...),
    hq9: int = Form(...),
    hq10: int = Form(...),
) -> HTMLResponse:
    scores = [hq1, hq2, hq3, hq4, hq5, hq6, hq7, hq8, hq9, hq10]
    total = sum(scores)

    if total <= 24:
        bucket = "low"
        title = "Early in AI – Great Time to Build Foundations"
        recommendation = "Foundations of AI in Work training (daily usage, prompts, basic tools)."
    elif total <= 37:
        bucket = "medium"
        title = "Solid AI Readiness – Time to Specialize"
        recommendation = "Choose AI Operator / Implementation or AI Sales Support track."
    else:
        bucket = "high"
        title = "High AI Readiness – Ready for Real Projects"
        recommendation = "Consider AI Sales in Practice / SDR-like role or implementation lead on client projects."

    interests = []
    if interest_operations:
        interests.append("operations")
    if interest_sales:
        interests.append("sales")
    if interest_marketing:
        interests.append("marketing")
    if interest_tech:
        interests.append("tech")
    if interest_other:
        interests.append("other")

    csv_path = DATA_DIR / "human_results.csv"
    header = [
        "timestamp",
        "name",
        "email",
        "country",
        "city",
        "role",
        "languages",
        "interests",
        "consent_marketing",
        "hq1",
        "hq2",
        "hq3",
        "hq4",
        "hq5",
        "hq6",
        "hq7",
        "hq8",
        "hq9",
        "hq10",
        "total_score",
        "bucket",
        "recommendation",
    ]
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "name": name,
        "email": email,
        "country": country,
        "city": city,
        "role": role,
        "languages": languages,
        "interests": ",".join(interests),
        "consent_marketing": "yes" if consent_marketing else "no",
        "hq1": str(hq1),
        "hq2": str(hq2),
        "hq3": str(hq3),
        "hq4": str(hq4),
        "hq5": str(hq5),
        "hq6": str(hq6),
        "hq7": str(hq7),
        "hq8": str(hq8),
        "hq9": str(hq9),
        "hq10": str(hq10),
        "total_score": str(total),
        "bucket": bucket,
        "recommendation": recommendation,
    }
    _write_csv_row(csv_path, header, row)

    return templates.TemplateResponse(
        "human_result.html",
        {
            "request": request,
            "name": name,
            "total_score": total,
            "bucket": bucket,
            "title": title,
            "recommendation": recommendation,
            "interests": interests,
        },
    )


class BusinessAPIRequest(BaseModel):
    company_name: str
    website: str | None = None
    country: str | None = None
    industry: str | None = None
    employees: str | None = None
    contact_name: str
    contact_role: str | None = None
    email: str
    consent_marketing: bool = False
    priority_sales: bool = False
    priority_support: bool = False
    priority_operations: bool = False
    priority_finance: bool = False
    priority_hr: bool = False
    q1: int
    q2: int
    q3: int
    q4: int
    q5: int
    q6: int
    q7: int
    q8: int
    q9: int
    q10: int
    q11: int
    q12: int


@app.post("/api/business")
async def business_api(payload: BusinessAPIRequest) -> Dict[str, object]:
    scores = [
        payload.q1,
        payload.q2,
        payload.q3,
        payload.q4,
        payload.q5,
        payload.q6,
        payload.q7,
        payload.q8,
        payload.q9,
        payload.q10,
        payload.q11,
        payload.q12,
    ]
    total = sum(scores)

    if total <= 29:
        bucket = "low"
        title = "Low AI Readiness – Big Upside if You Start Structured"
        recommendation = "AI Impact Audit (primary) + optional intro training."
    elif total <= 44:
        bucket = "medium"
        title = "Medium AI Readiness – Time to Consolidate and Train"
        recommendation = "AI Impact Staff Training + focused implementation on 2–3 workflows."
    else:
        bucket = "high"
        title = "High AI Readiness – Ready to Turn AI into Revenue"
        recommendation = "AI Sales in Practice (build outbound/inside-sales machine) and portfolio deployment."

    priorities: List[str] = []
    if payload.priority_sales:
        priorities.append("sales")
    if payload.priority_support:
        priorities.append("support")
    if payload.priority_operations:
        priorities.append("operations")
    if payload.priority_finance:
        priorities.append("finance")
    if payload.priority_hr:
        priorities.append("hr")

    csv_path = DATA_DIR / "business_results.csv"
    header = [
        "timestamp",
        "company_name",
        "website",
        "country",
        "industry",
        "employees",
        "contact_name",
        "contact_role",
        "email",
        "consent_marketing",
        "priorities",
        "q1",
        "q2",
        "q3",
        "q4",
        "q5",
        "q6",
        "q7",
        "q8",
        "q9",
        "q10",
        "q11",
        "q12",
        "total_score",
        "bucket",
        "recommendation",
    ]
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "company_name": payload.company_name,
        "website": payload.website or "",
        "country": payload.country or "",
        "industry": payload.industry or "",
        "employees": payload.employees or "",
        "contact_name": payload.contact_name,
        "contact_role": payload.contact_role or "",
        "email": payload.email,
        "consent_marketing": "yes" if payload.consent_marketing else "no",
        "priorities": ",".join(priorities),
        "q1": str(payload.q1),
        "q2": str(payload.q2),
        "q3": str(payload.q3),
        "q4": str(payload.q4),
        "q5": str(payload.q5),
        "q6": str(payload.q6),
        "q7": str(payload.q7),
        "q8": str(payload.q8),
        "q9": str(payload.q9),
        "q10": str(payload.q10),
        "q11": str(payload.q11),
        "q12": str(payload.q12),
        "total_score": str(total),
        "bucket": bucket,
        "recommendation": recommendation,
    }
    _write_csv_row(csv_path, header, row)

    return {
        "total_score": total,
        "bucket": bucket,
        "title": title,
        "recommendation": recommendation,
        "priorities": priorities,
    }


class HumanAPIRequest(BaseModel):
    name: str
    email: str
    country: str | None = None
    city: str | None = None
    role: str | None = None
    languages: str | None = None
    interest_operations: bool = False
    interest_sales: bool = False
    interest_marketing: bool = False
    interest_tech: bool = False
    interest_other: bool = False
    consent_marketing: bool = False
    hq1: int
    hq2: int
    hq3: int
    hq4: int
    hq5: int
    hq6: int
    hq7: int
    hq8: int
    hq9: int
    hq10: int


@app.post("/api/human")
async def human_api(payload: HumanAPIRequest) -> Dict[str, object]:
    scores = [
        payload.hq1,
        payload.hq2,
        payload.hq3,
        payload.hq4,
        payload.hq5,
        payload.hq6,
        payload.hq7,
        payload.hq8,
        payload.hq9,
        payload.hq10,
    ]
    total = sum(scores)

    if total <= 24:
        bucket = "low"
        title = "Early in AI – Great Time to Build Foundations"
        recommendation = "Foundations of AI in Work training (daily usage, prompts, basic tools)."
    elif total <= 37:
        bucket = "medium"
        title = "Solid AI Readiness – Time to Specialize"
        recommendation = "Choose AI Operator / Implementation or AI Sales Support track."
    else:
        bucket = "high"
        title = "High AI Readiness – Ready for Real Projects"
        recommendation = "Consider AI Sales in Practice / SDR-like role or implementation lead on client projects."

    interests: List[str] = []
    if payload.interest_operations:
        interests.append("operations")
    if payload.interest_sales:
        interests.append("sales")
    if payload.interest_marketing:
        interests.append("marketing")
    if payload.interest_tech:
        interests.append("tech")
    if payload.interest_other:
        interests.append("other")

    csv_path = DATA_DIR / "human_results.csv"
    header = [
        "timestamp",
        "name",
        "email",
        "country",
        "city",
        "role",
        "languages",
        "interests",
        "consent_marketing",
        "hq1",
        "hq2",
        "hq3",
        "hq4",
        "hq5",
        "hq6",
        "hq7",
        "hq8",
        "hq9",
        "hq10",
        "total_score",
        "bucket",
        "recommendation",
    ]
    row = {
        "timestamp": datetime.utcnow().isoformat(),
        "name": payload.name,
        "email": payload.email,
        "country": payload.country or "",
        "city": payload.city or "",
        "role": payload.role or "",
        "languages": payload.languages or "",
        "interests": ",".join(interests),
        "consent_marketing": "yes" if payload.consent_marketing else "no",
        "hq1": str(payload.hq1),
        "hq2": str(payload.hq2),
        "hq3": str(payload.hq3),
        "hq4": str(payload.hq4),
        "hq5": str(payload.hq5),
        "hq6": str(payload.hq6),
        "hq7": str(payload.hq7),
        "hq8": str(payload.hq8),
        "hq9": str(payload.hq9),
        "hq10": str(payload.hq10),
        "total_score": str(total),
        "bucket": bucket,
        "recommendation": recommendation,
    }
    _write_csv_row(csv_path, header, row)

    return {
        "total_score": total,
        "bucket": bucket,
        "title": title,
        "recommendation": recommendation,
        "interests": interests,
    }

