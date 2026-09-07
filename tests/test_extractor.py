"""Unit and integration tests for ResumeExtractor and API endpoints."""

from pathlib import Path
import pytest
from starlette.testclient import TestClient

from app.cleaner import clean_text, detect_sections, segment_sections
from app.extractor import ResumeExtractor
from app.main import app
from app.parser import extract_document_layout, extract_text_from_file
from app.skills import extract_skills

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"
client = TestClient(app)


# ==========================================
# 1. FIELD EXTRACTOR UNIT TESTS
# ==========================================

def test_extract_email():
    """Verify email extraction across different contexts, subdomains, and cases."""
    text1 = "Contact me at John.Doe@Email.com or support@company.org."
    assert ResumeExtractor(text1).extract_email() == "john.doe@email.com"

    text2 = "Candidate email: devendar.ai+test@sub.domain.co.in."
    assert ResumeExtractor(text2).extract_email() == "devendar.ai+test@sub.domain.co.in"

    text3 = "No email provided in this text string."
    assert ResumeExtractor(text3).extract_email() is None


def test_extract_phone_formats():
    """Verify phone extraction across Indian (spaced, continuous) and international formats."""
    # Indian with +91 and space
    t1 = "DEVENDAR KUMAVAT\nPhone: +91 7600765359\nNavsari, Gujarat"
    assert ResumeExtractor(t1).extract_phone() == "+91 7600765359"

    # Indian with +91 and 5-5 split
    t2 = "John Doe\nPhone: +91 98765 43210\nBangalore, India"
    assert ResumeExtractor(t2).extract_phone() == "+91 98765 43210"

    # Indian 10-digit continuous
    t3 = "Jane Smith\nMobile: 9876543210\nDelhi"
    assert ResumeExtractor(t3).extract_phone() == "9876543210"

    # US format with parentheses
    t4 = "Sarah Jenkins\n(415) 555-0199\nSan Francisco, CA"
    assert ResumeExtractor(t4).extract_phone() == "(415) 555-0199"

    # International with plus code
    t5 = "Alex Vance\nTel: +44 20 7946 0991\nLondon, UK"
    assert ResumeExtractor(t5).extract_phone() == "+44 20 7946 0991"

    # Text without phone
    t6 = "No phone number is available here."
    assert ResumeExtractor(t6).extract_phone() is None


def test_extract_name_heuristics():
    """Verify candidate name detection heuristics."""
    # Standard Title Case
    t1 = "Devendar Kumavat\nEmail: dev@example.com\nPhone: 9876543210"
    assert ResumeExtractor(t1).extract_name() == "Devendar Kumavat"

    # ALL CAPS Name
    t2 = "ALAN MATHISON TURING\nalan@turing.org | 9876543210"
    assert ResumeExtractor(t2).extract_name() == "ALAN MATHISON TURING"

    # Header with labels to ignore
    t3 = "CURRICULUM VITAE\n\nEmily Watson\nemily@example.com\n9876543210"
    assert ResumeExtractor(t3).extract_name() == "Emily Watson"


def test_name_not_from_first_raw_line():
    """Ensure name is not picked simply from the first line when it's a soft skill or heading."""
    jumbled_text = (
        "Problem Solving\n"
        "Analytical Thinking\n"
        "Critical Thinking\n"
        "EDUCATION\n"
        "BCA\n"
        "DEVENDAR KUMAVAT\n"
        "kumavatbdevendar@gmail.com\n"
        "+91 7600765359\n"
    )
    ext = ResumeExtractor(jumbled_text)
    extracted_name = ext.extract_name()
    assert extracted_name != "Problem Solving"
    assert extracted_name != "Analytical Thinking"
    assert extracted_name == "DEVENDAR KUMAVAT"


def test_extract_skills_boundary_safety():
    """Verify skills extraction including symbol-based skills and boundary safety."""
    text = (
        "Experienced in Python, C++, C#, .NET, Node.js, and SQL.\n"
        "Worked on Docker, Kubernetes, and AWS cloud infrastructure."
    )
    skills = extract_skills(text)
    
    expected_subset = {"Python", "C++", "C#", ".NET", "Node.js", "SQL", "Docker", "Kubernetes", "AWS"}
    for skill in expected_subset:
        assert skill in skills, f"Expected '{skill}' to be detected"

    # Ensure "Java" is not falsely triggered by "JavaScript" alone
    text_js = "Frontend developer skilled in JavaScript, HTML5, and CSS3."
    skills_js = extract_skills(text_js)
    assert "JavaScript" in skills_js
    assert "Java" not in skills_js


def test_extract_skills_categorized_and_taxonomy():
    """Verify category-aware skill parsing and multi-word modern skills."""
    skills_section = (
        "TECHNICAL SKILLS:\n"
        "Programming: Python, SQL, HTML, CSS, JavaScript\n"
        "AI/ML: Machine Learning, Deep Learning, NLP, RAG, LangChain, FAISS, CNN, Transfer Learning\n"
        "Libraries: NumPy, Pandas, Matplotlib, Seaborn, Scikit-learn, TensorFlow\n"
        "Backend & Deployment: FastAPI, Streamlit, REST APIs, Docker, Railway, Render\n"
        "Tools: Git, GitHub, Jupyter Notebook, Google Colab"
    )
    skills = extract_skills(skills_section, skills_section)
    required = [
        "Python", "SQL", "HTML", "CSS", "JavaScript",
        "Machine Learning", "Deep Learning", "NLP", "RAG", "LangChain", "FAISS", "CNN", "Transfer Learning",
        "NumPy", "Pandas", "Matplotlib", "Seaborn", "Scikit-learn", "TensorFlow",
        "FastAPI", "Streamlit", "REST APIs", "Docker", "Railway", "Render",
        "Git", "GitHub", "Jupyter Notebook", "Google Colab"
    ]
    for req in required:
        assert req in skills or req.title() in skills or req.upper() in skills, f"Missing {req}"


def test_soft_skills_excluded_from_technical_skills():
    """Verify soft skills are never included in technical skills."""
    text = (
        "TECHNICAL SKILLS:\n"
        "Programming: Python, SQL\n\n"
        "SOFT SKILLS:\n"
        "Problem Solving, Analytical Thinking, Critical Thinking, Team Collaboration, Communication"
    )
    ext = ResumeExtractor(text)
    skills = ext.extract_skills()
    assert "Python" in skills
    assert "SQL" in skills
    assert "Problem Solving" not in skills
    assert "Critical Thinking" not in skills
    assert "Analytical Thinking" not in skills
    assert "Team Collaboration" not in skills


def test_projects_not_extracted_as_experience():
    """Ensure academic and practical projects are never treated as work experience."""
    text = (
        "ACADEMIC & PRACTICAL PROJECTS:\n"
        "1. AI-Powered Travel Agent\n"
        "Built an AI travel planner integrating 6 live APIs using LangChain, Groq LLM, and FastAPI.\n"
        "2. AI-Powered RAG Chatbot\n"
        "Developed a PDF-based GenAI chatbot using LangChain, FAISS, Groq LLM, FastAPI."
    )
    ext = ResumeExtractor(text)
    assert ext.extract_experience() == []


def test_extract_education_multi_format():
    """Verify education extraction with separate degree, institution, university, CGPA, and percentage lines."""
    edu_text = (
        "EDUCATION\n"
        "S. S. Agrawal College, Navsari | July 2022 – April 2025 | CGPA: 7.84\n"
        "Bachelor of Computer Applications (BCA)\n"
        "Veer Narmad South Gujarat University, Surat\n"
        "Higher Secondary Education (12th – Commerce Stream) | 2021 | Percentage: 81.5%\n"
        "Seth P.H. Vidyalaya, Navsari\n"
    )
    ext = ResumeExtractor(edu_text)
    edu_items = ext.extract_education()

    assert len(edu_items) >= 2
    bca = next(e for e in edu_items if "BCA" in e.degree or "Bachelor of Computer Applications" in e.degree)
    assert "S. S. Agrawal College" in bca.institution
    assert "Veer Narmad South Gujarat University" in bca.university
    assert bca.cgpa == "7.84"
    assert "2025" in bca.year

    hsc = next(e for e in edu_items if "Higher Secondary" in e.degree)
    assert "Seth P.H. Vidyalaya" in hsc.institution
    assert hsc.percentage == "81.5%"
    assert hsc.year == "2021"


def test_extract_linkedin_and_github():
    """Verify social profile extraction, URL normalization, and trailing slash preservation."""
    text = (
        "Connect with me:\n"
        "LinkedIn: https://www.linkedin.com/in/devendar-kumavat-ai/\n"
        "GitHub: https://github.com/Dk76-76"
    )
    ext = ResumeExtractor(text)
    assert ext.extract_linkedin() == "https://www.linkedin.com/in/devendar-kumavat-ai/"
    assert ext.extract_github() == "https://github.com/Dk76-76"


# ==========================================
# 2. END-TO-END SAMPLE & REGRESSION TESTS
# ==========================================

def test_extract_devendar_pdf_regression():
    """Regression test specifically for Devendar_Kumavat_AI_ML_Engineer_Resume.pdf."""
    pdf_path = SAMPLES_DIR / "Devendar_Kumavat_AI_ML_Engineer_Resume.pdf"
    assert pdf_path.exists(), "Test resume must exist in samples directory"

    file_bytes = pdf_path.read_bytes()
    raw_text, spans = extract_document_layout(file_bytes, "Devendar_Kumavat_AI_ML_Engineer_Resume.pdf")
    ext = ResumeExtractor(raw_text, blocks_metadata=spans)
    data = ext.extract_all()

    # Exact requirements
    assert data.name == "DEVENDAR KUMAVAT"
    assert data.email == "kumavatbdevendar@gmail.com"
    assert data.phone == "+91 7600765359"
    assert data.linkedin == "https://www.linkedin.com/in/devendar-kumavat-ai/"
    assert data.github == "https://github.com/Dk76-76"
    assert data.experience == []

    # Education records
    assert len(data.education) >= 2
    degrees = [e.degree for e in data.education]
    assert any("Bachelor of Computer Applications (BCA)" in d for d in degrees)
    assert any("Higher Secondary Education" in d for d in degrees)

    # Technical skills
    required_skills = [
        "Python", "SQL", "HTML", "CSS", "JavaScript",
        "Machine Learning", "Deep Learning", "NLP", "RAG", "LangChain", "FAISS", "CNN", "Transfer Learning",
        "NumPy", "Pandas", "Matplotlib", "Seaborn", "TensorFlow",
        "FastAPI", "Streamlit", "REST APIs", "Docker", "Railway", "Render",
        "Git", "GitHub", "Jupyter Notebook", "Google Colab"
    ]
    skills_lower = {s.lower() for s in data.skills}
    for skill in required_skills:
        assert skill.lower() in skills_lower, f"Missing skill: {skill}"

    # Soft skills must not be in technical skills
    assert "problem solving" not in skills_lower
    assert "critical thinking" not in skills_lower


def test_extract_sample_1_pdf():
    """Test full extraction pipeline on sample_1.pdf."""
    pdf_path = SAMPLES_DIR / "resume_1.pdf"
    raw_text, spans = extract_document_layout(pdf_path.read_bytes(), "resume_1.pdf")
    data = ResumeExtractor(raw_text, blocks_metadata=spans).extract_all()

    assert data.name == "Aarav Sharma"
    assert data.email == "aarav.sharma@example.com"
    assert data.phone == "+91 98765 43210"
    assert data.linkedin == "https://linkedin.com/in/aaravsharma"
    assert data.github == "https://github.com/aaravsharma"
    assert "Python" in data.skills
    assert "FastAPI" in data.skills
    assert "Docker" in data.skills
    assert len(data.education) >= 1
    assert "B.Tech" in data.education[0].degree
    assert len(data.experience) >= 1
    assert "Intern" in data.experience[0].title


def test_extract_sample_2_docx():
    """Test full extraction pipeline on sample_2.docx."""
    docx_path = SAMPLES_DIR / "resume_2.docx"
    raw_text, spans = extract_document_layout(docx_path.read_bytes(), "resume_2.docx")
    data = ResumeExtractor(raw_text, blocks_metadata=spans).extract_all()

    assert data.name == "Sarah Jenkins"
    assert data.email == "sarah.jenkins@techmail.org"
    assert data.phone == "(415) 555-0199"
    assert data.linkedin == "https://www.linkedin.com/in/sarahjenkins-dev"
    assert data.github == "https://github.com/sarahjenkins"
    assert "TypeScript" in data.skills
    assert "React" in data.skills
    assert len(data.education) >= 2
    assert len(data.experience) >= 2


def test_extract_sample_3_pdf_minimal():
    """Test graceful handling of missing fields on sample_3.pdf."""
    pdf_path = SAMPLES_DIR / "resume_3.pdf"
    raw_text, spans = extract_document_layout(pdf_path.read_bytes(), "resume_3.pdf")
    data = ResumeExtractor(raw_text, blocks_metadata=spans).extract_all()

    assert data.name == "Vikram Patel"
    assert data.email == "vikram.patel99@gmail.com"
    assert data.phone == "9823456789"
    # Mandatory missing check
    assert data.linkedin is None
    assert data.github is None
    assert data.experience == []
    assert len(data.education) >= 1
    assert "Machine Learning" in data.skills


# ==========================================
# 3. FASTAPI REST API TESTS
# ==========================================

def test_api_health_endpoint():
    """Verify /api/health endpoint returns 200 OK and expected payload."""
    response = client.get("/api/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert json_data["llm_free"] is True


def test_api_extract_success():
    """Verify POST /api/extract with a valid sample PDF."""
    pdf_path = SAMPLES_DIR / "resume_1.pdf"
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/extract",
            files={"file": ("resume_1.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["name"] == "Aarav Sharma"
    assert res["data"]["email"] == "aarav.sharma@example.com"


def test_api_extract_devendar_resume():
    """Verify POST /api/extract with Devendar_Kumavat_AI_ML_Engineer_Resume.pdf."""
    pdf_path = SAMPLES_DIR / "Devendar_Kumavat_AI_ML_Engineer_Resume.pdf"
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/extract",
            files={"file": ("Devendar_Kumavat_AI_ML_Engineer_Resume.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    res = response.json()
    assert res["success"] is True
    assert res["data"]["name"] == "DEVENDAR KUMAVAT"
    assert res["data"]["email"] == "kumavatbdevendar@gmail.com"
    assert res["data"]["phone"] == "+91 7600765359"
    assert res["data"]["linkedin"] == "https://www.linkedin.com/in/devendar-kumavat-ai/"
    assert res["data"]["github"] == "https://github.com/Dk76-76"
    assert res["data"]["experience"] == []
    assert len(res["data"]["education"]) >= 2
    assert len(res["data"]["skills"]) >= 25


def test_api_extract_unsupported_file():
    """Verify POST /api/extract with an unsupported file returns 400 Bad Request."""
    response = client.post(
        "/api/extract",
        files={"file": ("test.txt", b"plain text content", "text/plain")}
    )
    assert response.status_code == 400
    res = response.json()
    assert res["success"] is False
    assert "Unsupported format" in res["message"]

