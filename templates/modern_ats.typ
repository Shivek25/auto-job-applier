#set page(
  paper: "a4",
  margin: (x: 1.5cm, top: 1.2cm, bottom: 1.2cm),
)
#set text(
  font: ("Arial", "Liberation Sans", "DejaVu Sans"),
  size: 10pt,
  fill: rgb("#111827"),
)

#let cv_data = json("profile_data.json")

// Header
#align(center)[
  #text(18pt, weight: "bold")[#cv_data.personal_info.name] \
  #v(2pt)
  #text(9pt, fill: rgb("#4b5563"))[
    #cv_data.personal_info.location | #cv_data.personal_info.email | #cv_data.personal_info.phone \
    #if cv_data.personal_info.linkedin_url != none and cv_data.personal_info.linkedin_url != "" [#cv_data.personal_info.linkedin_url | ]
    #if cv_data.personal_info.github_url != none and cv_data.personal_info.github_url != "" [#cv_data.personal_info.github_url]
  ]
]

#v(6pt)
#line(length: 100%, stroke: 0.5pt + rgb("#d1d5db"))

// Professional Summary
#v(4pt)
#text(10.5pt, weight: "bold", fill: rgb("#1e3a8a"))[PROFESSIONAL SUMMARY]
#v(2pt)
#text(9.5pt)[#cv_data.summary]

// Technical Skills
#v(6pt)
#text(10.5pt, weight: "bold", fill: rgb("#1e3a8a"))[TECHNICAL SKILLS]
#v(2pt)
#if cv_data.skills.languages.len() > 0 [
  - *Languages:* #cv_data.skills.languages.join(", ")
]
#if cv_data.skills.frameworks.len() > 0 [
  - *Frameworks & Libraries:* #cv_data.skills.frameworks.join(", ")
]
#if cv_data.skills.tools_and_cloud.len() > 0 [
  - *Tools & Cloud:* #cv_data.skills.tools_and_cloud.join(", ")
]
#if cv_data.skills.databases.len() > 0 [
  - *Databases:* #cv_data.skills.databases.join(", ")
]

// Work Experience
#if cv_data.work_experience.len() > 0 [
  #v(6pt)
  #text(10.5pt, weight: "bold", fill: rgb("#1e3a8a"))[WORK EXPERIENCE]
  #v(2pt)
  #for exp in cv_data.work_experience [
    #grid(
      columns: (1fr, auto),
      [*#exp.role* - #exp.company],
      [#text(9pt, fill: rgb("#6b7280"))[#exp.start_date - #exp.end_date]]
    )
    #for bullet in exp.bullets [
      - #bullet
    ]
    #v(3pt)
  ]
]

// Projects
#if cv_data.projects.len() > 0 [
  #v(6pt)
  #text(10.5pt, weight: "bold", fill: rgb("#1e3a8a"))[KEY PROJECTS]
  #v(2pt)
  #for proj in cv_data.projects [
    #grid(
      columns: (1fr, auto),
      [*#proj.name* (#proj.tech_stack.join(", "))],
      [#if proj.github_link != none and proj.github_link != "" [#text(9pt, fill: rgb("#2563eb"))[#proj.github_link]]]
    )
    #for bullet in proj.bullets [
      - #bullet
    ]
    #v(3pt)
  ]
]

// Education
#if cv_data.education.len() > 0 [
  #v(6pt)
  #text(10.5pt, weight: "bold", fill: rgb("#1e3a8a"))[EDUCATION]
  #v(2pt)
  #for edu in cv_data.education [
    #grid(
      columns: (1fr, auto),
      [*#edu.degree* - #edu.institution],
      [#text(9pt, fill: rgb("#6b7280"))[#edu.graduation_year]]
    )
  ]
]
