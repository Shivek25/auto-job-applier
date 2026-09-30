# AutoJobForge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete, free, local-first automated job application and dynamic ATS resume tailoring system on Windows targeting LinkedIn and Indeed Easy Apply with verification receipts, a modern Web Dashboard, and a Task Scheduler CLI.

**Architecture:** A modular Python pipeline combining `python-jobspy` for job discovery, a pluggable LLM interface (Gemini Flash / Groq / Ollama) for CV tailoring and screening questions, a Typst ATS PDF compiler for single-page resume generation, a stealth Playwright engine attached to the user's Chrome profile, an SQLite audit store, and a FastAPI web dashboard.

**Tech Stack:** Python 3.11+, Playwright, playwright-stealth, python-jobspy, google-genai, typst, FastAPI, Uvicorn, Jinja2, SQLite3, pytest.

---

## File Structure Map

```
automatic_job_apply/
├── config/
│   ├── config.yaml               # User preferences (keywords, location, daily limit, mode)
│   └── master_profile.json       # Candidate master structured CV
├── src/
│   ├── __init__.py
│   ├── config_loader.py          # Pydantic models & config loader
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── llm_client.py         # Pluggable LLM interface (Gemini Flash, Groq, Ollama)
│   │   └── prompts.py            # System prompts for CV ingestion, tailoring & form answering
│   ├── resume/
│   │   ├── __init__.py
│   │   ├── models.py             # MasterProfile Pydantic schema
│   │   ├── ingestor.py           # Ingests PDF CV -> master_profile.json
│   │   ├── tailor.py             # Tailors profile fields against target Job Description
│   │   └── compiler.py           # Compiles tailored profile into PDF via Typst
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── job_fetcher.py        # python-jobspy wrapper with deduplication
│   │   └── matcher.py            # AI semantic match scoring engine
│   ├── applier/
│   │   ├── __init__.py
│   │   ├── browser.py            # Playwright session manager with stealth & user profile
│   │   ├── form_filler.py        # AI-driven modal form-field detection and answering
│   │   ├── linkedin.py           # LinkedIn Easy Apply flow handler
│   │   └── indeed.py             # Indeed Easily Apply flow handler
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py           # SQLite manager and migrations
│   │   └── verifier.py           # DOM submission detector & screenshot receipt capturer
│   └── web/
│       ├── __init__.py
│       ├── app.py                # FastAPI routes & endpoints
│       ├── static/
│       │   ├── css/style.css     # Modern dark-mode styling
│       │   └── js/main.js        # Interactive dashboard logic
│       └── templates/
│           ├── base.html
│           ├── dashboard.html
│           ├── profile.html
│           └── settings.html
├── templates/
│   └── modern_ats.typ            # Typst resume template
├── storage/
│   ├── applications.db           # SQLite database
│   ├── receipts/                 # Screenshot proof of submissions
│   └── tailored_resumes/         # Generated dynamic PDFs
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_llm_client.py
│   ├── test_resume_models.py
│   ├── test_resume_tailor.py
│   ├── test_compiler.py
│   ├── test_job_matcher.py
│   └── test_verifier.py
├── run.py                        # Standalone CLI entrypoint for Windows Task Scheduler
├── setup_task.bat                # Windows Task Scheduler automation helper
├── requirements.txt              # Project dependencies
└── README.md                     # Portfolio documentation & setup instructions
```

---

## Tasks

### Task 1: Environment Setup & Project Configuration

**Files:**
- Create: `requirements.txt`
- Create: `config/config.yaml`
- Create: `src/config_loader.py`
- Create: `tests/test_config.py`

- [x] **Step 1: Write the failing test for configuration loader**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Create `requirements.txt` and install core dependencies**
- [x] **Step 4: Implement `src/config_loader.py` and `config/config.yaml`**
- [x] **Step 5: Run tests to verify they pass**
- [x] **Step 6: Commit**

---

### Task 2: Storage & Database Layer

**Files:**
- Create: `src/storage/database.py`
- Create: `tests/test_database.py`

- [x] **Step 1: Write the failing test for SQLite database operations**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `src/storage/database.py`**
- [x] **Step 4: Run tests to verify they pass**
- [x] **Step 5: Commit**

---

### Task 3: Pluggable AI Client & Prompts

**Files:**
- Create: `src/ai/prompts.py`
- Create: `src/ai/llm_client.py`
- Create: `tests/test_llm_client.py`

- [x] **Step 1: Write failing test for LLM client abstraction**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `src/ai/prompts.py`**
- [x] **Step 4: Implement `src/ai/llm_client.py` with multi-provider fallback**
- [x] **Step 5: Run tests to verify they pass**
- [x] **Step 6: Commit**

---

### Task 4: Master Profile Schema & CV Ingestion

**Files:**
- Create: `src/resume/models.py`
- Create: `src/resume/ingestor.py`
- Create: `tests/test_resume_models.py`

- [x] **Step 1: Write failing test for Master Profile schema & validation**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `src/resume/models.py` and `src/resume/ingestor.py`**
- [x] **Step 4: Run tests to verify they pass**
- [x] **Step 5: Commit**

---

### Task 5: Dynamic Resume Tailor & Typst ATS PDF Compiler

**Files:**
- Create: `templates/modern_ats.typ`
- Create: `src/resume/tailor.py`
- Create: `src/resume/compiler.py`
- Create: `tests/test_resume_tailor.py`
- Create: `tests/test_compiler.py`

- [x] **Step 1: Write failing test for Resume Tailoring and Typst compilation**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `templates/modern_ats.typ`**
- [x] **Step 4: Implement `src/resume/tailor.py` and `src/resume/compiler.py`**
- [x] **Step 5: Run tests to verify they pass**
- [x] **Step 6: Commit**

---

### Task 6: Job Discovery & AI Match Evaluator

**Files:**
- Create: `src/scraper/job_fetcher.py`
- Create: `src/scraper/matcher.py`
- Create: `tests/test_job_matcher.py`

- [x] **Step 1: Write failing test for Job Matcher**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `src/scraper/job_fetcher.py` and `src/scraper/matcher.py`**
- [x] **Step 4: Run tests to verify they pass**
- [x] **Step 5: Commit**

---

### Task 7: Playwright Stealth Browser & Session Manager

**Files:**
- Create: `src/applier/browser.py`

- [x] **Step 1: Implement `src/applier/browser.py` with persistent context & stealth**
- [x] **Step 2: Commit**

```bash
git add src/applier/browser.py
git commit -m "feat: implement stealth playwright browser session manager"
```

---

### Task 8: AI Screening Form-Filler & Submission Verifier

**Files:**
- Create: `src/applier/form_filler.py`
- Create: `src/storage/verifier.py`
- Create: `tests/test_verifier.py`

- [x] **Step 1: Write failing test for submission verifier**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `src/storage/verifier.py`**
- [x] **Step 4: Implement `src/applier/form_filler.py`**
- [x] **Step 5: Run tests to verify they pass**
- [x] **Step 6: Commit**

---

### Task 9: LinkedIn & Indeed Easy Apply Automators

**Files:**
- Create: `src/applier/linkedin.py`
- Create: `src/applier/indeed.py`

- [x] **Step 1: Implement `src/applier/linkedin.py`**
- [x] **Step 2: Implement `src/applier/indeed.py`**
- [x] **Step 3: Commit**

---

### Task 10: Headless CLI Orchestrator & Windows Task Scheduler Setup

**Files:**
- Create: `run.py`
- Create: `setup_task.bat`

- [x] **Step 1: Implement `run.py` CLI pipeline**
- [x] **Step 2: Create Windows Task Scheduler setup script `setup_task.bat`**
- [x] **Step 3: Commit**

---

### Task 11: Modern Dark-Mode Web Dashboard

**Files:**
- Create: `src/web/static/css/style.css`
- Create: `src/web/templates/base.html`
- Create: `src/web/templates/dashboard.html`
- Create: `src/web/templates/profile.html`
- Create: `src/web/templates/settings.html`
- Create: `src/web/app.py`

- [x] **Step 1: Create modern dark-mode stylesheet `src/web/static/css/style.css`**

```css
/* src/web/static/css/style.css */
:root {
  --bg-dark: #0f172a;
  --card-bg: #1e293b;
  --card-border: #334155;
  --text-primary: #f8fafc;
  --text-muted: #94a3b8;
  --accent-blue: #38bdf8;
  --accent-green: #4ade80;
  --accent-red: #f87171;
  --accent-purple: #c084fc;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background-color: var(--bg-dark);
  color: var(--text-primary);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--card-bg);
  border-bottom: 1px solid var(--card-border);
}

nav .brand {
  font-size: 20px;
  font-weight: bold;
  color: var(--accent-blue);
}

nav .links a {
  color: var(--text-muted);
  text-decoration: none;
  margin-left: 20px;
  font-weight: 500;
  transition: color 0.2s;
}

nav .links a:hover, nav .links a.active {
  color: var(--accent-blue);
}

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.kpi-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  padding: 20px;
}

.kpi-card .label {
  font-size: 13px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kpi-card .value {
  font-size: 28px;
  font-weight: bold;
  margin-top: 8px;
  color: var(--accent-blue);
}

table {
  width: 100%;
  border-collapse: collapse;
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 8px;
  overflow: hidden;
}

th, td {
  padding: 14px 18px;
  text-align: left;
  border-bottom: 1px solid var(--card-border);
}

th {
  background: #111827;
  color: var(--text-muted);
  font-size: 12px;
  text-transform: uppercase;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.badge.submitted { background: #065f46; color: #34d399; }
.badge.failed { background: #7f1d1d; color: #f87171; }
.badge.skipped { background: #374151; color: #9ca3af; }

.btn {
  background: var(--accent-blue);
  color: #0f172a;
  padding: 10px 18px;
  border: none;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
}

.btn:hover {
  opacity: 0.9;
}
```

- [x] **Step 2: Implement templates `base.html`, `dashboard.html`, `profile.html`, `settings.html`**

```html
<!-- src/web/templates/base.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>AutoJobForge | Autonomous Job Copilot</title>
  <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
  <nav>
    <div class="brand">⚡ AutoJobForge</div>
    <div class="links">
      <a href="/" class="active">Dashboard</a>
      <a href="/profile">Profile Studio</a>
      <a href="/settings">Settings</a>
    </div>
  </nav>
  <div class="container">
    {% block content %}{% endblock %}
  </div>
</body>
</html>
```

```html
<!-- src/web/templates/dashboard.html -->
{% extends "base.html" %}
{% block content %}
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
  <h2>Application Operations Hub</h2>
  <form action="/run" method="post" style="margin: 0;">
    <button type="submit" class="btn">🚀 Run Daily Batch Now</button>
  </form>
</div>

<div class="kpi-grid">
  <div class="kpi-card">
    <div class="label">Today's Applications</div>
    <div class="value">{{ stats.today_submitted }}</div>
  </div>
  <div class="kpi-card">
    <div class="label">Total Submitted</div>
    <div class="value">{{ stats.total_submitted }}</div>
  </div>
  <div class="kpi-card">
    <div class="label">Total Jobs Evaluated</div>
    <div class="value">{{ stats.total }}</div>
  </div>
  <div class="kpi-card">
    <div class="label">Success Rate</div>
    <div class="value">{{ success_rate }}%</div>
  </div>
</div>

<h3>Recent Applications</h3>
<table>
  <thead>
    <tr>
      <th>Timestamp</th>
      <th>Company</th>
      <th>Role</th>
      <th>Platform</th>
      <th>Match Score</th>
      <th>Status</th>
      <th>Proof Receipt</th>
    </tr>
  </thead>
  <tbody>
    {% for app in applications %}
    <tr>
      <td>{{ app.applied_at }}</td>
      <td><strong>{{ app.company }}</strong></td>
      <td>{{ app.title }}</td>
      <td>{{ app.platform | upper }}</td>
      <td>{{ app.match_score }}%</td>
      <td><span class="badge {{ app.status | lower }}">{{ app.status }}</span></td>
      <td>
        {% if app.screenshot_path %}
        <a href="/receipts/{{ app.job_id }}" target="_blank" style="color: var(--accent-blue);">View Screenshot</a>
        {% else %}
        -
        {% endif %}
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

- [x] **Step 3: Implement `src/web/app.py` FastAPI server**

```python
# src/web/app.py
from pathlib import Path
import json
import yaml
from fastapi import FastAPI, Request, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.storage.database import Database
from src.config_loader import load_config
from src.ai.llm_client import LLMClient
from src.resume.ingestor import CVIngestor
from src.resume.models import MasterProfile

app = FastAPI(title="AutoJobForge Dashboard")
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")
db = Database()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = db.get_stats()
    applications = db.get_all_applications(limit=50)
    total_att = (stats["total_submitted"] + stats["total_failed"]) or 1
    success_rate = int((stats["total_submitted"] / total_att) * 100)
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "stats": stats,
            "applications": applications,
            "success_rate": success_rate
        }
    )

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    p_file = Path("config/master_profile.json")
    profile_data = json.loads(p_file.read_text(encoding="utf-8")) if p_file.exists() else {}
    return templates.TemplateResponse("profile.html", {"request": request, "profile": profile_data})

@app.post("/profile/upload")
async def upload_cv(file: UploadFile = File(...)):
    tmp_path = Path(f"storage/temp_{file.filename}")
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_path, "wb") as f:
        f.write(await file.read())
    
    config = load_config()
    llm = LLMClient(provider=config.llm.provider, api_key=config.llm.api_key)
    ingestor = CVIngestor(llm)
    ingestor.ingest_cv(tmp_path)
    tmp_path.unlink(missing_ok=True)
    return RedirectResponse(url="/profile", status_code=303)

@app.get("/receipts/{job_id}")
async def view_receipt(job_id: str):
    rec = db.get_application(job_id)
    if rec and rec.get("screenshot_path") and Path(rec["screenshot_path"]).exists():
        return FileResponse(rec["screenshot_path"])
    return HTMLResponse("No receipt found", status_code=404)

@app.post("/run")
async def trigger_run(background_tasks: BackgroundTasks):
    import subprocess
    # Run run.py asynchronously in background
    background_tasks.add_task(subprocess.run, ["python", "run.py"])
    return RedirectResponse(url="/", status_code=303)
```

- [x] **Step 4: Commit**

```bash
git add src/web/
git commit -m "feat: implement modern web dashboard with fastui and jinja2"
```

---

### Task 12: End-to-End Integration Verification & Portfolio README

**Files:**
- Create: `README.md`
- Run: `pytest` complete test suite

- [ ] **Step 1: Create high-impact Portfolio `README.md`**

```markdown
# ⚡ AutoJobForge

> An intelligent, autonomous job application and dynamic resume tailoring pipeline engineered for LinkedIn and Indeed Easy Apply. 100% free, local-first, and stealthy.

## 🚀 Key Features

* **AI Dynamic CV Tailoring:** Ingests your Master Profile and rewrites skills, summaries, and bullet points to match the target Job Description using Google Gemini Flash.
* **Vector-Perfect ATS Resumes:** Compiles custom single-page, ATS-compliant PDFs on the fly using [Typst](https://typst.app/).
* **Stealth Playwright Execution:** Leverages existing Chrome browser sessions to bypass 2FA, OTPs, and Cloudflare/bot detections with real residential IPs.
* **Proof of Submission:** Captures timestamped screenshot receipts and logs every transaction to SQLite.
* **Modern Web Dashboard:** Visual Operations Hub built with FastAPI, dark-mode CSS, live stats, and one-click manual triggers.
* **Automated Daily Scheduling:** Zero-maintenance execution via native Windows Task Scheduler.

## 🛠️ Toolstack

* **Language:** Python 3.11+
* **Browser Automation:** Playwright, Playwright-Stealth
* **Job Discovery:** Python-JobSpy (LinkedIn & Indeed aggregator)
* **Document Engine:** Typst
* **AI Engine:** Google Gemini 2.0 Flash / Groq / Ollama
* **Backend:** FastAPI, Uvicorn, Jinja2
* **Storage:** SQLite

## 🏁 Quickstart

1. **Clone & Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Set your Gemini Free API Key:**
   ```powershell
   $env:GEMINI_API_KEY="your-api-key-here"
   ```

3. **Launch the Web Dashboard:**
   ```bash
   uvicorn src.web.app:app --reload --port 8000
   ```
   Open `http://localhost:8000` to upload your existing CV (.pdf) and configure your job search preferences.

4. **Run Headless Batch Manually or via Schedule:**
   ```bash
   python run.py --mode auto
   ```
   To setup Windows Task Scheduler for daily 09:30 AM runs:
   ```cmd
   setup_task.bat
   ```
```

- [ ] **Step 2: Run all tests to verify full passing state**

Run: `pytest`
Expected: ALL PASS

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive portfolio readme and architecture guide"
```
