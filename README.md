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

```text
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
