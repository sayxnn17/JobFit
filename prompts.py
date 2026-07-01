from typing import Literal
from models import ResumeMatch, Requirement, ATSScore, SWOTAnalysis

def requirement_extraction_function(job_description: str) -> str:
    return f"""
    You are an information extraction system.

    Your task is to extract every hiring requirement from the following job description.
    Return ONLY valid JSON.

    The output MUST be exactly in this format:

    {{
    "requirements": [
        {{
        "text": "example requirement",
        "importance": "required"
        }}
    ]
    }}

    Rules:
    - The top-level object MUST contain only one key: "requirements".
    - Do not return a bare list.
    - Do not return a single object.
    - Every element inside "requirements" must contain only:
    - text
    - importance
    - Return ONLY data matching the provided output schema.
    - Do NOT create your own JSON structure.
    - Do NOT add extra fields.
    - Every requirement must contain:
    - text
    - importance
    - importance must be either "required" or "preferred".
    - If the JD does not explicitly state that something is preferred, classify it as "required".
    - Do not output explanations, markdown, or prose.

    Job Description:
    {job_description}
    """

def requirement_match_function(requirement_text: str, requirement_importance: Literal["required", "preferred"], content: str) -> str:
    return f"""
        Job requirement: {requirement_text}
        requirement importance: {requirement_importance}
        Resume evidence: {content}

        Return ONLY valid JSON.

        The JSON must have exactly these fields:

        {{
        "requirement": "<job requirement>",
        "importance": "required",
        "match_status": "strong_match",
        "confidence": 95,
        "evidence": "<exact quote from resume>",
        "explanation": "<brief explanation>"
        }}

        Rules:
        - Do not add extra fields.
        - Do not omit required fields.
        - match_status must be exactly one of:
        - strong_match
        - partial_match
        - missing
        - importance must be exactly one of:
        - required
        - preferred
        - confidence must be an integer from 0 to 100.
        - evidence must be a string or null.
        - Return only the JSON object.

        Determine whether the candidate has a:
        1.  strong_match: Only when the resume shows exlpicit evidence.
        2.  partial_match: When the resume shows related evidence but not direct evidence.
        3.  missing: No mention of direct or related evidence present.

        Rules:
        1.  Only assume the resume evidence
        2.  Do NOT assume achievements
        3.  Missing means that there is no evidence.
        4. If the requirement mentions quantity(years, count, degree level), then explicitly verify whether the quantity is supported or not. Otherwise downgrade the match level to partial_match.
        5. For "missing" matches, leave the "evidence" field blank.
        """

def keyword_extraction_function(job_description: str) -> str:
    return f"""
    You are an information extraction system.

    Your task is to extract all important keywords from the given job description.

    Return ONLY valid JSON.

    The output MUST be exactly in this format:

    {{
    "keywords": [
        "<keyword 1>",
        "<keyword 2>",
        "<keyword 3>"
    ]
    }}

    Rules:
    - The top-level object must contain ONLY one key: "keywords".
    - "keywords" must be a list of strings.
    - Do NOT return objects inside the list.
    - Do NOT group keywords by category.
    - Do NOT create additional fields.
    - Do NOT output explanations, markdown, headings or prose.
    - Remove duplicate keywords.
    - Preserve the wording used in the job description whenever possible.

    Include:
    - Programming languages
    - Technologies
    - Frameworks
    - Libraries
    - Tools
    - Cloud platforms
    - Databases
    - DevOps tools
    - Testing methodologies
    - Software engineering practices
    - Architectural concepts
    - Educational qualifications
    - Certifications
    - Domain-specific concepts
    - Important soft skills

    Ignore:
    - Company names
    - Generic filler words
    - Complete sentences
    - Responsibilities that are not skills or qualifications

    Job Description:
    {job_description}
    """

def keyword_match_function(context: str, keyword: str) -> str:
    return f"""
    You are an ATS keyword matching system.

    Your task is to determine whether the given keyword is present in the resume.

    Return ONLY valid JSON.

    The output MUST be exactly in this format:

    {{
    "keyword": "<input keyword>",
    "match_status": "present",
    "evidence": "<exact quote from the resume>"
    }}

    Rules:
    - The output must contain EXACTLY these three fields:
    - keyword
    - match_status
    - evidence
    - Do NOT add extra fields.
    - Do NOT output markdown, explanations, or prose.
    - Copy the input keyword exactly.
    - match_status must be exactly one of:
    - present
    - related
    - missing

    Evaluation Rules:
    1. "present"
    - The exact keyword appears in the resume.
    - Evidence must be the exact text from the resume containing the keyword.

    2. "related"
    - The exact keyword does not appear.
    - A closely related technology, framework, methodology or concept appears.
    - Do NOT consider unrelated technologies as related.
    - Evidence must be the exact supporting text.

    3. "missing"
    - Neither the keyword nor any closely related concept appears.
    - Set evidence to null.

    Important Rules:
    - Only use the provided resume context.
    - Never invent evidence.
    - Never infer missing skills.
    - Never use outside knowledge about the candidate.
    - If uncertain, return "missing".

    Resume Context:
    {context}

    Input Keyword:
    {keyword}
    """

def swot_function(strengths: ResumeMatch, weaknesses: ResumeMatch, opportunities: ResumeMatch, threats: ResumeMatch) -> str:
    return f"""
    You are an expert ATS evaluator and career coach.

    Your task is to generate a SWOT analysis for the candidate.

    Return ONLY valid JSON.

    The output MUST be exactly in this format:

    {{
    "strengths": [
        "<strength 1>",
        "<strength 2>"
    ],
    "weaknesses": [
        "<weakness 1>"
    ],
    "opportunities": [
        "<opportunity 1>"
    ],
    "threats": [
        "<threat 1>"
    ]
    }}

    Rules:
    - The output must contain EXACTLY these four fields:
    - strengths
    - weaknesses
    - opportunities
    - threats
    - Every field must be a list of strings.
    - Do NOT add extra fields.
    - Do NOT output markdown, explanations or prose.

    Use ONLY the candidate analysis data provided below.

    Candidate Analysis Data

    Strong Matches:
    {strengths}

    Partial Matches:
    {weaknesses}

    Missing Preferred Requirements:
    {opportunities}

    Missing Required Requirements:
    {threats}

    Interpretation Rules:

    Strengths
    - Convert each strong match into a concise strength.
    - Mention only demonstrated qualifications.
    - Do NOT exaggerate or invent achievements.

    Weaknesses
    - Convert each partial match into a concise weakness.
    - Explain only the missing aspect of the partially satisfied requirement.
    - Do NOT repeat strengths.

    Opportunities
    - Convert each missing preferred requirement into an improvement opportunity.
    - Focus on skills or experience that are realistically attainable.
    - Phrase them as opportunities for growth.

    Threats
    - Convert each missing required requirement into a hiring risk.
    - Focus on requirements that may reduce interview chances.
    - Do NOT suggest solutions here.

    Quality Rules
    - Every item must be one concise sentence.
    - Avoid duplicates across all four sections.
    - Do not repeat the same requirement using different wording.
    - Preserve the meaning of the input.
    - Do not invent facts.
    - Do not recommend technologies not present in the analysis data.
    - If a section has no items, return an empty list.
    """

def fetch_parts_function(resume_text: str) -> str:
    return f"""
    You are an information extraction system.

    Return ONLY valid JSON.

    The JSON MUST be exactly:

    {{
    "parts": [
        {{
        "section": "projects",
        "original_text": "..."
        }}
    ]
    }}

    Rules:

    - The top-level object must contain ONLY one field:
    "parts"

    - "parts" must be a list.

    - Every list element must contain EXACTLY:
    - section
    - original_text

    - section must be exactly one of:
    - "projects"
    - "work_experience"
    - "achievements"

    - original_text must be one complete bullet from the resume.

    - Ignore:
    - Education
    - Skills
    - Certifications
    - Languages
    - Contact information

    - Do not summarize.
    - Do not rewrite.
    - Do not merge bullets.
    - Copy the original text exactly.

    Resume:

    {resume_text}
    """

def improvement_function(requirements_extracted_requirements: list[Requirement], unmet_requirements: list[ResumeMatch], missing_keywords: list[str], part_section: Literal["projects", "work_experience", "achievements"], part_original_text: str):
    return f"""
    You are an expert resume writer and ATS optimization specialist.

    Your task is to improve ONE resume bullet.

    Return ONLY valid JSON matching the provided output schema.

    The output must have exactly these fields:

    {{
        "original_text": "...",
        "improved_text": "...",
        "missing_information": [
            "...",
            "..."
        ],
        "relevance_to_jd": "..."
    }}

    Do NOT add extra fields.

    -----------------------------
    Target Job Requirements
    -----------------------------
    {requirements_extracted_requirements}

    Missing or Partial Requirements
    -----------------------------
    {unmet_requirements}

    Missing Keywords
    -----------------------------
    {missing_keywords}

    Resume Section
    -----------------------------
    {part_section}

    Original Resume Bullet
    -----------------------------
    {part_original_text}

    Your task:

    Rewrite ONLY the given resume bullet.

    Rules:

    1. Preserve every factual statement.
    2. Do NOT invent technologies.
    3. Do NOT invent metrics.
    4. Do NOT invent user counts.
    5. Do NOT invent years of experience.
    6. Do NOT invent certifications.
    7. Do NOT invent deployment environments.
    8. Do NOT invent responsibilities.
    9. Do NOT invent achievements.
    10. Every statement in improved_text must be directly inferable from the original text.
    11. Improve clarity, technical specificity and ATS readability.
    12. Use stronger action verbs.
    13. Use concise professional resume language.
    14. If technologies are already mentioned, place them naturally within the bullet.
    15. Remove unnecessary filler words.
    16. Keep the bullet approximately the same length.
    17. If important information is missing but cannot be inferred, DO NOT add it to improved_text.
    18. Instead, list it under missing_information.
    19. Tailor wording toward the target job only when supported by the original text.
    20. Never claim the candidate has experience they do not explicitly demonstrate.

    Section-specific guidance:

    Projects
    - Emphasize implementation details.
    - Mention architecture, algorithms and technologies only if present.
    - Highlight technical complexity.

    Work Experience
    - Emphasize responsibilities, ownership and measurable impact.
    - Improve professional wording.

    Achievements
    - Emphasize accomplishment, recognition and significance.
    - Do not exaggerate impact.

    Field requirements:

    original_text
    - Copy the original bullet exactly.

    improved_text
    - Produce a single improved bullet.

    missing_information
    - List only information that would genuinely strengthen the bullet but is absent.
    - Examples:
    - performance metrics
    - scale
    - deployment details
    - testing methodology
    - architecture decisions
    - business impact
    - Return an empty list if nothing important is missing.

    relevance_to_jd
    - Explain in one or two concise sentences why the rewritten bullet is better aligned with the job description.
    """

def roadmap_function(requirements_extracted_requirements: list[Requirement], overall_ats_score: ATSScore, requirements_match_details: list[ResumeMatch], missing_keywords: list[str], swot_result: SWOTAnalysis, content_improvements: list[dict]):
    return f"""
    You are an expert ATS consultant and career coach.

    Generate a personalized resume improvement roadmap.

    Return ONLY valid JSON matching the provided output schema.

    The JSON must contain exactly these fields:
    - immediate_actions
    - short_term_actions
    - long_term_actions

    Each action must contain exactly:
    - action
    - priority
    - reason

    Candidate Data

    Target Job Requirements:
    {requirements_extracted_requirements}

    ATS Score:
    {overall_ats_score}

    Requirement Analysis:
    {requirements_match_details}

    Missing Keywords:
    {missing_keywords}

    SWOT Analysis:
    {swot_result}

    Resume Content Improvements:
    {content_improvements}

    Task

    Create the minimum set of actions that will produce the maximum increase in ATS score and interview readiness.

    Guidelines

    Immediate Actions (within 1 week)
    - Resume rewrites
    - Resume restructuring
    - Keyword optimization
    - Better project descriptions
    - Add missing information already supported by existing experience

    Short Term Actions (1-3 weeks)
    - Small portfolio projects
    - Certifications
    - Demonstrate partially missing skills
    - Improve GitHub/portfolio

    Long Term Actions (>3 weeks)
    - Learn missing required technologies
    - Build advanced projects
    - Gain missing experience
    - Develop skills that cannot be added through resume editing

    Priority Rules

    high
    - Missing required requirement
    - Major ATS impact
    - Interview blocker

    medium
    - Partial matches
    - Missing preferred requirements
    - Competitive advantage

    low
    - Cosmetic improvements
    - Minor optimizations

    Quality Rules

    - Every recommendation must address an identified gap.
    - Do not recommend skills already strongly demonstrated.
    - Do not duplicate recommendations.
    - Prefer project-based recommendations over generic learning advice.
    - Explain why each recommendation improves alignment with the job.
    - Be specific.
    - Do not invent candidate experience.
    - Keep action statements concise.
    - Keep reasons to one or two sentences.
    - If a category has no recommendations, return an empty list.
    """