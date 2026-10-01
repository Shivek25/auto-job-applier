# Graph Report - automatic_job_apply  (2026-10-01)

## Corpus Check
- 42 files · ~12,315 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 447 nodes · 971 edges · 36 communities (17 shown, 19 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 103 edges (avg confidence: 0.79)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1cd60fc2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_run.py|run.py]]
- [[_COMMUNITY_MasterProfile|MasterProfile]]
- [[_COMMUNITY_app.py|app.py]]
- [[_COMMUNITY_Database|Database]]
- [[_COMMUNITY_LLMClient|LLMClient]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_⚡ AutoJobForge|⚡ AutoJobForge]]
- [[_COMMUNITY_Tasks|Tasks]]
- [[_COMMUNITY_BrowserManager|BrowserManager]]
- [[_COMMUNITY_3. Module Specifications|3. Module Specifications]]
- [[_COMMUNITY_SubmissionVerifier|SubmissionVerifier]]
- [[_COMMUNITY_ai__init__.py|ai/__init__.py]]
- [[_COMMUNITY_applier__init__.py|applier/__init__.py]]
- [[_COMMUNITY_src__init__.py|src/__init__.py]]
- [[_COMMUNITY_resume__init__.py|resume/__init__.py]]
- [[_COMMUNITY_scraper__init__.py|scraper/__init__.py]]
- [[_COMMUNITY_storage__init__.py|storage/__init__.py]]
- [[_COMMUNITY_web__init__.py|web/__init__.py]]
- [[_COMMUNITY_tests__init__.py|tests/__init__.py]]
- [[_COMMUNITY_main.js|main.js]]
- [[_COMMUNITY_test_web_app.py|test_web_app.py]]
- [[_COMMUNITY_rulesgraphify|rules/graphify.md]]
- [[_COMMUNITY_workflowsgraphify|workflows/graphify.md]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]

## God Nodes (most connected - your core abstractions)
1. `MasterProfile` - 32 edges
2. `LLMClient` - 27 edges
3. `Database` - 24 edges
4. `BrowserManager` - 19 edges
5. `load_config()` - 17 edges
6. `MasterProfile` - 17 edges
7. `LLMClient` - 16 edges
8. `test_typst_resume_compilation()` - 16 edges
9. `FormFiller` - 16 edges
10. `Database` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Tech Stack` --references--> `LLMClient`  [INFERRED]
  docs/superpowers/specs/2026-09-30-autojobforge-design.md → src/ai/llm_client.py
- `test_llm_client_model_routing()` --calls--> `LLMClient`  [INFERRED]
  tests/test_llm_client.py → src/ai/llm_client.py
- `main()` --calls--> `load_config()`  [INFERRED]
  run.py → src/config_loader.py
- `main()` --calls--> `MasterProfile`  [INFERRED]
  run.py → src/resume/models.py
- `main()` --calls--> `LLMClient`  [INFERRED]
  run.py → src/ai/llm_client.py

## Communities (36 total, 19 thin omitted)

### Community 0 - "run.py"
Cohesion: 0.08
Nodes (31): argparse, asyncio, BrowserContext, datetime, jobspy, logging, os, pathlib (+23 more)

### Community 1 - "MasterProfile"
Cohesion: 0.12
Nodes (27): pytest, ResumeCompiler, MasterProfile, PersonalInfo, Skills, ResumeTailor, shutil, Path (+19 more)

### Community 2 - "app.py"
Cohesion: 0.09
Nodes (28): BackgroundTasks, fastapi, fastapi_responses, fastapi_staticfiles, fastapi_templating, get, post, Request (+20 more)

### Community 3 - "Database"
Cohesion: 0.09
Nodes (8): BrowserManager, FormFiller, IndeedApplier, LinkedInApplier, main(), JobFetcher, Database, SubmissionVerifier

### Community 4 - "LLMClient"
Cohesion: 0.07
Nodes (29): AutoJobForge Implementation Plan, code:block1 (automatic_job_apply/), code:block10, code:block11 (Open `http://localhost:8000` to upload your existing CV (.pd), code:block12 (To setup Windows Task Scheduler for daily 09:30 AM runs:), code:block13, code:bash (git add README.md), code:bash (git add src/applier/browser.py) (+21 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (23): 1. Prerequisites, 2. Installation, 3. Configuration, ⚡ AutoJobForge, code:mermaid (flowchart TD), code:bash (# Clone the repository), code:powershell ($env:GEMINI_API_KEY="your-gemini-api-key"), code:bash (uvicorn src.web.app:app --reload --port 8000) (+15 more)

### Community 6 - "⚡ AutoJobForge"
Cohesion: 0.13
Nodes (9): LLMClient, Any, CVIngestor, Path, upload_cv(), test_llm_client_json_cleaning(), test_llm_client_mock_gemini(), test_llm_client_model_routing() (+1 more)

### Community 7 - "Tasks"
Cohesion: 0.23
Nodes (16): BaseModel, pydantic, EducationItem, ProjectItem, WorkExperienceItem, AppConfig, AppSettings, BrowserSettings (+8 more)

### Community 8 - "BrowserManager"
Cohesion: 0.18
Nodes (4): LLMClient, CVIngestor, JobMatcher, upload_cv()

### Community 9 - "3. Module Specifications"
Cohesion: 0.12
Nodes (16): 1. Prerequisites, 2. Installation, 3. Configuration, ⚡ AutoJobForge, ✨ Core Features, 🚀 Getting Started, 📄 License, Option A: The Web Dashboard (Recommended) (+8 more)

### Community 10 - "SubmissionVerifier"
Cohesion: 0.12
Nodes (15): 1. Overview & Goals, 2. Architecture & Tech Stack, 3.1 Ingestion & ATS Resume Compiler (`src/resume/`), 3.2 Job Scraper & Match Scoring (`src/scraper/`), 3.3 Playwright Stealth Applier (`src/applier/`), 3.4 Storage & Verification (`src/storage/`), 3.5 Web Dashboard & CLI (`src/web/`, `run.py`), 3. Module Specifications (+7 more)

### Community 11 - "ai/__init__.py"
Cohesion: 0.12
Nodes (15): AutoJobForge Implementation Plan, File Structure Map, Task 10: Headless CLI Orchestrator & Windows Task Scheduler Setup, Task 11: Modern Dark-Mode Web Dashboard, Task 12: End-to-End Integration Verification & Portfolio README, Task 1: Environment Setup & Project Configuration, Task 2: Storage & Database Layer, Task 3: Pluggable AI Client & Prompts (+7 more)

### Community 12 - "applier/__init__.py"
Cohesion: 0.24
Nodes (4): Connection, Database, Any, Path

### Community 13 - "src/__init__.py"
Cohesion: 0.31
Nodes (6): json, pdfplumber, re, requests, time, typing

### Community 14 - "resume/__init__.py"
Cohesion: 0.14
Nodes (13): 1. Overview & Goals, 2. Architecture & Tech Stack, 3.1 Ingestion & ATS Resume Compiler (`src/resume/`), 3.2 Job Scraper & Match Scoring (`src/scraper/`), 3.3 Playwright Stealth Applier (`src/applier/`), 3.4 Storage & Verification (`src/storage/`), 3.5 Web Dashboard & CLI (`src/web/`, `run.py`), 3. Module Specifications (+5 more)

## Knowledge Gaps
- **106 isolated node(s):** `AI client and prompt templates for AutoJobForge`, `Job application execution and automation package for AutoJobForge`, `Resume and CV processing package for AutoJobForge`, `Job discovery and matching package for AutoJobForge`, `Storage and persistence package for AutoJobForge` (+101 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMClient` connect `⚡ AutoJobForge` to `run.py`, `MasterProfile`, `app.py`, `src/__init__.py`, `resume/__init__.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `main()` connect `Database` to `run.py`, `MasterProfile`, `BrowserManager`, `Tasks`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Why does `Database` connect `applier/__init__.py` to `run.py`, `app.py`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `MasterProfile` (e.g. with `FormFiller` and `ResumeCompiler`) actually correct?**
  _`MasterProfile` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `LLMClient` (e.g. with `Tech Stack` and `FormFiller`) actually correct?**
  _`LLMClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Database` (e.g. with `IndeedApplier` and `LinkedInApplier`) actually correct?**
  _`Database` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `AI client and prompt templates for AutoJobForge`, `Job application execution and automation package for AutoJobForge`, `Resume and CV processing package for AutoJobForge` to the rest of the system?**
  _106 weakly-connected nodes found - possible documentation gaps or missing edges._