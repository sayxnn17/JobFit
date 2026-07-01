from langchain_classic.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
from tasks import extract_requirements, match_requirements, swot_analysis, extract_keywords, match_keywords, fetch_parts, calculate_ats, improvement, roadmap, final_report
from langchain_core.runnables import RunnableSequence, RunnableParallel, RunnableLambda
import os

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]

embedding_model = OpenAIEmbeddings(
    model = "text-embedding-3-small",
    api_key = api_key,
    base_url = "https://api.aicredits.in/v1"
)


model = ChatOpenAI(
    model = "gpt-4o-mini",
    api_key = api_key,
    base_url = "https://api.aicredits.in/v1"
)


def analyze_resume(resume_path, job_description):
    # Extract the text from the Resume
    docs = PyPDFLoader(resume_path).load()
    resume_text = "\n".join(doc.page_content for doc in docs)

    # Generate chunks from thet text.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50
    )
    chunks = splitter.create_documents([resume_text])

    # Generate the embeddings and store the embeddings in a vector store.
    resume_embeddings = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model
    )

    retriever = resume_embeddings.as_retriever(
        search_type = "similarity",
        search_kwargs = {"k": 3}
    )

    inputs = {
        "model": model,
        "job_description": job_description,
        "resume_text": resume_text,
        "retriever": retriever
    }

    # Chain 1: Requirement Chain
    requirement_chain = RunnableSequence(
        RunnableLambda(extract_requirements),
        RunnableLambda(match_requirements),
        RunnableLambda(swot_analysis)
    )

    # Chain 2: Keyword Chain
    keyword_chain = RunnableSequence(
        RunnableLambda(extract_keywords),
        RunnableLambda(match_keywords)
    )


    # Parallel Chain
    parallel_chain = RunnableParallel(
        requirements = requirement_chain,
        keywords = keyword_chain,
        parts = RunnableLambda(fetch_parts)
    )

    parallel_output = parallel_chain.invoke(inputs)

    first_merged_output = {
        **parallel_output["requirements"],
        **parallel_output["keywords"],
        **parallel_output["parts"]
    }




    second_parallel = RunnableParallel(
        ats = RunnableLambda(calculate_ats),
        improvement = RunnableLambda(improvement)
    )
    second_output = second_parallel.invoke(first_merged_output)

    second_merged_output = {
        **second_output["ats"],
        **second_output["improvement"]
    }


    last_sequence = RunnableSequence(
        RunnableLambda(roadmap),
        RunnableLambda(final_report)
    )
    last_output = last_sequence.invoke(second_merged_output)

    return last_output["final_report"]


#  ____________
# < HelloWorld >
#  ------------
#         \   ^__^
#          \  (oo)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||