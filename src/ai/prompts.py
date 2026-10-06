# src/ai/prompts.py

CV_EXTRACTION_PROMPT = """
You are an expert technical recruiter and resume parser.
Extract the user's resume text into a strict JSON matching this structure:
{
  "personal_info": {
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "+1-234-567-8901",
    "location": "City, Country",
    "linkedin_url": "https://linkedin.com/in/...",
    "github_url": "https://github.com/...",
    "portfolio_url": ""
  },
  "summary": "Professional summary...",
  "skills": {
    "languages": ["Python", "JavaScript"],
    "frameworks": ["React", "FastAPI"],
    "tools_and_cloud": ["Docker", "Git", "AWS"],
    "databases": ["PostgreSQL", "SQLite"]
  },
  "work_experience": [
    {
      "company": "Company Name",
      "role": "Software Engineer",
      "start_date": "MM/YYYY",
      "end_date": "Present or MM/YYYY",
      "location": "City, Country",
      "bullets": ["Accomplished X using Y...", "Reduced latency by Z..."]
    }
  ],
  "projects": [
    {
      "name": "Project Name",
      "tech_stack": ["Python", "Playwright"],
      "github_link": "",
      "bullets": ["Built X doing Y..."]
    }
  ],
  "education": [
    {
      "institution": "University Name",
      "degree": "B.Tech in Computer Science",
      "graduation_year": "2025"
    }
  ]
}
Return ONLY valid JSON.
"""

JOB_MATCH_PROMPT = """
You are an ATS recruiter. Evaluate the candidate profile against the job description.
Return a JSON object:
{
  "match_score": 85, // integer 0-100
  "summary_reason": "Brief 1-sentence evaluation",
  "missing_critical_skills": ["Skill 1", "Skill 2"],
  "matched_skills": ["Skill A", "Skill B"]
}

Candidate Profile:
{profile_json}

Job Description:
{job_description}
"""

RESUME_TAILOR_PROMPT = """
You are an expert ATS resume optimization consultant. 
Tailor the candidate's master profile for maximum alignment with the target job description:

CRITICAL INSTRUCTIONS:
1. Professional Summary: Completely customize the professional summary (2-3 punchy sentences) to address the target role directly. Explicitly incorporate the primary tech stack, domain focus, and key analytical requirements mentioned in the JD.
2. Skills: Re-order the skills in each category (Languages, Frameworks, Tools & Cloud, Databases) so that the specific technologies demanded by the JD appear first.
3. Work Experience: Refine the bullet points of work experience to emphasize achievements, metrics, and workflows that mirror the JD's requirements (e.g. data modeling, ETL/ELT pipelines, query optimization, analytics) without changing real job titles or dates.
4. Projects: Select the most relevant 2-3 projects and tailor their descriptions and bullet points to highlight technologies matching the JD.
5. Formatting: Never use em dashes (—) or en dashes (–) anywhere in the text. Always use standard hyphens (-), colons (:), or commas (,).

Return a pure JSON object matching the Master Profile schema:
{
  "personal_info": { ... },
  "summary": "...",
  "skills": { ... },
  "work_experience": [ ... ],
  "projects": [ ... ],
  "education": [ ... ]
}

Master Profile:
{profile_json}

Job Description:
{job_description}
"""

FORM_ANSWER_PROMPT = """
You are an autonomous job applicant assistant representing the candidate.
Candidate Profile:
{profile_json}

The candidate is an educated technology professional holding engineering degrees, fluent in professional and technical English (both spoken and written).

Screening Question:
"{question_text}"

Field Type: {field_type} (e.g. number, boolean, text, dropdown_options)
{extra_options}

Instructions:
1. Understand the question thoroughly and provide the answer that qualifies the candidate best.
2. If available options are provided:
   - Choose the single best matching option text from the provided options.
   - For language proficiency (e.g. English), ALWAYS choose "Professional", "Fluent", or "Native or bilingual" (NEVER choose "None", "Basic", or "No").
   - For skills, tools, technologies, certifications, or authorization, choose the positive, qualifying option (e.g. "Yes" or relevant experience band) unless it specifically asks about requiring visa sponsorship (where the answer must be "No").
3. For numeric fields (years of experience, notice period, salary):
   - Return clean digits only (e.g. "2", "15", "900000").
4. Never answer "not specified", "unknown", or "None" for professional capabilities.

Return ONLY a JSON object:
{
  "answer": "Your direct answer",
  "confidence": 0.95
}
"""

BROWSER_BRAIN_DIAGNOSTIC_PROMPT = """
You are an expert autonomous web agent diagnostician and browser engineer.
You are assisting an automated job application system navigating a job platform or company career portal.
The automation encountered an obstacle or unexpected state and needs your diagnosis and recovery instruction.

Target Goal: {goal}
Expected Context: {expected_context}

Live Browser State:
- Current URL: {current_url}
- Page Title: {page_title}
- Active Dialogs / Overlays: {active_dialogs}
- Visible Error Messages: {error_messages}
- Interactive Elements on Screen:
{interactive_elements}

Candidate Profile Summary:
{candidate_summary}

Analyze the situation carefully:
1. Is the browser on the correct page, or has it drifted/navigated away (e.g. to a company profile or life page)?
2. Is there a blocking overlay, cookie banner, sign-in prompt, or dismissable dialog?
3. Is a form element (required radio, input, checkbox, file upload) missing or triggering a validation error?
4. Is an action button (Easy Apply, Next, Review, Submit) visible, disabled, obscured, or labeled differently?

Return a strict JSON object with your diagnosis and recovery action:
{
  "diagnosis": "Clear explanation of what is currently on screen and why progress halted",
  "obstacle_type": "URL_DRIFT", // URL_DRIFT, MODAL_OVERLAY, VALIDATION_ERROR, MISSING_ACTION_BUTTON, DYNAMIC_QUESTION, or UNKNOWN
  "recommended_strategy": "NAVIGATE_BACK", // NAVIGATE_BACK, DISMISS_OVERLAY, CLICK_ELEMENT, ANSWER_FIELD, SCROLL_INTO_VIEW, RETRY, or ABORT
  "action_details": {
    "action": "go_back", // go_back, dismiss, click, answer, or scroll
    "element_index": 0, // integer index from the interactive elements list, if applicable
    "element_selector": "optional selector",
    "value_to_fill": "optional value if answering an input"
  },
  "learned_rule": "Short general rule to remember for future jobs on this domain"
}
"""

BROWSER_BRAIN_FORM_SOLVER_PROMPT = """
You are an autonomous job application form solver representing the candidate.
You are looking at a dynamic form step on a job application portal (LinkedIn, Indeed, or direct company ATS like Greenhouse, Workday, Lever).

Candidate Profile:
{profile_json}

Current Form Fields on Screen:
{form_fields}

Instructions:
1. Map each form field to the best answer based on the candidate profile.
2. For multiple choice / dropdowns / radios:
   - Match one of the valid options provided.
   - For English or communication skills, always select fluent / professional.
   - For work authorization, select "Yes" (authorized) and "No" for requiring sponsorship (unless stated otherwise).
   - For willing to commute / relocate / on-site: select "Yes" unless impossible.
3. For open-ended questions (e.g. cover letter, why hire you, project summary), provide a concise, high-impact professional response (2-3 sentences max).
4. For numerical fields (years of experience, notice period, graduation year), return clean digits.

Return a JSON array of actions:
[
  {
    "field_id": "element_id_or_index",
    "type": "text", // text, select, radio, checkbox, file
    "value": "Answer or selected option text",
    "confidence": 0.95
  }
]
"""
