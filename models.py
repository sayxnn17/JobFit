from pydantic import BaseModel
from pydantic import Field
from typing import Literal, Optional

class Requirement(BaseModel):
    text: str = Field(
        description = "What is the requirement this job?"
    )
    importance: Literal["required", "preferred"] = Field (
        description = "Whether this particular requirement is a must-have one or is it preferred to have?"
    )

class JDRequirements(BaseModel):
    requirements: list[Requirement] = Field(
        description = "List down the various requirements stated by the JD."
    )

class ResumeMatch(BaseModel):
    requirement: str
    importance: Literal["required", "preferred"]
    match_status: Literal["strong_match", "partial_match", "missing"]
    confidence: int = Field(
        description = "0 - 100 confidence score that the match_status is correct"
    )
    evidence: Optional[str] = Field(
        default = None,
        description = "Exact text from the resume quoted. Leave this field blank in case of missing matches."
    )
    explanation: str = Field(
        description = "Simple 1 to 2 liner explanation justifying why is this a good match for the job."
    )

class KeywordExtract(BaseModel):
    keywords: list[str] = Field(description = "Extract all impotant skills, technologies, frameworks, methodologies, qualifications from the job description")

class KeywordMatch(BaseModel):
    keyword: str
    match_status: Literal["present", "related", "missing"]
    evidence: Optional[str] = Field(description = "Exact text from the Resume where this oparticular keyword is mentioned")

class ATSScore(BaseModel):
    score: float

    required_score: float
    preferred_score: float
    keyword_score: float

    verdict: str

class SWOTAnalysis(BaseModel):
    strengths: list[str]
    weaknesses: list[str]
    opportunities: list[str]
    threats: list[str]

class ResumeContentGap(BaseModel):
    original_text: str
    improved_text: str = Field(
        description = "Improved version of the original text using stronger technical knowledge with the same facts mentioned in the original text. Do NOT invent facts."
    )
    missing_information: list[str] = Field(
        description = "Imortant information that is missing in the original text, that would make the original text stronger."
    )
    relevance_to_jd: str = Field(
        description = "Why is the improved version more relevant to the job description."
    )

class ResumeParts(BaseModel):
    section: Literal["projects", "work_experience", "achievements"]
    original_text: str 

class ResumePartsList(BaseModel):
    parts: list[ResumeParts]

class Action(BaseModel):
    action: str = Field(
        description = "Describe what action needs to be taken in order to improve the Resume and make the candidate more eligible for the job openning"
    )

    priority: Literal["high", "medium", "low"] = Field(
        description = "How urgent is this improvement?"
    )

    reason: str = Field(
        description = "Explain why this task needs to be performed and how this increases the alignment of the resume with the JD."
    )


class Roadmap(BaseModel):
    immediate_actions: list[Action] = Field(
        description = "List down those actions that can be completed within 1 week."
    )
    short_term_actions: list[Action] = Field(
        description = "List down those actions that can be completed in from 1 week to 3 weeks."
    )
    long_term_actions: list[Action] = Field(
        description = "List down those actions that need more than 3 weeks to be completed."
    )

class FinalReport(BaseModel):
    ats_result: ATSScore
    swot_analysis: SWOTAnalysis
    present_keywords: list
    missing_keywords: list
    related_keywords: list

    requirement_analysis: list[ResumeMatch]
    content_gap_analysis: list

    improvement_roadmap: Roadmap