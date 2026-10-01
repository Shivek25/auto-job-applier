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
You are an automated job applicant assistant. 
Answer the following screening question based STRICTLY on the candidate's profile:
Candidate Profile:
{profile_json}

Question:
"{question_text}"

Field Type: {field_type} (e.g. number, boolean, text, dropdown_options)
{extra_options}

Return ONLY a JSON object:
{
  "answer": "Your direct answer", // string, number, or exact option text
  "confidence": 0.95
}
"""
