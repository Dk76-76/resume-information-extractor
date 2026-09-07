# Resume Information Extraction System

A fast, lightweight, and **100% local rule-based** Resume Information Extraction System built with Python, FastAPI, and vanilla HTML/CSS/JS. It accepts **PDF** and **DOCX** resumes and extracts structured candidate data into clean JSON format.

> **CRITICAL ARCHITECTURAL GUARANTEE:**
> This system **DOES NOT use any external LLM, Generative AI service, or Cloud API** (no OpenAI, Gemini, Claude, etc.). All extraction logic executes completely on-device using deterministic text parsing, regular expressions, section segmentation heuristics, and a curated skills catalog. Your resume data remains strictly local and private.

---

## 🌟 Key Features

- **Multi-Format Support:** Accepts text-based `.pdf` and Word `.docx` documents.
- **Mandatory Fields Extracted:**
  - **Full Name:** Discovered via top-header candidate heuristics, title casing, and noise word exclusion.
  - **Email Address:** RFC-compliant regex with case normalization and punctuation cleaning.
  - **Phone Number:** Domestic (Indian `+91`, 10-digit mobile) and international formats (e.g. US `(415) 555-0199`, UK `+44`).
  - **Skills:** Boundary-safe taxonomy matching across 350+ technical and professional skills. Handles symbols like `C++`, `C#`, `.NET`, and `Node.js`.
- **Bonus Fields Extracted:**
  - **Education:** Structured degrees (`B.Tech`, `M.S.`, `B.Sc`, `Ph.D`), nearby institutions, and graduation years.
  - **Work Experience:** Job titles (`Software Engineer`, `Intern`, `Developer`), company names, and date ranges (`Jan 2024 - Jun 2024`, `Present`).
  - **LinkedIn Profile:** Extracted and canonicalized (`https://linkedin.com/in/...`).
  - **GitHub Profile:** Extracted and canonicalized (`https://github.com/...`).
- **Standardized JSON Schema:** Consistent representation of missing values (`null` for absent scalar fields, `[]` for empty lists).
- **Graceful Error Handling:** Helpful error messages for unsupported file formats, empty files, or corrupted documents.
- **Interactive Web Interface:** Modern, responsive UI with drag-and-drop file upload, visual preview cards, skill badges, live JSON viewer, and 1-click sample testing.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI** + **Uvicorn** | High-performance ASGI REST API with automatic OpenAPI documentation. |
| **PDF Extraction** | **pypdf** | Pure-Python PDF text extraction; zero external C++ compiler dependencies. |
| **DOCX Extraction** | **python-docx** | Document object model traversal for paragraphs and tables. |
| **Extraction Engine** | **Python Standard Library** (`re`, `unicodedata`) | Deterministic regex, section segmenter, and heuristic rule engines. |
| **Schema Validation** | **Pydantic v2** | Strict structured schema and JSON serialization. |
| **Frontend UI** | **HTML5, Modern CSS, ES6 JavaScript** | Zero node/npm build complexity. Direct drag-and-drop, card view, and JSON export. |
| **Test Suite** | **pytest** | Comprehensive unit and integration test coverage. |

---

## 📐 System Architecture

```
                      ┌─────────────────────────────────────────┐
                      │             Client / Browser            │
                      │  (HTML5 Drag & Drop UI / REST API Call) │
                      └────────────────────┬────────────────────┘
                                           │ Upload PDF / DOCX
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │          FastAPI Server (main.py)       │
                      │      - Validates file type & size       │
                      │      - Handles HTTP requests / errors   │
                      └────────────────────┬────────────────────┘
                                           │ File byte stream
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       Document Parser (parser.py)       │
                      │  pypdf (PDF) / python-docx (DOCX)       │
                      └────────────────────┬────────────────────┘
                                           │ Raw text
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │       Text Cleaner & Segmenter          │
                      │             (cleaner.py)                │
                      │  - Unicode & whitespace normalization   │
                      │  - Section splitting (Skills, Edu, Exp) │
                      └────────────────────┬────────────────────┘
                                           │ Normalized sections
                                           ▼
                 ┌──────────────────────────────────────────────────┐
                 │     Rule-Based Extraction Engine (extractor.py)  │
                 ├──────────────────────────────────────────────────┤
                 │ • Name: Top-header heuristic & title case filter │
                 │ • Email: RFC-compliant regex pattern             │
                 │ • Phone: Indian (+91) & International patterns   │
                 │ • Skills: Boundary-safe dictionary catalog       │
                 │ • Links: LinkedIn & GitHub URL regex             │
                 │ • Education: Degree keywords & University lookup │
                 │ • Experience: Job titles, companies, date ranges │
                 └─────────────────────────┬────────────────────────┘
                                           │
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │         Pydantic Schema (schemas.py)    │
                      │    Validates & standardizes JSON        │
                      └────────────────────┬────────────────────┘
                                           │ Structured JSON
                                           ▼
                      ┌─────────────────────────────────────────┐
                      │   Response: UI Display & JSON Export    │
                      └─────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
resume-information-extractor/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI server, endpoints, CORS, static file serving
│   ├── schemas.py           # Pydantic models for structured output & validation
│   ├── parser.py            # PDF & DOCX text extraction with robust error handling
│   ├── cleaner.py           # Text normalization and section segmentation
│   ├── patterns.py          # Pre-compiled regex patterns (Email, Phone, URLs, Degrees)
│   ├── skills.py            # Curated categorized skills dictionary & token matcher
│   └── extractor.py         # Main extraction pipeline orchestrating all field extractors
│
├── frontend/
│   ├── index.html           # Modern, responsive UI with upload dropzone & result cards
│   ├── styles.css           # Premium styling, dark theme accents, skill badges, JSON display
│   └── app.js               # Upload handling, interactive tab switching, copy & download JSON
│
├── samples/
│   ├── resume_1.pdf         # Sample 1: Tech fresher (B.Tech, skills, GitHub/LinkedIn, Indian phone)
│   ├── resume_2.docx        # Sample 2: Senior software engineer (DOCX format, work experience)
│   └── resume_3.pdf         # Sample 3: Minimal resume with missing optional fields (testing nulls)
│
├── outputs/
│   ├── resume_1_output.json # Reference extracted JSON for resume_1
│   ├── resume_2_output.json # Reference extracted JSON for resume_2
│   └── resume_3_output.json # Reference extracted JSON for resume_3
│
├── tests/
│   ├── __init__.py
│   ├── test_parser.py       # Tests for PDF/DOCX parsing, empty files, corrupt files
│   └── test_extractor.py    # Unit tests for individual field extraction and edge cases
│
├── create_samples.py        # Script to programmatically generate test PDF & DOCX files
├── requirements.txt         # Pinned lightweight dependencies
├── README.md                # Project documentation
└── .gitignore               # Python and runtime exclusions
```

---

## 🧠 Extraction Strategy

### 1. Full Name
- **Heuristic**: Candidate names almost universally appear at the top of a resume header (first 3–7 lines).
- **Filtering**:
  - Excludes lines containing contact markers (`@`, `http`, `github`, `linkedin`).
  - Excludes lines containing phone-like digit sequences (`\d{3,}`).
  - Excludes generic header labels (`Resume`, `Curriculum Vitae`, `CV`, `Page 1`, `Contact`).
- **Scoring**: Identifies lines with 2 to 4 capitalized or ALL CAPS words with length between 3 and 35 characters, standardizing output into proper Title Case.

### 2. Email Address
- Uses RFC-compliant pattern `[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+`.
- Normalizes to lowercase and trims trailing periods, commas, or semicolons.

### 3. Phone Number
- Multi-regex matcher supporting:
  - Indian mobile formats: `+91 98765 43210`, `+91-9876543210`, `9876543210`.
  - North American / US formats: `(415) 555-0199`, `+1-555-123-4567`.
  - International formats with country codes: `+44 20 7946 0991`.
- Filters out non-phone digit sequences (such as graduation years or zip codes).

### 4. Skills
- Curated catalog covering 350+ skills categorized into:
  - *Programming Languages* (Python, Java, C++, C#, Go, Rust, TypeScript, etc.)
  - *Frameworks & Libraries* (FastAPI, React, Django, Node.js, Express, etc.)
  - *Databases* (PostgreSQL, MongoDB, Redis, MySQL, etc.)
  - *Cloud & DevOps* (AWS, Docker, Kubernetes, CI/CD, Linux, etc.)
  - *AI & Data Science* (Machine Learning, Pandas, NumPy, Scikit-Learn, PyTorch, etc.)
- **Boundary-Safe Matching**: Standard word boundaries `\b` fail on symbols like `C++`, `C#`, and `.NET`. Custom lookahead/lookbehind patterns are employed to match special symbols accurately without false positives.

### 5. LinkedIn & GitHub Profiles
- LinkedIn: `(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub)\/([a-zA-Z0-9_-]+)`
- GitHub: `(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)`
- Canonicalized to ensure complete `https://...` URLs.

### 6. Education (Bonus)
- Prioritizes the segmented `EDUCATION` block.
- Detects degrees via pattern matching (`B.Tech`, `B.E.`, `M.S.`, `B.Sc`, `Bachelor of ...`, `Master of ...`, `Ph.D`, etc.).
- Identifies institutions using institutional keywords (`University`, `College`, `Institute`, `School`, `Academy`, `Campus`, `IIT`, `NIT`, `BITS`).
- Identifies graduation year via 4-digit year patterns (`19xx` or `20xx`).

### 7. Work Experience (Bonus)
- Prioritizes the segmented `EXPERIENCE` / `WORK HISTORY` block.
- Identifies common professional titles (`Software Engineer`, `Full Stack Developer`, `Intern`, `Data Analyst`, etc.).
- Detects tenure via multi-format date ranges (`Jan 2024 - Jun 2024`, `2020 - 2022`, `Present`).
- Pairs title, duration, and organization into clean structured entries.

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.10+ (Tested and verified on Python 3.13)
- pip package manager

### 1. Clone or Open the Project
```bash
cd "c:/Users/Devendar Kumavat/Desktop/gopal ]"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🏃 Running the Application

### Start the FastAPI Server
Run the application using Uvicorn:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Access the Web Interface
Open your browser and navigate to:
```
http://127.0.0.1:8000/
```

- **Interactive UI**: Upload any `.pdf` or `.docx` resume, view extracted cards, and copy/download structured JSON.
- **Quick Sample Testing**: Click on the **Sample 1**, **Sample 2**, or **Sample 3** buttons in the left panel to test extraction instantly with one click.
- **Interactive API Documentation (Swagger)**: Available at `http://127.0.0.1:8000/docs`.

---

## 🧪 Testing Instructions

The repository includes a comprehensive test suite covering parser edge cases, regex accuracy, and end-to-end extraction against all 3 sample files.

Run the test suite:
```bash
pytest -v
```

### Test Coverage Highlights:
- ✅ `test_parse_valid_pdf`: Verifies PDF parsing with `pypdf`.
- ✅ `test_parse_valid_docx`: Verifies DOCX paragraph and table parsing with `python-docx`.
- ✅ `test_parse_empty_file`: Asserts `EmptyDocumentError` on 0-byte uploads.
- ✅ `test_parse_unsupported_extension`: Asserts `UnsupportedFileTypeError` on non-PDF/DOCX files.
- ✅ `test_parse_corrupted_pdf` & `test_parse_corrupted_docx`: Asserts graceful handling of corrupt files.
- ✅ `test_extract_email`: Tests email parsing and case normalization.
- ✅ `test_extract_phone_formats`: Tests domestic, Indian `+91`, US parentheses, and international numbers.
- ✅ `test_extract_name_heuristics`: Tests Title Case, uppercase, and header filtering.
- ✅ `test_extract_skills_boundary_safety`: Tests boundary safety for `C++`, `C#`, `.NET`, `Node.js`, and ensures `Java` is not triggered by `JavaScript`.
- ✅ `test_extract_sample_1_pdf`: Full verification on tech fresher resume.
- ✅ `test_extract_sample_2_docx`: Full verification on senior engineer DOCX resume.
- ✅ `test_extract_sample_3_pdf_minimal`: Verifies missing optional fields resolve to `null` and `[]`.
- ✅ `test_api_health_endpoint` & `test_api_extract_success`: Tests FastAPI REST endpoints.

---

## 📋 Example Inputs and Outputs

### Sample 1: Fresh Graduate (`samples/resume_1.pdf`)
**Extracted JSON (`outputs/resume_1_output.json`)**:
```json
{
  "name": "Aarav Sharma",
  "email": "aarav.sharma@example.com",
  "phone": "+91 98765 43210",
  "skills": [
    "C++",
    "CSS",
    "Docker",
    "FastAPI",
    "Git",
    "GitHub",
    "HTML",
    "Java",
    "Linux",
    "Microservices",
    "PostgreSQL",
    "Python",
    "React",
    "SQL"
  ],
  "education": [
    {
      "degree": "B.Tech in Computer Science",
      "institution": "ABC Institute of Technology",
      "year": "2024"
    }
  ],
  "experience": [
    {
      "title": "Software Engineering Intern",
      "company": "Nexus Tech Solutions",
      "duration": "Jan 2024 - Jun 2024"
    }
  ],
  "linkedin": "https://linkedin.com/in/aaravsharma",
  "github": "https://github.com/aaravsharma"
}
```

### Sample 3: Minimal Fields (`samples/resume_3.pdf`)
Demonstrating graceful handling of missing optional values (`null` and `[]`):
```json
{
  "name": "Vikram Patel",
  "email": "vikram.patel99@gmail.com",
  "phone": "9823456789",
  "skills": [
    "Data Analysis",
    "Data Science",
    "Machine Learning",
    "NumPy",
    "Pandas",
    "Python",
    "SQL",
    "Tableau"
  ],
  "education": [
    {
      "degree": "B.Sc in Statistics",
      "institution": "City College",
      "year": "2023"
    }
  ],
  "experience": [],
  "linkedin": null,
  "github": null
}
```

---

## 📌 Assumptions & Potential Limitations

1. **Digital Text Requirement**:
   - The parser assumes the resume contains digital text layers. Scanned resumes that are pure images without OCR text cannot be read; the application catches this and returns a clear message: `"No readable text found in document"`.
2. **Standard Reading Order**:
   - Complex multi-column graphic designs in PDFs are parsed sequentially. The cleaner handles newline normalization, but atypical layouts where candidate names are in bottom footers or vertical sidebars may require manual review.
3. **Skills Dictionary Scope**:
   - Skills extraction uses a pre-compiled taxonomy of 350+ entries. Highly niche or organization-internal proprietary tool names not present in the dictionary will not be matched. New skills can be effortlessly added to `app/skills.py`.
4. **No External LLM Guarantee**:
   - Extraction is deterministic, fast, runs offline, and does not incur any API costs or risk data exposure.
