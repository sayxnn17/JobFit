import streamlit as st
from analyzer import analyze_resume
import os
import uuid

st.set_page_config(
    page_title="JobFit",
    page_icon="./utils/favicon_transparent.png"
)

if "report" not in st.session_state:
    st.session_state.report = None

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False


# Title
st.title("JobFit")


home_page_placeholder = st.empty()

with home_page_placeholder.container():
    st.subheader("Optimize your resume📝 Maximize your opportunities📈")

    text = """Analyze your resume against any job description with AI. Get an ATS score, identify missing skills, improve resume content, and receive personalized recommendations to maximize your interview chances."""
    st.write(text)
    resume = st.file_uploader(
        label = "Upload you resume here(.pdf):",
        type = "pdf",
        accept_multiple_files = False
    )
    job_description = st.text_input(
        label = "Enter the job description:"
    )

    analyze = st.button(
        "Analyze Resume",
        type="primary"
    )



if analyze:

    # Validate inputs
    if resume is None and not job_description.strip():
        st.error("Resume and Job Description both are missing.")
        st.stop()

    if resume is None:
        st.error("Resume is missing!")
        st.stop()


    if not job_description.strip():
        st.error("Job Description is missing!")
        st.stop()

    # Save uploaded resume
    UPLOAD_DIR = "./uploads"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)


    uid = uuid.uuid4()
    resume_name = f"{uid}.pdf"

    file_path = f"./uploads/{resume_name}"
    with open(file_path, "wb") as f:
        f.write(resume.getbuffer())

    # Create placeholders
    loading_placeholder = st.empty()
    result_placeholder = st.empty()


    with loading_placeholder.container():
        # Center GIF
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("./utils/bean_waiting.gif")
            with st.spinner("Analyzing your resume..."):
                report = analyze_resume(file_path, job_description)
        st.session_state.report = report


    home_page_placeholder.empty()
    st.session_state.analysis_done = True
    loading_placeholder.empty()

    # Display report
    with result_placeholder.container():
        st.title("Your Report is ready!!")

        # ATS Score
        ats_score = report.ats_result.score
        ats_verdict = report.ats_result.verdict
        st.header(f"ATS Score: {ats_score}/100")
        st.subheader(f"Verdict: {ats_verdict}")
        st.divider()

        # SWOT
        st.header("SWOT Board")
        st.write("Strengths:")
        for strength in report.swot_analysis.strengths:
            st.write(f"✅{strength}")

        st.write("Weaknesses:")
        for weak in report.swot_analysis.weaknesses:
            st.write(f"❌{weak}")

        st.write("Opportunities:")
        for oppo in report.swot_analysis.opportunities:
            st.write(f"📈{oppo}")

        st.write("Threats:")
        for thr in report.swot_analysis.threats:
            st.write(f"☢️{thr}")


        st.divider()

        # Requirement Match
        st.header("Requirement Match")
        for req in report.requirement_analysis:
            st.write(f"Requirement: {req.requirement}")
            st.write(f"Importance: {req.importance}")
            st.write(f"Match Status: {req.match_status}")
            with st.expander("Details:"):
                if req.match_status != "missing":
                    st.write(f"Evidence from Resume: {req.evidence}")
                
                st.write(f"Explanation: {req.explanation}")

        st.divider()

        

        # Keyword Match
        st.header("Keyword Analysis")
        st.subheader("Related Keywords:")
        if report.related_keywords:
            st.write("Following keywords from the job description do not find direct mention in the resume, but other related keywords are present in the resume.")
            for kwd in report.related_keywords:
                st.write(f"★ {kwd}")

        st.write("\n\n")
        
        st.subheader("Missing Keywords:")
        if report.missing_keywords:
            st.write("Following keywords from the job description neither find direct or indirect mention in the resume.")
            for kwd in report.missing_keywords:
                st.write(f"★ {kwd}")

        
        st.divider()

        # Resume Improvements
        st.header("Content Gap Improvements")
        st.write("Personalized suggestions to strengthen your resume content and improve relevance.")
        if report.content_gap_analysis:
            for item in report.content_gap_analysis:
                section = item["section"]
                imp = item["improvement"]

                st.write(f"SECTION: {section}")
                st.write(f"ORIGINAL TEXT: {imp.original_text}")
                st.write(f"IMPROVED TEXT: {imp.improved_text}")
                if imp.missing_information:
                    st.write(f"MISSING INFORMATION: {imp.missing_information}")
                if imp.relevance_to_jd:
                    st.write(f"RELEVANCE: {imp.relevance_to_jd}\n\n")

        st.divider()

        # Roadmap
        if report.improvement_roadmap:
            st.header("Improvement Roadmap")
            st.write("This is a step-by-step roadmap that would help you maximize your ATS Scores and interview readiness.")
            if report.improvement_roadmap.immediate_actions:
                st.write("Immediate Actions: Can be completed in 1 week.")
                for action in report.improvement_roadmap.immediate_actions:
                    st.write(f"Action: {action.action}")
                    st.write(f"Priority: {action.priority}")
                    st.write(f"Reason: {action.reason}")
                    st.write("\n\n")

            if report.improvement_roadmap.short_term_actions:
                st.write("Short-Term Actions: Can be completed in 1-3 weeks.")
                for action in report.improvement_roadmap.short_term_actions:
                    st.write(f"Action: {action.action}")
                    st.write(f"Priority: {action.priority}")
                    st.write(f"Reason: {action.reason}")
                    st.write("\n\n")

            if report.improvement_roadmap.long_term_actions:
                st.write("Long-Term Actions: Need a month or more to complete.")
                for action in report.improvement_roadmap.long_term_actions:
                    st.write(f"Action: {action.action}")
                    st.write(f"Priority: {action.priority}")
                    st.write(f"Reason: {action.reason}")
                    st.write("\n\n")
            
        else:
            st.write("You are good to go!")


    st.session_state.report = None
    st.session_state.analysis_done = False
    try:
        os.remove(file_path)
    except OSError:
        pass