from models import Requirement, JDRequirements, ResumeMatch, KeywordExtract, KeywordMatch, ATSScore, SWOTAnalysis, ResumeContentGap, ResumeParts, ResumePartsList, Action, Roadmap, FinalReport
from prompts import requirement_extraction_function, requirement_match_function, keyword_extraction_function, keyword_match_function, swot_function, fetch_parts_function, improvement_function, roadmap_function

# 1
def extract_requirements(inputs: dict):
    model = inputs["model"]
    job_description = inputs["job_description"]

    requirements_extraction_model = model.with_structured_output(JDRequirements, method = "json_mode")
    requirement_extraction_prompt = requirement_extraction_function(job_description)
    requirements_extracted = requirements_extraction_model.invoke(requirement_extraction_prompt)

    return {
        **inputs,
        "requirements_extracted": requirements_extracted
    }

# 2
def match_requirements(inputs: dict):
    requirements_extracted = inputs["requirements_extracted"]
    model = inputs["model"]
    retriever = inputs["retriever"]

    requirements_match_details = []
    match_model = model.with_structured_output(ResumeMatch, method = "json_mode")

    for requirement in requirements_extracted.requirements:
        docs = retriever.invoke(requirement.text)
        # List of the exact matches obtained from the resume based on the requirements listed down in the JD.

        content = "\n".join(doc.page_content for doc in docs)

        requirement_match_prompt = requirement_match_function(
            requirement_text = requirement.text,
            requirement_importance = requirement.importance,
            content = content
        )

        response = match_model.invoke(requirement_match_prompt)
        requirements_match_details.append(response)

        unmet_requirements = [req
                        for req in requirements_match_details
                        if req.match_status != "strong_match"]

    return {
        **inputs,
        "requirements_match_details": requirements_match_details,
        "unmet_requirements": unmet_requirements
    }

# 5
def swot_analysis(inputs: dict):
    requirements_match_details = inputs["requirements_match_details"]
    model = inputs["model"]
    
    strengths = [req
                for req in requirements_match_details
                if req.match_status == 'strong_match'
    ]

    weaknesses = [req
                for req in requirements_match_details
                if req.match_status == "partial_match"
    ]

    opportunities = [req
                for req in requirements_match_details
                if req.match_status == "missing"
                and req.importance == "preferred"
    ]

    threats = [req
                for req in requirements_match_details
                if req.match_status == "missing"
                and req.importance == "required"
    ]


    swot_analysis_model = model.with_structured_output(SWOTAnalysis, method = "json_mode")
    swot_prompt = swot_function(
        strengths = strengths,
        weaknesses = weaknesses,
        opportunities = opportunities,
        threats = threats
    )

    swot_result = swot_analysis_model.invoke(swot_prompt)

    return {
        **inputs,
        "swot_result": swot_result
    }
    

# 3
def extract_keywords(inputs: dict):
    model = inputs["model"]
    job_description = inputs["job_description"]

    keyword_extraction_model = model.with_structured_output(KeywordExtract, method = "json_mode")


    keyword_extraction_prompt = keyword_extraction_function(job_description)
    mentioned_keywords = keyword_extraction_model.invoke(keyword_extraction_prompt)

    return {
        **inputs,
        "mentioned_keywords": mentioned_keywords
    }

# 4
def match_keywords(inputs: dict):
    model = inputs["model"]
    mentioned_keywords = inputs["mentioned_keywords"]
    retriever = inputs["retriever"]
    keyword_match_model = model.with_structured_output(KeywordMatch, method = "json_mode")
    keyword_match_results = []
    for keyword in mentioned_keywords.keywords:
        docs = retriever.invoke(keyword)

        context = "\n".join(doc.page_content for doc in docs)


        keyword_match_prompt = keyword_match_function(
            context = context,
            keyword = keyword
        )
        response = keyword_match_model.invoke(keyword_match_prompt)

        keyword_match_results.append(response)


    # Listing down the various categories of keywords.
    missing_keywords = []
    present_keywords = []
    related_keywords = []

    for kwd in keyword_match_results:
        if kwd.match_status == "present":
            present_keywords.append(kwd.keyword)
        elif kwd.match_status == "related":
            related_keywords.append(kwd.keyword)
        else:
            missing_keywords.append(kwd.keyword)

    return {
        **inputs,
        "keyword_match_results": keyword_match_results,
        "missing_keywords": missing_keywords,
        "related_keywords": related_keywords,
        "present_keywords": present_keywords
    }

def calculate_ats(inputs: dict):
    requirements_match_details = inputs["requirements_match_details"]
    mentioned_keywords = inputs["mentioned_keywords"]
    present_keywords = inputs["present_keywords"]
    related_keywords = inputs["related_keywords"]

    preferred_points = 0.0
    preferred_total = 0

    required_points = 0.0
    required_total = 0

    for req in requirements_match_details:

        if req.importance == "required":
            required_total += 1

            if req.match_status == "strong_match":
                required_points += 1
            elif req.match_status == "partial_match":
                required_points += 0.3

        elif req.importance == "preferred":
            preferred_total += 1

            if req.match_status == "strong_match":
                preferred_points += 1
            elif req.match_status == "partial_match":
                preferred_points += 0.3

    required_score = (
        (required_points / required_total) * 100
        if required_total else 0
    )

    preferred_score = (
        (preferred_points / preferred_total) * 100
        if preferred_total else 0
    )

    keyword_score = (
        (
            len(present_keywords) +
            0.5 * len(related_keywords)
        ) / len(mentioned_keywords.keywords) * 100
        if mentioned_keywords.keywords else 0
    )

    ats_score = (
        0.70 * required_score +
        0.15 * preferred_score +
        0.15 * keyword_score
    )

    if ats_score >= 85:
        verdict = "Excellent Match"
    elif ats_score >= 70:
        verdict = "Good Match"
    elif ats_score >= 55:
        verdict = "Moderate Match"
    else:
        verdict = "Weak Match"

    overall_ats_score = ATSScore(
        score=round(ats_score, 2),
        required_score=round(required_score, 2),
        preferred_score=round(preferred_score, 2),
        keyword_score=round(keyword_score, 2),
        verdict=verdict,
    )

    return {
        **inputs,
        "overall_ats_score": overall_ats_score,
    }

# 6
def fetch_parts(inputs: dict):
    model = inputs["model"]
    resume_text = inputs["resume_text"]

    fetch_resume_parts_model = model.with_structured_output(ResumePartsList, method = "json_mode")
    fetch_parts_prompt = fetch_parts_function(resume_text)
    resume_parts_list = fetch_resume_parts_model.invoke(fetch_parts_prompt)

    return {
        **inputs,
        "resume_parts_list": resume_parts_list
    }

# 7
def improvement(inputs: dict):
    model = inputs["model"]
    resume_parts_list = inputs["resume_parts_list"]
    requirements_extracted = inputs["requirements_extracted"]
    unmet_requirements = inputs["unmet_requirements"]
    missing_keywords = inputs["missing_keywords"]

    content_improvements = []

    improved_bullet_model = model.with_structured_output(ResumeContentGap, method = "json_mode")
    for part in resume_parts_list.parts:
        
        improvement_prompt = improvement_function(
            requirements_extracted_requirements = requirements_extracted.requirements,
            unmet_requirements = unmet_requirements,
            missing_keywords = missing_keywords,
            part_section = part.section,
            part_original_text = part.original_text
        )
        response = improved_bullet_model.invoke(improvement_prompt)
        content_improvements.append({
            "section": part.section,
            "improvement": response
        })

    content_improvements = content_improvements[:10]

    return {
        **inputs,
        "content_improvements": content_improvements
    }

# 8
def roadmap(inputs: dict):

    model = inputs["model"]
    requirements_extracted = inputs["requirements_extracted"]
    overall_ats_score = inputs["overall_ats_score"]
    requirements_match_details = inputs["requirements_match_details"]
    missing_keywords = inputs["missing_keywords"]
    swot_result = inputs["swot_result"]
    content_improvements = inputs["content_improvements"]

    improvement_roadmap_model = model.with_structured_output(Roadmap, method = "json_mode")
    roadmap_prompt = roadmap_function(
        requirements_extracted_requirements = requirements_extracted.requirements,
        overall_ats_score = overall_ats_score,
        requirements_match_details = requirements_match_details,
        missing_keywords = missing_keywords,
        swot_result = swot_result,
        content_improvements = content_improvements
    )

    improvement_roadmap = improvement_roadmap_model.invoke(roadmap_prompt)

    return {
        **inputs,
        "improvement_roadmap": improvement_roadmap
    }

def final_report(inputs: dict):
    overall_ats_score = inputs["overall_ats_score"]
    requirements_match_details = inputs["requirements_match_details"]
    missing_keywords = inputs["missing_keywords"]
    swot_result = inputs["swot_result"]
    content_improvements = inputs["content_improvements"]
    present_keywords = inputs["present_keywords"]
    related_keywords = inputs["related_keywords"]
    improvement_roadmap = inputs["improvement_roadmap"]


    final_report = FinalReport(
        ats_result = overall_ats_score,
        swot_analysis = swot_result,
        present_keywords = present_keywords,
        missing_keywords = missing_keywords,
        related_keywords = related_keywords,

        requirement_analysis = requirements_match_details,
        content_gap_analysis = content_improvements,

        improvement_roadmap = improvement_roadmap
    )

    return {
        **inputs,
        "final_report": final_report
    }