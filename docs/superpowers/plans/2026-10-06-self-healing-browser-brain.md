# Self-Healing Browser Brain Implementation Plan

> **For agentic workers:** Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a platform-agnostic, self-healing `BrowserBrain` agent that dynamically perceives forms, iframes, and interactive controls, uses Gemini to diagnose and resolve navigation/form blockers on the fly, and persists learned remedies in memory.

**Architecture:** A lightweight perceptual DOM/frame extractor captures interactive elements and error states; Gemini reasons over obstacles and produces actionable recovery instructions (navigate back, dismiss modal, answer dynamic question, scroll, or click); an action dispatcher executes remedies safely in Playwright; persistent memory caches recurring patterns in `storage/brain_memory.json`.

**Tech Stack:** Python 3.13, Playwright, Google Gemini via Google GenAI SDK, SQLite / JSON persistent cache, pytest.

---

### Task 1: Add Browser Brain Diagnostic and Solver Prompts

**Files:**
- Modify: `src/ai/prompts.py`
- Test: `tests/test_browser_brain.py`

- [ ] **Step 1: Define prompts in `src/ai/prompts.py`**
Add `BROWSER_BRAIN_DIAGNOSTIC_PROMPT` and `BROWSER_BRAIN_FORM_SOLVER_PROMPT` to `src/ai/prompts.py`.

- [ ] **Step 2: Commit prompts**
```bash
git add src/ai/prompts.py
git commit -m "feat(brain): add diagnostic and form solver prompts for browser brain"
```

---

### Task 2: Implement Perception and Persistent Memory in `BrowserBrain`

**Files:**
- Create: `src/applier/brain.py`
- Test: `tests/test_browser_brain.py`

- [ ] **Step 1: Write failing test for page state extraction and memory caching**
Test that `BrowserBrain.inspect_page_state()` normalizes interactive elements across main page and child frames, and that `save_learned_rule` / `get_learned_rule` persist correctly.

- [ ] **Step 2: Implement `BrowserBrain` perception methods and memory cache in `src/applier/brain.py`**
Implement frame traversal, interactive element extraction, dialog detection, validation error capture, and file-based JSON memory caching.

- [ ] **Step 3: Run unit tests to verify perception and caching pass**
```bash
pytest tests/test_browser_brain.py -k "test_perception or test_memory" -v
```

- [ ] **Step 4: Commit**
```bash
git add src/applier/brain.py tests/test_browser_brain.py
git commit -m "feat(brain): implement perception extractor and persistent memory store"
```

---

### Task 3: Implement Reasoning and Recovery Dispatcher in `BrowserBrain`

**Files:**
- Modify: `src/applier/brain.py`
- Test: `tests/test_browser_brain.py`

- [ ] **Step 1: Write unit tests for diagnosis and action execution**
Test `diagnose_and_heal` with simulated URL drift (recovery: `go_back`), modal overlay (recovery: `dismiss`), and missing field (recovery: `answer_field`).

- [ ] **Step 2: Implement `diagnose_and_heal` and `execute_action` in `src/applier/brain.py`**
Integrate `LLMClient.generate_json()` with `BROWSER_BRAIN_DIAGNOSTIC_PROMPT`, parse structured actions, dispatch Playwright interactions, and verify post-action state change.

- [ ] **Step 3: Run unit tests to verify diagnosis and execution pass**
```bash
pytest tests/test_browser_brain.py -v
```

- [ ] **Step 4: Commit**
```bash
git add src/applier/brain.py tests/test_browser_brain.py
git commit -m "feat(brain): implement diagnostic reasoning and recovery action dispatcher"
```

---

### Task 4: Integrate `BrowserBrain` into `LinkedInApplier` and `IndeedApplier`

**Files:**
- Modify: `src/applier/linkedin.py`
- Modify: `src/applier/indeed.py`
- Modify: `run.py`
- Test: `tests/test_applier_drivers.py`

- [ ] **Step 1: Initialize `BrowserBrain` and pass it to applier instances in `run.py`**
Instantiate `BrowserBrain(llm, master_profile)` and inject it into `LinkedInApplier` and `IndeedApplier`.

- [ ] **Step 2: Add self-healing hooks to `LinkedInApplier`**
Hook `self.brain.diagnose_and_heal()` on Easy Apply discovery, URL drift verification, and wizard step validation stall.

- [ ] **Step 3: Add self-healing hooks to `IndeedApplier`**
Hook `self.brain.diagnose_and_heal()` on multi-step question screening and resume confirmation.

- [ ] **Step 4: Run full test suite to ensure zero regressions**
```bash
pytest -v
```

- [ ] **Step 5: Commit**
```bash
git add src/applier/linkedin.py src/applier/indeed.py run.py
git commit -m "feat(applier): hook self-healing browser brain into LinkedIn and Indeed appliers"
```

---

### Task 5: Live Verification and Final Validation

**Files:**
- Test: Live headful test run on sample target job

- [ ] **Step 1: Run complete test suite**
Ensure all 20+ unit tests pass cleanly.

- [ ] **Step 2: Test live browser run with headful review mode**
```powershell
.\venv\Scripts\python.exe run.py --mode review --limit 1
```
Verify that the applier cleanly diagnoses and heals any unexpected page states, navigates with zero drift, and proceeds to the application form.

- [ ] **Step 3: Push changes to remote repository**
```bash
git push origin SH_AJ_V3
```
