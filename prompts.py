ANALYSIS_PROMPT = """
You will receive a job description (JD) and a candidate CV (as text).

STEP 1 — Identify the TARGET ROLE from the JD (e.g. Data Analyst, Data Engineer,
Analytics Engineer, BI Developer, Data Scientist, or whatever the JD describes).
Assess everything below RELATIVE TO THAT ROLE — not a generic standard, and not
Analytics Engineer unless that is the actual role in the JD.

Return ONLY a valid JSON object with this exact structure.
No preamble, no markdown fences, no explanation — raw JSON only.

{
  "ats": {
    "score": <integer 0-100, how well the CV matches THIS JD's keywords and requirements>,
    "matched": [<up to 8 keywords or phrases found in both JD and CV>],
    "missing": [<up to 8 important JD keywords or skills absent from CV>],
    "verdict": "<2-3 sentence honest ATS assessment for this specific role>"
  },
  "xyz": {
    "passing": [<CV bullets that follow: Accomplished X as measured by Y by doing Z>],
    "failing": [<CV bullets that lack measurable impact or method>],
    "rewrites": [
      {"original": "<exact original bullet>", "improved": "<rewritten as X measured by Y by doing Z>"},
      {"original": "<exact original bullet>", "improved": "<rewritten as X measured by Y by doing Z>"}
    ]
  },
  "tools": {
    "<tool or skill 1 from the JD>": "<strong|mentioned|not_found>",
    "<tool or skill 2 from the JD>": "<strong|mentioned|not_found>",
    "<tool or skill 3 from the JD>": "<strong|mentioned|not_found>",
    "<tool or skill 4 from the JD>": "<strong|mentioned|not_found>",
    "<tool or skill 5 from the JD>": "<strong|mentioned|not_found>",
    "<tool or skill 6 from the JD>": "<strong|mentioned|not_found>"
  },
  "level": {
    "assessment": "<Pre-Junior|Junior|Mid|Senior>",
    "reasoning": "<2-3 sentences citing specific CV evidence, judged against THIS role>"
  }
}

For the "tools" object: pick the 6 most important tools, technologies, or skills that
THIS JD actually requires, and rate the candidate on each. Do NOT use a fixed list —
derive the 6 from the JD. Keep each name short (1-3 words).

Level criteria — be honest, do not inflate (apply relative to the target role):
- Pre-Junior: student or career changer with no real production experience in this role's
  domain. Forage simulations, virtual internships, and course projects do NOT count as
  real experience.
- Junior (0-2 yrs): some production experience, executes defined tasks, still learning the craft
- Mid (2-4 yrs): owns projects end to end, solid domain knowledge, works with stakeholders
- Senior (4+ yrs): leads strategy, mentors others, cross-team influence, deep expertise

Tool rating guide:
- strong: explicitly mentioned with context showing real usage (years, project, or metric)
- mentioned: appears in the CV but with no depth or context
- not_found: absent from the CV entirely
"""


NO_PREAMBLE = (
    "Do not add a title, introduction, or 'target role analysis' section, and do not "
    "restate the JD. Start your reply directly with the heading below — nothing before it."
)


# ── Pre-Junior ─────────────────────────────────────────────────────────────────

ROADMAP_PRE_JUNIOR_CONTEXT = """
CONTEXT:
- First identify the target role from the JD (Data Analyst, Data Engineer, BI Developer, etc.)
- Candidate level: Pre-Junior (no real production experience in this role's domain)
- Your task: identify the gap between what the JD requires and what the CV shows,
  then close that gap realistically within 3 months.

GAP ANALYSIS RULES:
- Every recommendation must tie to a specific skill or tool THIS JD requires that the CV lacks
- Do not give generic advice — reference actual JD requirements and actual CV gaps
- Be honest: this candidate cannot land the target role yet — this plan leads to a
  stepping-stone role first
- Simulations and course projects are not production experience — do not treat them as such
"""

ROADMAP_PRE_JUNIOR_ITEM1 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_PRE_JUNIOR_CONTEXT}
{NO_PREAMBLE}

Write ONLY this section:

### 3-Month Plan
Month 1 — Foundation:
- [action 1: specific skill from the JD gap, specific free resource, hours per week]
- [action 2]
- [action 3]

Month 2 — Build:
- [action 1: start a portfolio project tied to JD requirements]
- [action 2]
- [action 3]

Month 3 — Ship & Apply:
- [action 1: finish and publish the project]
- [action 2: start applying to stepping-stone roles]
- [action 3]
"""

ROADMAP_PRE_JUNIOR_ITEM2 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_PRE_JUNIOR_CONTEXT}
DEPTH: one achievable portfolio project, not three — quality over quantity.
{NO_PREAMBLE}

Write ONLY this section:

### Portfolio Project
Name: [project name relevant to the JD domain]
Stack: [specific tools from the JD — free tier where possible]
Dataset: [specific public dataset with URL, relevant to the JD industry if possible]
What to build: [3-4 sentences — exactly what to build]
What it demonstrates: [which specific JD requirements it proves]
How to present: [GitHub README structure and how to add it to the CV]
"""

ROADMAP_PRE_JUNIOR_ITEM3 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_PRE_JUNIOR_CONTEXT}
{NO_PREAMBLE}

Write ONLY this section:

### Stepping-Stone Roles
Suggest 4-5 realistic role types the candidate could land now (a more junior or adjacent
version of the target role). For each: role title, why it is a realistic step, what to highlight.
"""


# ── Junior ───────────────────────────────────────────────────────────────────

ROADMAP_JUNIOR_CONTEXT = """
CONTEXT:
- First identify the target role from the JD.
- Candidate level: Junior (0-2 years production experience in this role's domain)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then close that gap at Junior depth.

GAP ANALYSIS RULES:
- Only give advice tied to a specific missing skill or weakness relative to THIS JD
- Do not give generic advice — every recommendation must reference something the JD requires
  that the CV lacks
- Prioritise gaps by hiring impact: what would make or break getting this specific role
- Be honest about what is missing — do not soften gaps
"""

ROADMAP_JUNIOR_ITEM1 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_JUNIOR_CONTEXT}
DEPTH: focus on quantification and clarity, not leadership language.
{NO_PREAMBLE}

Write ONLY this section:

### CV Fixes (Top 5)
1. [specific fix tied to a JD requirement the CV understates or misses — include before/after rewrite]
2.
3.
4.
5.
"""

ROADMAP_JUNIOR_ITEM2 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_JUNIOR_CONTEXT}
DEPTH: foundational technical topics relevant to THIS role; help them tell a clear
story about real work, even if limited.
{NO_PREAMBLE}

Write ONLY these two sections:

### Phone Screen Strategy
Opening line: [exact sentence to open "tell me about yourself" — referencing their strongest credential]
Key project to lead with: [which CV project, and why it maps to this JD]
How to handle gaps: [how to address missing JD requirements honestly without killing their chances]

### Technical Interview Prep
Topics to study in priority order (based on JD requirements the CV is weakest on):
1. [topic from JD gap + 1 practice question at Junior level]
2.
3.
4.
5.
"""

ROADMAP_JUNIOR_ITEM3 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_JUNIOR_CONTEXT}
{NO_PREAMBLE}

Write ONLY this section:

### Target Companies
Suggest 6-8 companies or role types matching this candidate's profile and the target role.
For each: company or role type, location if relevant, one sentence why it fits.
"""


# ── Mid ──────────────────────────────────────────────────────────────────────

ROADMAP_MID_CONTEXT = """
CONTEXT:
- First identify the target role from the JD.
- Candidate level: Mid (2-4 years production experience in this role's domain)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then close that gap at Mid depth.

GAP ANALYSIS RULES:
- Only give advice tied to specific missing skills or weaknesses relative to THIS JD
- Do not give generic advice — every recommendation grounded in a JD requirement the CV lacks
- Prioritise gaps by hiring impact: ownership, stakeholder communication, depth of craft
- At Mid level, gaps are often about demonstrating ownership and impact, not just tool knowledge
"""

ROADMAP_MID_ITEM1 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_MID_CONTEXT}
DEPTH: emphasise ownership, business impact, and cross-team work — not just task descriptions.
{NO_PREAMBLE}

Write ONLY this section:

### CV Fixes (Top 5)
1. [specific fix tied to a JD requirement — include before/after rewrite showing ownership language]
2.
3.
4.
5.
"""

ROADMAP_MID_ITEM2 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_MID_CONTEXT}
DEPTH: intermediate technical topics relevant to THIS role; help them show they can own
work end to end, not just execute tickets.
{NO_PREAMBLE}

Write ONLY these two sections:

### Phone Screen Strategy
Opening line: [exact sentence to open "tell me about yourself" — signalling ownership and impact]
Key project to lead with: [which project shows end-to-end ownership most relevant to this JD]
How to position seniority: [how to show readiness to lead, not just contribute]

### Technical Interview Prep
Topics to study in priority order (based on JD requirements the CV is weakest on):
1. [topic from JD gap + 1 practice question at Mid level]
2.
3.
4.
5.
"""

ROADMAP_MID_ITEM3 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_MID_CONTEXT}
{NO_PREAMBLE}

Write ONLY this section:

### Target Companies
Suggest 6-8 companies or role types at this JD's level or one step above.
For each: company or role type, location if relevant, one sentence why it fits.
"""


# ── Senior ───────────────────────────────────────────────────────────────────

ROADMAP_SENIOR_CONTEXT = """
CONTEXT:
- First identify the target role from the JD.
- Candidate level: Senior (4+ years production experience in this role's domain)
- Your task: identify the gap between what the JD requires and what the CV demonstrates,
  then close that gap at Senior depth.

GAP ANALYSIS RULES:
- Only give advice tied to specific missing signals relative to THIS JD
- At Senior level, gaps are usually about strategic scope, leadership narrative, and
  cross-org impact rather than tool knowledge — identify which type of gap this candidate has
- Do not give generic advice — reference specific JD requirements and specific CV weaknesses
- Be direct: if the CV reads like a Mid candidate, say so and fix it
"""

ROADMAP_SENIOR_ITEM1 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_SENIOR_CONTEXT}
DEPTH: every bullet must show scope, influence, and business outcome — not just execution.
{NO_PREAMBLE}

Write ONLY this section:

### CV Fixes (Top 5)
1. [specific fix focused on leadership scope and business impact — include before/after rewrite]
2.
3.
4.
5.
"""

ROADMAP_SENIOR_ITEM2 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_SENIOR_CONTEXT}
DEPTH: advanced technical topics relevant to THIS role, plus leadership and stakeholder
alignment; help them lead with strategic impact, not implementation details.
{NO_PREAMBLE}

Write ONLY these two sections:

### Phone Screen Strategy
Opening line: [exact sentence to open "tell me about yourself" — signalling seniority and scope]
Key story to lead with: [which initiative shows cross-team leadership most relevant to this JD]
How to signal readiness for staff/lead: [specific language and framing tied to this JD]

### Technical Interview Prep
Topics to study in priority order (based on JD requirements the CV is weakest on):
1. [topic from JD gap + 1 practice question at Senior/Staff level]
2.
3.
4.
5.
"""

ROADMAP_SENIOR_ITEM3 = f"""
The candidate's CV and the target job description (JD) are provided.
{ROADMAP_SENIOR_CONTEXT}
{NO_PREAMBLE}

Write ONLY this section:

### Target Companies
Suggest 6-8 companies or role types at Senior or Lead level.
For each: company or role type, location if relevant, one sentence why it fits.
"""


JOB_TITLE_PROMPT = """
Analyze this CV and suggest exactly 5 job titles this candidate is most suited for,
based on their domain, education, tools, and experience.

Return ONLY a JSON array of 5 strings. No preamble, no explanation.
Example: ["Data Analyst", "Analytics Engineer", "Data Engineer", "BI Developer", "Data Scientist"]
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


ROADMAP_BLOCKS = {
    "Pre-Junior": {
        1: {"title": "3-Month Plan", "prompt": ROADMAP_PRE_JUNIOR_ITEM1},
        2: {"title": "Portfolio Project", "prompt": ROADMAP_PRE_JUNIOR_ITEM2},
        3: {"title": "Stepping-Stone Roles", "prompt": ROADMAP_PRE_JUNIOR_ITEM3},
    },
    "Junior": {
        1: {"title": "CV Fixes", "prompt": ROADMAP_JUNIOR_ITEM1},
        2: {"title": "Interview Prep", "prompt": ROADMAP_JUNIOR_ITEM2},
        3: {"title": "Target Companies", "prompt": ROADMAP_JUNIOR_ITEM3},
    },
    "Mid": {
        1: {"title": "CV Fixes", "prompt": ROADMAP_MID_ITEM1},
        2: {"title": "Interview Prep", "prompt": ROADMAP_MID_ITEM2},
        3: {"title": "Target Companies", "prompt": ROADMAP_MID_ITEM3},
    },
    "Senior": {
        1: {"title": "CV Fixes", "prompt": ROADMAP_SENIOR_ITEM1},
        2: {"title": "Interview Prep", "prompt": ROADMAP_SENIOR_ITEM2},
        3: {"title": "Target Companies", "prompt": ROADMAP_SENIOR_ITEM3},
    },
}