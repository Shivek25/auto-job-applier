# Graph Report - automatic_job_apply  (2026-10-01)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 196 nodes · 479 edges · 20 communities (6 shown, 14 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 31 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3517183e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run.py
- MasterProfile
- app.py
- Database
- LLMClient
- config_loader.py
- compiler.py

## God Nodes (most connected - your core abstractions)
1. `MasterProfile` - 32 edges
2. `LLMClient` - 26 edges
3. `Database` - 24 edges
4. `BrowserManager` - 18 edges
5. `FormFiller` - 16 edges
6. `SubmissionVerifier` - 14 edges
7. `main()` - 14 edges
8. `load_config()` - 12 edges
9. `IndeedApplier` - 11 edges
10. `LinkedInApplier` - 11 edges

## Surprising Connections (you probably didn't know these)
- `test_form_filler_answer()` --uses--> `FormFiller`  [INFERRED]
  tests/test_form_filler.py → src/applier/form_filler.py
- `test_browser_manager_init()` --calls--> `BrowserManager`  [EXTRACTED]
  tests/test_browser.py → src/applier/browser.py
- `test_browser_manager_lifecycle()` --uses--> `BrowserManager`  [INFERRED]
  tests/test_browser.py → src/applier/browser.py
- `test_verifier_receipt_path()` --calls--> `SubmissionVerifier`  [EXTRACTED]
  tests/test_verifier.py → src/storage/verifier.py
- `main()` --calls--> `MasterProfile`  [EXTRACTED]
  run.py → src/resume/models.py

## Import Cycles
- None detected.

## Communities (20 total, 14 thin omitted)

### Community 0 - "run.py"
Cohesion: 0.13
Nodes (10): main(), BrowserManager, FormFiller, IndeedApplier, LinkedInApplier, SubmissionVerifier, test_applier_drivers_init(), test_browser_manager_init() (+2 more)

### Community 1 - "MasterProfile"
Cohesion: 0.21
Nodes (13): EducationItem, MasterProfile, PersonalInfo, ProjectItem, Skills, WorkExperienceItem, ResumeTailor, JobMatcher (+5 more)

### Community 2 - "app.py"
Cohesion: 0.12
Nodes (10): dashboard(), get_profile_data(), preview_pdf(), profile_page(), save_profile(), save_settings(), settings_page(), trigger_run() (+2 more)

### Community 3 - "Database"
Cohesion: 0.13
Nodes (3): JobFetcher, Database, test_database_init_and_crud()

### Community 4 - "LLMClient"
Cohesion: 0.14
Nodes (4): LLMClient, CVIngestor, test_llm_client_json_cleaning(), test_llm_client_mock_gemini()

### Community 5 - "config_loader.py"
Cohesion: 0.25
Nodes (9): AppConfig, AppSettings, BrowserSettings, LLMSettings, load_config(), PlatformSettings, SearchSettings, test_load_config_default() (+1 more)

## Knowledge Gaps
- **14 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Database` to `run.py`, `app.py`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Why does `MasterProfile` connect `MasterProfile` to `run.py`, `app.py`, `LLMClient`, `compiler.py`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `LLMClient` connect `LLMClient` to `run.py`, `MasterProfile`, `app.py`?**
  _High betweenness centrality (0.117) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `MasterProfile` (e.g. with `FormFiller` and `ResumeCompiler`) actually correct?**
  _`MasterProfile` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `LLMClient` (e.g. with `FormFiller` and `CVIngestor`) actually correct?**
  _`LLMClient` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Database` (e.g. with `IndeedApplier` and `LinkedInApplier`) actually correct?**
  _`Database` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `BrowserManager` (e.g. with `IndeedApplier` and `LinkedInApplier`) actually correct?**
  _`BrowserManager` has 3 INFERRED edges - model-reasoned connections that need verification._