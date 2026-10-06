# Design Spec: Self-Healing Browser Brain (Agentic Dynamic Form & Recovery Engine)

Date: 2026-10-06
Author: Antigravity Pair Programmer
Status: Approved & Expanded for Platform-Agnostic Company Applications

---

## 1. Overview & Objective

### 1.1 Problem Statement
1. **Fragility of Hardcoded Selectors**: Static scripts break whenever a platform alters CSS classes, wraps controls in new modals, or introduces unexpected UI elements.
2. **Dynamic Company Career Portals**: Applying directly on company websites (via Workday, Greenhouse, Lever, Ashby, SmartRecruiters, or bespoke career portals) is the highest-value application channel, but company application pages are completely non-standardized. They use custom forms, variable step sequences, dynamic screening questions, and embedded iframes.

### 1.2 Objective
Build an autonomous, platform-agnostic **Browser Brain** (`BrowserBrain`) that:
1. Operates as an intelligent web agent capable of understanding ANY job application flow: LinkedIn Easy Apply, Indeed, or direct company career sites.
2. Traverses main frames, embedded iframes (`page.frames`), and dialog containers.
3. Dynamically extracts form elements (inputs, dropdowns, radios, checkboxes, textareas, file uploaders) and pairs them with candidate data from `MasterProfile`.
4. Intelligently answers arbitrary screening questions (e.g., notice period, expected compensation, work authorization, tool experience) using LLM reasoning.
5. Diagnoses blockers on the fly (e.g., validation warnings, URL drift, overlay popups, obscured buttons) and executes corrective actions.
6. Caches learned patterns in persistent memory (`storage/brain_memory.json`) for speed and zero-token repeat execution.

---

## 2. Architecture: Universal Perception & Action Loop

```
+--------------------------------------------------------------------------------+
|                         Target Job Application Flow                            |
|             (LinkedIn Easy Apply, Indeed, Greenhouse, Workday, Lever)          |
+---------------------------------------+----------------------------------------+
                                        |
                             Browser Page State (Playwright)
                                        |
                                        v
+---------------------------------------+----------------------------------------+
|                   Perception: Universal Form & UI Extractor                    |
|                                                                                |
|  1. Frame Hierarchy: Traverses page main document and child iframes            |
|  2. Semantic Forms: Extracts labels, input types, required flags, current state|
|  3. Action Targets: Identifies primary buttons ('Apply', 'Next', 'Submit')     |
|  4. Diagnostics: Captures validation errors, blocked inputs, dialog overlays   |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+---------------------------------------+----------------------------------------+
|                     Reasoning: Diagnostic & Form Brain                         |
|                                                                                |
|  A. Intent Identification: (e.g. Job View -> Apply Button -> Multi-step Form)  |
|  B. Form Mapping: Maps candidate MasterProfile to dynamic field names          |
|  C. Screening Q&A: Generates context-appropriate answers to custom questions   |
|  D. Blocker Diagnosis: Pinpoints why progress stopped and prescribes remedy   |
+---------------------------------------+----------------------------------------+
                                        |
                                        v
+---------------------------------------+----------------------------------------+
|                         Execution & Self-Healing                               |
|                                                                                |
|  - Fill fields / select options / trigger file upload                          |
|  - Click navigation control or recovery action                                 |
|  - Verify state transition (did wizard step advance or modal open?)            |
|  - Update persistent memory cache (storage/brain_memory.json)                  |
+--------------------------------------------------------------------------------+
```

---

## 3. Core Capabilities & Component Breakdown

### 3.1 Universal DOM & Frame Perception (`src/applier/brain.py`)
Company portals often load application forms inside child iframes (e.g., embedded Greenhouse or Workday forms). The perception engine:
- Traverses `page.frames` to inspect all embedded documents.
- Extracts a compact, normalized JSON representation of interactive elements:
  ```json
  {
    "url": "https://company.com/careers/data-analyst",
    "is_job_page": true,
    "apply_button_found": true,
    "form_fields": [
      {"id": "field_1", "label": "Years of Python experience", "type": "number", "required": true},
      {"id": "field_2", "label": "Notice Period", "type": "select", "options": ["Immediate", "15 days", "30 days", "60+ days"], "required": true},
      {"id": "field_3", "label": "Are you comfortable working on-site in Noida?", "type": "radio", "options": ["Yes", "No"], "required": true}
    ],
    "action_buttons": [
      {"id": "btn_next", "text": "Save & Continue", "is_enabled": true}
    ],
    "validation_errors": []
  }
  ```

### 3.2 Dynamic Screening Question Solver
Company career portals ask varied questions. The Brain uses `MasterProfile` and LLM reasoning to determine the optimal response:
- **Radio / Checkbox Questions**: Automatically leans towards positive eligibility (e.g. "Yes" for legal right to work, "Yes" for location willingness, "No" for requiring sponsorship if applicable).
- **Compensation & Notice Period**: Pulls values from profile configuration (e.g. immediate or 15 days notice, standard market CTC expectations) rather than stalling.
- **Short-Answer / Motivation Questions**: Generates concise, professional answers highlighting candidate data skills without fluff.

### 3.3 Autonomous Self-Healing & Diagnostics
When any action fails to advance the page:
1. **Roadblock Detection**: Scans for:
   - `URL_DRIFT`: Browser jumped to an unintended page (e.g. company life page or home page). Remedy: `page.go_back()` or re-navigate to target job URL.
   - `VALIDATION_ERROR`: Required field skipped or format error. Remedy: Locate the highlighted red field, generate the correct value, and fill it.
   - `MODAL_OVERLAY`: Cookie banner, sign-in prompt, or feedback dialog blocking clicks. Remedy: Locate close/dismiss button or backdrop click.
   - `OBSCURED_BUTTON`: Button rendered below viewport or behind sticky footer. Remedy: `scrollIntoView()` and evaluate DOM dispatch.
2. **Verification Loop**: After executing a recovery action, inspects the page state after 1.5 seconds. If the blocker cleared, resumes the main flow.

### 3.4 Persistent Knowledge Memory (`storage/brain_memory.json`)
Saves site-specific heuristics and patterns:
- Domain-specific selectors: e.g. `{ "domain": "boards.greenhouse.io", "resume_input_selector": "input[type='file']", "submit_selector": "input[type='submit']" }`
- Avoids repeated LLM token usage on the same platform pattern.

---

## 4. Integration Points in AutoJobForge

1. **LinkedInApplier (`src/applier/linkedin.py`)**:
   - Acts as the first production harness for `BrowserBrain`.
   - Protects against description navigation bugs, obscured Easy Apply buttons, dynamic questions, and unexpected validation states.
2. **IndeedApplier (`src/applier/indeed.py`)**:
   - Uses `BrowserBrain` to handle Indeed's multi-step screening questions, salary input questions, and review steps.
3. **Future Company Portal Applier (`src/applier/company_portal.py`)**:
   - Built directly on top of `BrowserBrain` to navigate from job URLs directly into company ATS application forms.

---

## 5. Safety & Autonomy Controls

1. **Autonomy Guardrails**:
   - Maximum 3 self-healing attempts per step to prevent infinite loops.
   - Transparent console logs in `--mode review` detailing what the Brain diagnosed and what corrective action was taken.
2. **Review Mode Preservation**:
   - In review mode, before the final submission button is clicked on any platform, the Brain pauses for user inspection and confirmation.
3. **Receipt Capture**:
   - Captures screenshot verification upon submission on all platforms.

---

## 6. Implementation Plan & Deliverables

1. **`src/applier/brain.py`**:
   - Implements `BrowserBrain` class with perception, diagnosis, action execution, and memory caching.
2. **`src/ai/prompts.py`**:
   - Implements `BROWSER_BRAIN_SOLVER_PROMPT` and `BROWSER_BRAIN_DIAGNOSTIC_PROMPT`.
3. **Integration**:
   - Wire `BrowserBrain` into `LinkedInApplier` and `IndeedApplier`.
4. **Unit & Integration Tests**:
   - Tests in `tests/test_browser_brain.py` covering URL drift, form field mapping, unblocking, and persistent memory.
