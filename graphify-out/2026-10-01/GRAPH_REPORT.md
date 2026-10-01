# Graph Report - automatic_job_apply  (2026-10-01)

## Corpus Check
- 45 files · ~10,697 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .bat 1, .css 1)

## Summary
- 248 nodes · 528 edges · 23 communities (9 shown, 14 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 32 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2e6cae8f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run.py
- MasterProfile
- app.py
- Database
- LLMClient
- config_loader.py
- ⚡ AutoJobForge
- Tasks
- 3. Module Specifications
- rules/graphify.md
- workflows/graphify.md

## God Nodes (most connected - your core abstractions)
1. `MasterProfile` - 32 edges
2. `LLMClient` - 27 edges
3. `Database` - 24 edges
4. `BrowserManager` - 18 edges
5. `FormFiller` - 16 edges
6. `main()` - 14 edges
7. `SubmissionVerifier` - 14 edges
8. `Tasks` - 13 edges
9. `load_config()` - 12 edges
10. `IndeedApplier` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Tech Stack` --references--> `LLMClient`  [INFERRED]
  docs/superpowers/specs/2026-09-30-autojobforge-design.md → src/ai/llm_client.py
- `test_form_filler_answer()` --uses--> `FormFiller`  [INFERRED]
  tests/test_form_filler.py → src/applier/form_filler.py
- `main()` --calls--> `LLMClient`  [EXTRACTED]
  run.py → src/ai/llm_client.py
- `main()` --calls--> `load_config()`  [EXTRACTED]
  run.py → src/config_loader.py
- `main()` --calls--> `ResumeCompiler`  [EXTRACTED]
  run.py → src/resume/compiler.py

## Import Cycles
- None detected.

## Communities (23 total, 14 thin omitted)

### Community 0 - "run.py"
Cohesion: 0.13
Nodes (10): main(), BrowserManager, FormFiller, IndeedApplier, LinkedInApplier, SubmissionVerifier, test_applier_drivers_init(), test_browser_manager_init() (+2 more)

### Community 1 - "MasterProfile"
Cohesion: 0.18
Nodes (12): ResumeCompiler, EducationItem, MasterProfile, PersonalInfo, ProjectItem, Skills, WorkExperienceItem, test_typst_resume_compilation() (+4 more)

### Community 2 - "app.py"
Cohesion: 0.12
Nodes (10): dashboard(), get_profile_data(), preview_pdf(), profile_page(), save_profile(), save_settings(), settings_page(), trigger_run() (+2 more)

### Community 3 - "Database"
Cohesion: 0.13
Nodes (3): JobFetcher, Database, test_database_init_and_crud()

### Community 4 - "LLMClient"
Cohesion: 0.10
Nodes (6): LLMClient, CVIngestor, ResumeTailor, JobMatcher, test_llm_client_json_cleaning(), test_llm_client_mock_gemini()

### Community 5 - "config_loader.py"
Cohesion: 0.25
Nodes (9): AppConfig, AppSettings, BrowserSettings, LLMSettings, load_config(), PlatformSettings, SearchSettings, test_load_config_default() (+1 more)

### Community 6 - "⚡ AutoJobForge"
Cohesion: 0.12
Nodes (16): 1. Prerequisites, 2. Installation, 3. Configuration, ⚡ AutoJobForge, ✨ Core Features, 🚀 Getting Started, 📄 License, Option A: The Web Dashboard (Recommended) (+8 more)

### Community 7 - "Tasks"
Cohesion: 0.12
Nodes (15): AutoJobForge Implementation Plan, File Structure Map, Task 10: Headless CLI Orchestrator & Windows Task Scheduler Setup, Task 11: Modern Dark-Mode Web Dashboard, Task 12: End-to-End Integration Verification & Portfolio README, Task 1: Environment Setup & Project Configuration, Task 2: Storage & Database Layer, Task 3: Pluggable AI Client & Prompts (+7 more)

### Community 9 - "3. Module Specifications"
Cohesion: 0.14
Nodes (13): 1. Overview & Goals, 2. Architecture & Tech Stack, 3.1 Ingestion & ATS Resume Compiler (`src/resume/`), 3.2 Job Scraper & Match Scoring (`src/scraper/`), 3.3 Playwright Stealth Applier (`src/applier/`), 3.4 Storage & Verification (`src/storage/`), 3.5 Web Dashboard & CLI (`src/web/`, `run.py`), 3. Module Specifications (+5 more)

## Knowledge Gaps
- **36 isolated node(s):** `graphify`, `Workflow: graphify`, `🌟 Why AutoJobForge?`, `🏛️ System Architecture`, `✨ Core Features` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 98 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMClient` connect `LLMClient` to `run.py`, `3. Module Specifications`, `app.py`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `run.py`, `app.py`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `MasterProfile` connect `MasterProfile` to `run.py`, `app.py`, `LLMClient`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `MasterProfile` (e.g. with `FormFiller` and `ResumeCompiler`) actually correct?**
  _`MasterProfile` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `LLMClient` (e.g. with `Tech Stack` and `FormFiller`) actually correct?**
  _`LLMClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Database` (e.g. with `IndeedApplier` and `LinkedInApplier`) actually correct?**
  _`Database` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `BrowserManager` (e.g. with `IndeedApplier` and `LinkedInApplier`) actually correct?**
  _`BrowserManager` has 3 INFERRED edges - model-reasoned connections that need verification._