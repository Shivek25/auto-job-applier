# Graph Report - automatic_job_apply  (2026-10-01)

## Corpus Check
- 45 files · ~11,352 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 5, .bat 1, .css 1)

## Summary
- 258 nodes · 531 edges · 25 communities (9 shown, 16 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 25 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9f3474dd`
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
- BrowserManager
- 3. Module Specifications
- rules/graphify.md
- workflows/graphify.md

## God Nodes (most connected - your core abstractions)
1. `MasterProfile` - 32 edges
2. `LLMClient` - 27 edges
3. `Database` - 20 edges
4. `BrowserManager` - 19 edges
5. `main()` - 14 edges
6. `FormFiller` - 14 edges
7. `Tasks` - 13 edges
8. `load_config()` - 12 edges
9. `SubmissionVerifier` - 12 edges
10. `IndeedApplier` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Tech Stack` --references--> `LLMClient`  [INFERRED]
  docs/superpowers/specs/2026-09-30-autojobforge-design.md → src/ai/llm_client.py
- `test_form_filler_answer()` --uses--> `FormFiller`  [INFERRED]
  tests/test_form_filler.py → src/applier/form_filler.py
- `main()` --calls--> `LLMClient`  [EXTRACTED]
  run.py → src/ai/llm_client.py
- `main()` --calls--> `BrowserManager`  [EXTRACTED]
  run.py → src/applier/browser.py
- `main()` --calls--> `load_config()`  [EXTRACTED]
  run.py → src/config_loader.py

## Import Cycles
- None detected.

## Communities (25 total, 16 thin omitted)

### Community 0 - "run.py"
Cohesion: 0.11
Nodes (8): main(), FormFiller, IndeedApplier, LinkedInApplier, JobFetcher, SubmissionVerifier, test_applier_drivers_init(), test_verifier_receipt_path()

### Community 1 - "MasterProfile"
Cohesion: 0.16
Nodes (14): ResumeCompiler, EducationItem, MasterProfile, PersonalInfo, ProjectItem, Skills, WorkExperienceItem, ResumeTailor (+6 more)

### Community 2 - "app.py"
Cohesion: 0.11
Nodes (11): dashboard(), get_profile_data(), preview_pdf(), profile_page(), save_profile(), save_settings(), settings_page(), trigger_login() (+3 more)

### Community 4 - "LLMClient"
Cohesion: 0.12
Nodes (4): LLMClient, CVIngestor, test_llm_client_json_cleaning(), test_llm_client_mock_gemini()

### Community 5 - "config_loader.py"
Cohesion: 0.25
Nodes (9): AppConfig, AppSettings, BrowserSettings, LLMSettings, load_config(), PlatformSettings, SearchSettings, test_load_config_default() (+1 more)

### Community 6 - "⚡ AutoJobForge"
Cohesion: 0.12
Nodes (16): 1. Prerequisites, 2. Installation, 3. Configuration, ⚡ AutoJobForge, ✨ Core Features, 🚀 Getting Started, 📄 License, Option A: The Web Dashboard (Recommended) (+8 more)

### Community 7 - "Tasks"
Cohesion: 0.12
Nodes (15): AutoJobForge Implementation Plan, File Structure Map, Task 10: Headless CLI Orchestrator & Windows Task Scheduler Setup, Task 11: Modern Dark-Mode Web Dashboard, Task 12: End-to-End Integration Verification & Portfolio README, Task 1: Environment Setup & Project Configuration, Task 2: Storage & Database Layer, Task 3: Pluggable AI Client & Prompts (+7 more)

### Community 8 - "BrowserManager"
Cohesion: 0.14
Nodes (3): BrowserManager, test_browser_manager_init(), test_browser_manager_lifecycle()

### Community 9 - "3. Module Specifications"
Cohesion: 0.14
Nodes (13): 1. Overview & Goals, 2. Architecture & Tech Stack, 3.1 Ingestion & ATS Resume Compiler (`src/resume/`), 3.2 Job Scraper & Match Scoring (`src/scraper/`), 3.3 Playwright Stealth Applier (`src/applier/`), 3.4 Storage & Verification (`src/storage/`), 3.5 Web Dashboard & CLI (`src/web/`, `run.py`), 3. Module Specifications (+5 more)

## Knowledge Gaps
- **36 isolated node(s):** `graphify`, `Workflow: graphify`, `1. Prerequisites`, `2. Installation`, `3. Configuration` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 105 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `LLMClient` connect `LLMClient` to `run.py`, `3. Module Specifications`, `app.py`, `MasterProfile`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Why does `Database` connect `Database` to `run.py`, `app.py`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `BrowserManager` connect `BrowserManager` to `run.py`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `MasterProfile` (e.g. with `FormFiller` and `ResumeCompiler`) actually correct?**
  _`MasterProfile` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `LLMClient` (e.g. with `Tech Stack` and `FormFiller`) actually correct?**
  _`LLMClient` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `BrowserManager` (e.g. with `IndeedApplier` and `LinkedInApplier`) actually correct?**
  _`BrowserManager` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `graphify`, `Workflow: graphify`, `1. Prerequisites` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._