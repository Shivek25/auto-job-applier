# Design Spec: Self-Healing Browser Brain (Agentic Recovery Layer)

Date: 2026-10-06
Author: Antigravity Pair Programmer
Status: Draft (Pending User Review)

---

## 1. Overview & Objective

### 1.1 Problem Statement
The current job applier uses static selectors and scripted logic for browser navigation and form traversal. When target platforms (such as LinkedIn or Indeed) change their DOM layout, alter class names to obfuscated strings, display unexpected overlays/modals, or navigate off-target, scripted steps fail and jobs get skipped with errors like "No Easy Apply button found" or "Element not attached to DOM".

### 1.2 Objective
Implement an autonomous, self-healing "Browser Brain" layer (`BrowserBrain`) that:
1. Keeps the high-speed, 0-token direct execution for standard steps.
2. Intercepts failures, missing elements, or unexpected page states immediately.
3. Inspects the live browser screen (URL, DOM accessibility tree, visible interactive controls, and screenshots).
4. Reasons using Gemini to diagnose the roadblock and determine a precise recovery action.
5. Executes the recovery action in the browser, verifies state transition, and resumes the application.
6. Persists learned recoveries in local cache (`storage/brain_memory.json`) to avoid repeated diagnosis.

---

## 2. Architecture & Components

```
+-------------------------------------------------------------------------+
|                         LinkedInApplier / IndeedApplier                 |
|                                                                         |
|  1. Fast Path: Standard Selector Action                                 |
|  2. Failure Intercepted? (Missing button, stuck wizard, URL drift)      |
+------------------------------------+------------------------------------+
                                     |
                          Trigger On Failure
                                     |
                                     v
+------------------------------------+------------------------------------+
|                      BrowserBrain (src/applier/brain.py)                |
|                                                                         |
|  A. Perception Module:                                                  |
|     - Verify URL matches job view (detect unintended redirects)         |
|     - Scan active modals / overlays (new obfuscated classes supported)  |
|     - Extract visible interactive elements (buttons, inputs, radios)   |
|     - Capture visual screenshot (for vision or diagnostic log)          |
|                                                                         |
|  B. Memory Query:                                                       |
|     - Check storage/brain_memory.json for known remedy for this pattern |
|                                                                         |
|  C. LLM Diagnostic & Decision Engine:                                   |
|     - Call Gemini with structured diagnosis prompt                      |
|     - Output: Diagnosis, Strategy, Action details, Learned rule         |
|                                                                         |
|  D. Action Dispatcher & Verification:                                   |
|     - Execute: navigate_back, dismiss_overlay, click_element,           |
|       fill_required_field, or wait_and_retry                            |
|     - Verify DOM state change                                           |
|     - Cache new learned rule to brain_memory.json                       |
+------------------------------------+------------------------------------+
                                     |
                          Resumes Normal Flow
                                     v
+-------------------------------------------------------------------------+
|                         Application Progress Continues                  |
+-------------------------------------------------------------------------+
```

---

## 3. Component Details

### 3.1 BrowserBrain (`src/applier/brain.py`)
The primary controller class responsible for diagnosing blockers and healing the browser session.

#### Key Methods:
- `diagnose_and_heal(page: Page, goal: str, context: dict) -> bool`:
  Main entry point. Given the current goal (e.g. `locate_easy_apply`, `advance_step`, `dismiss_blocking_modal`), inspects state, runs diagnosis, executes recovery, and returns whether recovery succeeded.
- `inspect_page_state(page: Page) -> dict`:
  Collects lightweight DOM summary:
  - `current_url`: string.
  - `page_title`: string.
  - `active_dialogs`: list of modal elements with text snippets.
  - `interactive_elements`: list of numbered buttons, inputs, radios, links with text, aria-labels, visibility, and bounding status.
  - `visible_error_messages`: list of red/validation error texts currently shown.
- `execute_action(page: Page, action: dict) -> bool`:
  Executes specific recovery action:
  - `NAVIGATE_BACK`: Calls `page.go_back()` when an unintended redirect occurred.
  - `DISMISS_OVERLAY`: Clicks dismiss/close on unexpected modals or backdrop.
  - `CLICK_ELEMENT`: Clicks element by text, role, or coordinate bounding box.
  - `ANSWER_FIELD`: Fills an unhandled required input/radio using candidate profile.
  - `SCROLL_INTO_VIEW`: Scrolls container or document to reveal obscured button.
- `save_learned_rule(pattern_key: str, remedy: dict)`:
  Writes learned rules to `storage/brain_memory.json` so known platform quirks execute instantly without querying the LLM next time.

### 3.2 Diagnostic Prompt (`src/ai/prompts.py`)
Add `BROWSER_BRAIN_DIAGNOSTIC_PROMPT` returning structured JSON:
```json
{
  "diagnosis": "The browser inadvertently navigated to the company life page rather than remaining on the job posting.",
  "obstacle_type": "URL_DRIFT",
  "recommended_strategy": "NAVIGATE_BACK",
  "action_details": {
    "action": "go_back"
  },
  "learned_rule": "Avoid clicking company life anchor links when expanding description"
}
```

### 3.3 Integration into `LinkedInApplier`
- Hook 1: **Easy Apply Discovery Recovery**:
  If `apply_btn` is not found, before marking as `SKIPPED`, call:
  `healed = await self.brain.diagnose_and_heal(page, goal="locate_easy_apply", context={"job_url": job_url, "company": company})`
  If healed, re-locate `apply_btn` and continue.
- Hook 2: **Wizard Step Unblocking**:
  In wizard loop, if `next_btn` is disabled or clicking `Next` produces validation errors:
  `healed = await self.brain.diagnose_and_heal(page, goal="unblock_wizard_step", context={"step": step})`
- Hook 3: **URL Sanity Guard**:
  Verify the page URL contains `linkedin.com/jobs/view` prior to attempting Easy Apply. If off-track, brain automatically recovers back to the job view.

---

## 4. Error Handling & Safety Guards

1. **Max Recovery Attempts**: Limit self-healing loop to at most 2 attempts per step to prevent infinite loops.
2. **Review Mode Safety**: When `--mode review` is active, the brain logs its diagnosis clearly to the console (e.g. `[BRAIN] Diagnosed URL drift: navigating back to job view...`).
3. **No Unintended Submissions**: The brain is NOT allowed to blindly submit. The final submission remains guarded by the standard review delay and verify receipt capture.
4. **Token Efficiency**: The lightweight DOM state extractor extracts only interactive elements and error messages (approx. 300 to 500 tokens), avoiding sending full HTML.

---

## 5. Testing Strategy

1. **Unit Tests (`tests/test_browser_brain.py`)**:
   - Mock Playwright page with simulated URL drift: assert brain detects drift and calls `go_back()`.
   - Mock page with validation error: assert brain identifies required input and fills it.
   - Mock page with persistent memory: assert brain uses cached remedy without calling LLM.
2. **Integration Verification**:
   - Test against live LinkedIn job URLs with headful browser in review mode.
