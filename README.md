# JobFit

AI resume analyzer that scores your resume against a job description and suggests targeted improvements using LangChain.

## Features
- **ATS Match Scoring**
- **SWOT Analysis**
- **Keyword Analysis**
- **Content Improvement Suggestions**
- **Targeted Improvement Roadmap**

## Installation

### Prerequisites
- Python 3.x
- OpenAI API Key

### Local Setup

1. Clone the repository
   ```bash
   git clone https://github.com/sayxnn17/JobFit.git
   cd JobFit
   ```

2. Create a virtual environment

   **On Linux/macOS:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   **On Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables

   Create a `.env` file inside the folder with the OpenAI API Key written inside:
   ```bash
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
   ```

## Run the Application

```bash
streamlit run app.py
```

## Tech Stack

1. **Streamlit**: Powers the web-based user interface, allowing users to upload their resume, enter the job description, and view their resume analysis report.
2. **LangChain**: Controls the multi-step pipeline by chaining the various parts — requirement extraction and matching, keyword extraction and matching, scoring, and improvement roadmap generation — into parallel and sequential steps.
3. **OpenAIEmbeddings**: Generates the embeddings from the resume uploaded by the user.
4. **ChatOpenAI**: Uses the chat model and trains it to produce structured output based on Pydantic schemas.
5. **Chroma**: Helps in storing and retrieving the embedding vectors of the resume as needed.
6. **Pydantic**: Defines structured schemas for requirements analysis, ATS scores, and SWOT results to enforce consistent outputs from the LLM.

## Contribution Guidelines

I welcome contributions to JobFit! Here's how you can contribute:

1. Fork the repository and clone it locally.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Write tests for any new functionality or fixes.
4. Ensure code follows PEP 8 guidelines. Use `black` for code formatting and `flake8` for linting.
5. Commit changes with descriptive messages:
   ```bash
   git commit -m "feat: add new feature"
   ```
6. Push changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a Pull Request to the main repository.
8. Review process: Once your PR is reviewed, be ready to make necessary changes and improvements based on feedback.
