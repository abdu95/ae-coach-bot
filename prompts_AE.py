ANALYSIS_PROMPT = """
You will receive a job description and a candidate CV (as a PDF document).

Analyze the CV carefully and return ONLY a valid JSON object with this exact structure.
No preamble, no markdown fences, no explanation — raw JSON only.

{
  "ats": {
    "score": <integer 0-100, how well the CV matches the JD keywords and requirements>,
    "matched": [<up to 8 keywords or phrases found in both JD and CV>],
    "missing": [<up to 8 important JD keywords or skills absent from CV>],
    "verdict": "<2-3 sentence honest ATS assessment — what passes, what fails, what to fix>"
  },
  "xyz": {
    "passing": [<bullet points from CV that follow Accomplished X as measured by Y by doing Z>],
    "failing": [<bullet points from CV that lack measurable impact or method>],
    "rewrites": [
      {"original": "<exact original bullet>", "improved": "<rewritten following X measured by Y by doing Z>"},
      {"original": "<exact original bullet>", "improved": "<rewritten following X measured by Y by doing Z>"}
    ]
  },
  "tools": {
    "Git": "<strong|mentioned|not_found>",
    "SQL": "<strong|mentioned|not_found>",
    "Python": "<strong|mentioned|not_found>",
    "dbt": "<strong|mentioned|not_found>",
    "data_warehouse": "<strong|mentioned|not_found>",
    "Cloud": "<strong|mentioned|not_found>"
  },
  "level": {
    "assessment": "<Pre-Junior|Junior|Mid|Senior>",
    "reasoning": "<2-3 sentences citing specific evidence from the CV — tools used, years of experience, production ownership, team scope>"
  }
}

Level criteria — be honest, do not inflate:
- Pre-Junior: student or career changer, no dbt or pipeline production experience. Forage simulations and virtual internships do NOT count as real AE experience.
- Junior (0-2 yrs AE): owns some dbt models in production, basic data modeling knowledge
- Mid (2-4 yrs AE): leads dbt projects in prod, solid dimensional modeling, pipeline ownership, stakeholder communication
- Senior (4+ yrs AE): leads data modeling strategy, mentors others, deep warehouse optimization, cross-team influence

Tool rating guide:
- strong: explicitly mentioned with context showing real usage (years, project, metric)
- mentioned: appears in CV but with no depth or context
- not_found: absent from CV entirely
"""

ROADMAP_PROMPT_PRE_JUNIOR = """
The candidate's CV and the target job description are attached.

CONTEXT:
- Candidate level: Pre-Junior (no Analytics Engineering production experience)
- Your task: identify the gap between what the JD requires and what the CV shows,
  then build a roadmap that closes that gap realistically within 3 months.

GAP ANALYSIS RULES:
- Every recommendation must be tied to a specific skill or tool the JD requires that the CV lacks
- Do not give generic advice — reference actual JD requirements and actual CV gaps
- Be honest: this candidate cannot apply to AE roles yet. The roadmap leads to stepping-stone roles first
- Forage simulations and virtual internships are not production experience — do not treat them as such

DEPTH FOR PRE-JUNIOR:
- Focus on foundational tools: SQL, dbt Core, BigQuery/Snowflake free tier, Git, Python basics
- One achievable portfolio project, not three — quality over quantity
- Stepping-stone roles only: Data Analyst, BI Analyst, Junior Data Engineer

Write a practical career roadmap using this exact structure:

### 3-Month Plan
Month 1 — Foundation:
- [action 1: specific skill from the JD gap, specific free resource, estimated hours per week]
- [action 2]
- [action 3]

Month 2 — Build:
- [action 1: start the portfolio project below, tied to JD requirements]
- [action 2]
- [action 3]

Month 3 — Ship & Apply:
- [action 1: finish and publish the project on GitHub]
- [action 2: start applying to stepping-stone roles below]
- [action 3]

### Portfolio Project
Name: [project name relevant to the JD domain]
Stack: [specific tools from the JD — use free tier e.g. dbt Core + BigQuery free tier]
Dataset: [specific public dataset with URL, relevant to JD industry if possible]
What to build: [3-4 sentences — exactly what to build, what transformations, what output]
What it demonstrates: [which specific JD requirements it proves to a hiring manager]
How to present: [how to write the GitHub README and how to add it to CV]

### Stepping-Stone Roles to Apply Now
Search for current openings the candidate can realistically get today (Data Analyst, BI Analyst,
Junior Data Engineer — not AE yet). List 4-5 roles with:
- Company name
- Role title
- Location
- One sentence why it is a realistic step toward the target AE role

Be specific and honest. Do not suggest roles requiring AE experience they do not have.
"""

ROADMAP_PROMPT_JUNIOR = """
The candidate's CV and the target job description are attached.

CONTEXT:
- Candidate level: Junior Analytics Engineer (0-2 years AE production experience)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then build a roadmap that directly closes that gap at Junior depth.

GAP ANALYSIS RULES:
- Only give advice tied to a specific missing skill or weakness relative to this JD
- Do not give generic AE advice — every recommendation must reference something the JD requires that the CV lacks
- Prioritise gaps by hiring impact: what would make or break getting this specific role
- Be honest about what is missing — do not soften gaps

DEPTH FOR JUNIOR LEVEL:
- CV fixes: focus on quantification and clarity, not leadership language
- Technical prep: foundational AE topics (basic dbt, SQL patterns, simple data modeling, pipeline basics)
- Target companies: similar or slightly easier roles than this JD, not above their level
- Phone screen: help them tell a clear story about real production work, even if limited

Write a focused job search roadmap using this exact structure:

### CV Fixes (Top 5)
1. [specific fix tied to a JD requirement the CV understates or misses — include before/after rewrite]
2.
3.
4.
5.

### Phone Screen Strategy
Opening line: [exact sentence to open "tell me about yourself" — must reference their strongest AE credential]
Key project to lead with: [which project from their CV, and why it maps to this JD]
How to handle gaps: [how to address missing JD requirements honestly without killing their chances]

### Technical Interview Prep
Topics to study in priority order (based on JD requirements the CV is weakest on):
1. [topic from JD gap + 1 practice question at Junior level]
2.
3.
4.
5.

### Target Companies
Search job boards for current Analytics Engineer openings matching this candidate's profile and skills.
List 6-8 companies with: company name, role title, location, one sentence why it fits their background.
"""

ROADMAP_PROMPT_MID = """
The candidate's CV and the target job description are attached.

CONTEXT:
- Candidate level: Mid Analytics Engineer (2-4 years AE production experience)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then build a roadmap that closes that gap at Mid level depth.

GAP ANALYSIS RULES:
- Only give advice tied to specific missing skills or weaknesses relative to this JD
- Do not give generic AE advice — every recommendation must be grounded in a JD requirement the CV lacks
- Prioritise gaps by hiring impact: ownership, stakeholder communication, data modeling depth
- At Mid level, gaps are often about demonstrating ownership and impact, not just tool knowledge

DEPTH FOR MID LEVEL:
- CV fixes: emphasise ownership, business impact, and cross-team work — not just task descriptions
- Technical prep: intermediate topics (dbt advanced features, dimensional modeling patterns,
  pipeline design decisions, warehouse optimisation basics)
- Target companies: roles at this JD's level or one step above
- Phone screen: help them show they can own work end-to-end, not just execute tickets

Write a focused job search roadmap using this exact structure:

### CV Fixes (Top 5)
1. [specific fix tied to a JD requirement the CV understates — include before/after rewrite showing ownership language]
2.
3.
4.
5.

### Phone Screen Strategy
Opening line: [exact sentence to open "tell me about yourself" — must signal ownership and impact immediately]
Key project to lead with: [which project shows end-to-end ownership most relevant to this JD]
How to position seniority: [how to show readiness to lead, not just contribute]

### Technical Interview Prep
Topics to study in priority order (based on JD requirements the CV is weakest on):
1. [topic from JD gap + 1 practice question at Mid level]
2.
3.
4.
5.

### Target Companies
Search job boards for current Mid or Senior Analytics Engineer openings matching this candidate.
List 6-8 companies with: company name, role title, location, one sentence why it fits.
"""

ROADMAP_PROMPT_SENIOR = """
The candidate's CV and the target job description are attached.

CONTEXT:
- Candidate level: Senior Analytics Engineer (4+ years AE production experience)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then build a roadmap that closes that gap at Senior depth.

GAP ANALYSIS RULES:
- Only give advice tied to specific missing signals relative to this JD
- At Senior level, gaps are usually about strategic scope, leadership narrative, and cross-org impact
  rather than tool knowledge — identify which type of gap this candidate has
- Do not give generic advice — reference specific JD requirements and specific CV weaknesses
- Be direct: if their CV reads like a Mid candidate, say so and fix it

DEPTH FOR SENIOR LEVEL:
- CV fixes: every bullet must show scope, influence, and business outcome — not just technical execution
- Technical prep: advanced topics (data platform architecture, modelling strategy trade-offs,
  warehouse cost optimisation, team mentorship, stakeholder alignment at director level)
- Target companies: Senior or Lead AE roles, possibly Staff at strong companies
- Phone screen: help them lead with strategic impact, not implementation details

Write a focused job search roadmap using this exact structure:

### CV Fixes (Top 5)
1. [specific fix focused on leadership scope and business impact — include before/after rewrite]
2.
3.
4.
5.

### Phone Screen Strategy
Opening line: [exact sentence to open "tell me about yourself" — must signal seniority and strategic scope immediately]
Key story to lead with: [which initiative shows cross-team leadership most relevant to this JD]
How to signal readiness for staff/lead: [specific language and framing tied to this JD's requirements]

### Technical Interview Prep
Topics to study in priority order (based on JD requirements the CV is weakest on):
1. [topic from JD gap + 1 practice question at Senior/Staff level]
2.
3.
4.
5.

### Target Companies
Search job boards for Senior or Lead Analytics Engineer openings matching this candidate.
List 6-8 companies with: company name, role title, location, one sentence why it fits.
"""


JOB_TITLE_PROMPT = """
Analyze this CV and suggest exactly 5 job titles this candidate is most suited for,
based on their domain, education, tools, and experience.

Return ONLY a JSON array of 5 strings. No preamble, no explanation.
Example: ["Analytics Engineer", "Data Engineer", "BI Developer", "Data Analyst", "Analytics Manager"]
"""

VACANCY_SEARCH_PROMPT = """
Search for currently active job postings matching these criteria:
- Job title: {job_title}
- Location: {location}
- Work setup: {work_setup}
- Industry: {industry}

Find 5 real, active job postings. For each return:
- company: company name
- title: exact job title
- location: city and country
- url: direct link to the job posting
- summary: 2-sentence description of the role

Return ONLY a JSON array of 5 objects with these exact keys.
No expired postings. No preamble. Raw JSON only.
"""


VACANCY_SEARCH_PROMPT = """
Search for ONE currently active job posting matching these criteria as closely as possible:
- Job title: {job_title}
- Location: {location}
- Work setup: {work_setup}
- Industry: {industry}

If you cannot find a perfect match, return the closest real active posting you can find.
A close match is better than no result. Do not invent postings.

{exclude}

Return ONLY a JSON object (not an array) with these exact keys:
{{
  "company": "company name",
  "title": "exact job title",
  "location": "city and country",
  "url": "direct link to the posting",
  "summary": "2-sentence role description"
}}

No preamble. Raw JSON only.
"""

VACANCY_SCORE_PROMPT = """
You will receive a candidate CV and a job description.

Compare them and return ONLY a JSON object:
{
  "score": <integer 0-100>,
  "matched": [<up to 6 keywords found in both CV and JD>],
  "missing": [<up to 6 important JD keywords absent from CV>],
  "verdict": "<1 sentence honest assessment>"
}

No preamble. Raw JSON only.
"""

ROADMAP_PROMPTS = {
    "Pre-Junior": ROADMAP_PROMPT_PRE_JUNIOR,
    "Junior": ROADMAP_PROMPT_JUNIOR,
    "Mid": ROADMAP_PROMPT_MID,
    "Senior": ROADMAP_PROMPT_SENIOR,
}