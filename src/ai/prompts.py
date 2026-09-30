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
You are an expert resume optimization consultant. 
Given the candidate's master profile and the target job description:
1. Rewrite the professional summary (2-3 sentences) to emphasize skills matching the JD.
2. Select the top 10-15 most relevant skills matching the JD without lying or fabricating experience.
3. Select the best 2-3 projects and tailor their bullet points using strong action verbs and metrics.
4. Slightly tune work experience bullet points to mirror JD terminology while strictly preserving truthfulness.

Return a JSON matching the Master Profile schema with the tailored fields.

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
