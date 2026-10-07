# src/web/app.py
import os
import sys
import json
import yaml
import subprocess
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.storage.database import Database
from src.config_loader import load_config
from src.ai.llm_client import LLMClient
from src.resume.ingestor import CVIngestor
from src.resume.compiler import ResumeCompiler
from src.resume.models import MasterProfile

app = FastAPI(title="AutoJobForge Dashboard")

# Static files & templates
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates = Jinja2Templates(directory=str(templates_dir))

db = Database()

def get_profile_data() -> tuple[dict, str]:
    p_file = Path("config/master_profile.json")
    if not p_file.exists():
        p_file = Path("config/master_profile.example.json")
    if p_file.exists():
        raw = p_file.read_text(encoding="utf-8")
        return json.loads(raw), raw
    return {}, "{}"

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, status: Optional[str] = "SUBMITTED"):
    stats = db.get_stats()
    applications = db.get_all_applications(limit=100, status=status)
    total_att = (stats["total_submitted"] + stats["total_failed"]) or 1
    success_rate = int((stats["total_submitted"] / total_att) * 100) if stats["total_submitted"] else 0
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "stats": stats,
            "applications": applications,
            "success_rate": success_rate,
            "filter_status": status
        }
    )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, success: Optional[str] = None, error: Optional[str] = None):
    profile_dict, profile_json = get_profile_data()
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "profile": profile_dict,
            "profile_json": profile_json,
            "success": success,
            "error": error
        }
    )

@app.post("/profile/save")
async def save_profile(profile_json: str = Form(...)):
    p_file = Path("config/master_profile.json")
    p_file.parent.mkdir(parents=True, exist_ok=True)
    # Validate JSON
    data = json.loads(profile_json)
    validated = MasterProfile(**data)
    p_file.write_text(validated.model_dump_json(indent=2), encoding="utf-8")
    return RedirectResponse(url="/profile?success=Master+Profile+saved+successfully!", status_code=303)

@app.post("/profile/upload")
async def upload_cv(file: UploadFile = File(...)):
    tmp_path = Path("storage") / f"temp_{file.filename}"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    
    try:
        config = load_config()
        llm = LLMClient(provider=config.llm.provider, model=config.llm.model, api_key=config.llm.api_key)
        ingestor = CVIngestor(llm)
        ingestor.ingest_cv(tmp_path, output_json="config/master_profile.json")
        return RedirectResponse(url="/profile?success=CV+parsed+and+Master+Profile+updated+successfully!", status_code=303)
    except Exception as e:
        logger.error(f"Error ingesting CV: {e}", exc_info=True)
        from urllib.parse import quote_plus
        return RedirectResponse(url=f"/profile?error={quote_plus(str(e))}", status_code=303)
    finally:
        tmp_path.unlink(missing_ok=True)

@app.get("/profile/preview-pdf")
async def preview_pdf():
    profile_dict, _ = get_profile_data()
    if not profile_dict:
        return HTMLResponse("No profile found", status_code=404)
    profile = MasterProfile(**profile_dict)
    compiler = ResumeCompiler()
    preview_path = Path("storage/preview_resume.pdf")
    compiler.compile_pdf(profile, preview_path)
    return FileResponse(preview_path, media_type="application/pdf", filename="preview_resume.pdf")

@app.get("/resumes/{job_id}")
async def get_tailored_resume(job_id: str):
    app_record = db.get_application(job_id)
    if app_record and app_record.get("resume_path"):
        r_path = Path(app_record["resume_path"])
        if r_path.exists():
            return FileResponse(r_path, media_type="application/pdf", filename=r_path.name)
    pdf_path = Path(f"storage/tailored_resumes/{job_id}.pdf")
    if pdf_path.exists():
        return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_path.name)
    matches = list(Path("storage/tailored_resumes").glob(f"*{job_id}*.pdf"))
    if matches:
        return FileResponse(matches[0], media_type="application/pdf", filename=matches[0].name)
    return HTMLResponse("Tailored resume not found for this job ID", status_code=404)

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, success: Optional[str] = None, error: Optional[str] = None):
    config = load_config()
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "config": config,
            "success": success,
            "error": error
        }
    )

@app.post("/settings/save")
async def save_settings(
    mode: str = Form(...),
    daily_limit: int = Form(...),
    min_score: int = Form(...),
    job_titles: str = Form(...),
    locations: str = Form(...),
    is_remote: bool = Form(False),
    days_old: int = Form(14),
    easy_apply_only: bool = Form(False),
    max_experience_years: int = Form(2),
    llm_provider: str = Form(...),
    api_key: str = Form("")
):
    config = load_config()
    config.app.mode = mode
    config.app.daily_application_limit = daily_limit
    config.app.min_match_score = min_score
    config.search.job_titles = [t.strip() for t in job_titles.split(",") if t.strip()]
    config.search.locations = [l.strip() for l in locations.split(",") if l.strip()]
    config.search.is_remote = is_remote
    config.search.hours_old = max(1, days_old) * 24
    config.search.easy_apply_only = easy_apply_only
    config.search.max_experience_years = max(0, max_experience_years)
    config.llm.provider = llm_provider
    if api_key.strip():
        config.llm.api_key = api_key.strip()
    
    out_yaml = Path("config/config.yaml")
    out_yaml.parent.mkdir(parents=True, exist_ok=True)
    with open(out_yaml, "w", encoding="utf-8") as f:
        yaml.safe_dump(config.model_dump(), f)
    return RedirectResponse(url="/settings?success=Settings+saved+successfully!", status_code=303)

@app.post("/settings/login")
async def trigger_login(background_tasks: BackgroundTasks, platform: str = Form("linkedin")):
    def run_login():
        python_exe = sys.executable
        subprocess.run([python_exe, "run.py", "--login", platform])

    background_tasks.add_task(run_login)
    return RedirectResponse(url="/settings?success=Chrome+browser+launched!+Please+log+in+in+the+opened+window.", status_code=303)

@app.get("/receipts/{job_id}")
async def view_receipt(job_id: str):
    rec = db.get_application(job_id)
    if rec and rec.get("screenshot_path") and Path(rec["screenshot_path"]).exists():
        return FileResponse(rec["screenshot_path"], media_type="image/png")
    return HTMLResponse("No receipt screenshot found for this application.", status_code=404)

@app.post("/run")
async def trigger_run(background_tasks: BackgroundTasks):
    def run_worker():
        python_exe = sys.executable
        subprocess.run([python_exe, "run.py"])

    background_tasks.add_task(run_worker)
    return RedirectResponse(url="/", status_code=303)
