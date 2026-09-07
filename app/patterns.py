"""Compiled regular expressions for resume information extraction."""

import re

# Email: Standard RFC-compatible pattern
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    re.IGNORECASE
)

# Phone: Comprehensive patterns covering Indian (+91, 10 digits starting 6-9)
# and International / US formats like +1 (555) 123-4567, 555-123-4567
PHONE_PATTERNS = [
    # Indian phone: +91 7600765359, +91 98765 43210, +91-9876543210, 09876543210, 9876543210
    re.compile(
        r"(?:(?:\+|00)91[\s.-]?)?[6-9]\d{4}[\s.-]?\d{5}\b"
    ),
    re.compile(
        r"(?:(?:\+|00)91[\s.-]?)?[6-9]\d{9}\b"
    ),
    # US / North American / Standard parentheses: +1 (555) 123-4567, (555) 123-4567
    re.compile(
        r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"
    ),
    # Generic international with country code: +44 20 7946 0991, +61 2 9876 5432
    re.compile(
        r"\+\d{1,3}[\s.-]?\(?\d{1,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b"
    )
]

# LinkedIn Profile URL
LINKEDIN_PATTERN = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?linkedin\.com\/(?:in|pub)\/([a-zA-Z0-9_-]+)(?:\/|\b)?",
    re.IGNORECASE
)

# GitHub Profile URL
GITHUB_PATTERN = re.compile(
    r"(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9_-]+)(?:\/|\b)?",
    re.IGNORECASE
)

# Year Pattern: 19xx or 20xx
YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")

# Date range / Duration pattern: e.g. "Jan 2021 - Present", "July 2022 – April 2025", "2019 - 2023"
DATE_RANGE_PATTERN = re.compile(
    r"(?:\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\b\d{1,2}\/\d{4}|\b(?:19|20)\d{2})\s*(?:-|–|—|to)\s*(?:\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|\b\d{1,2}\/\d{4}|\b(?:19|20)\d{2}|Present|Current|Ongoing)\b",
    re.IGNORECASE
)

# CGPA and Percentage Patterns
CGPA_PATTERN = re.compile(
    r"\b(?:CGPA|GPA|CPI)\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?(?:\s*\/\s*10)?)\b",
    re.IGNORECASE
)

PERCENTAGE_PATTERN = re.compile(
    r"(?:Percentage|Score|Marks|Aggregate)?\s*[:=-]?\s*([0-9]+(?:\.[0-9]+)?\s*%)",
    re.IGNORECASE
)

# Degrees Pattern - captures full degree / credential names
DEGREE_PATTERN = re.compile(
    r"\b("
    r"Bachelor\s+of\s+[A-Za-z\s&]+(?:\s*\([A-Za-z\s&]+\))?|"
    r"Master\s+of\s+[A-Za-z\s&]+(?:\s*\([A-Za-z\s&]+\))?|"
    r"Higher\s+Secondary(?:\s+Education)?(?:\s*\([^)]+\))?|"
    r"Senior\s+Secondary(?:\s+Education)?(?:\s*\([^)]+\))?|"
    r"Secondary\s+School(?:\s+Education)?(?:\s*\([^)]+\))?|"
    r"High\s+School(?:\s+Education|\s+Diploma)?(?:\s*\([^)]+\))?|"
    r"B\.?\s*Tech(?:\s+(?:in|of)\s+[A-Za-z &]+)?(?:\s*\([A-Za-z\s&]+\))?|"
    r"B\.?\s*E\.?(?:\s+(?:in|of)\s+[A-Za-z &]+)?(?:\s*\([A-Za-z\s&]+\))?|"
    r"M\.?\s*Tech(?:\s+(?:in|of)\s+[A-Za-z &]+)?(?:\s*\([A-Za-z\s&]+\))?|"
    r"M\.?\s*E\.?(?:\s+(?:in|of)\s+[A-Za-z &]+)?(?:\s*\([A-Za-z\s&]+\))?|"
    r"B\.?\s*Sc(?:\s+(?:in|of)\s+[A-Za-z &]+)?(?:\s*\([A-Za-z\s&]+\))?|"
    r"M\.?\s*Sc(?:\s+(?:in|of)\s+[A-Za-z &]+)?(?:\s*\([A-Za-z\s&]+\))?|"
    r"BCA(?:\s*\([A-Za-z\s&]+\))?|MCA(?:\s*\([A-Za-z\s&]+\))?|"
    r"B\.?\s*Com(?:\s+(?:in|of)\s+[A-Za-z &]+)?|"
    r"M\.?\s*Com|"
    r"BBA|MBA|"
    r"Ph\.?\s*D\.?|Doctor\s+of\s+Philosophy|"
    r"Bachelor(?:'s)?(?:\s+(?:of|in)\s+[A-Za-z &]+)?(?:\s*\([A-Za-z\s&]+\))?|"
    r"Master(?:'s)?(?:\s+(?:of|in)\s+[A-Za-z &]+)?(?:\s*\([A-Za-z\s&]+\))?|"
    r"Associate(?:'s)?(?:\s+Degree)?(?:\s+(?:in|of)\s+[A-Za-z &]+)?|"
    r"Diploma(?:\s+(?:in|of)\s+[A-Za-z &]+)?"
    r")\b",
    re.IGNORECASE
)

# Common words to filter out when searching for person's name
NAME_EXCLUDE_KEYWORDS = {
    "resume", "curriculum", "vitae", "cv", "page", "profile", "contact",
    "details", "information", "phone", "email", "address", "summary",
    "objective", "education", "experience", "skills", "projects", "certifications",
    "languages", "interests", "hobbies", "declaration", "personal", "github",
    "linkedin", "portfolio", "work", "technical", "academic", "strengths",
    "problem", "solving", "analytical", "critical", "thinking", "collaboration",
    "communication", "learning", "team", "continuous", "engineering", "developer",
    "engineer", "training", "activities", "references", "masai", "school",
    "navsari", "gujarat", "relocation", "india"
}

# Common job title patterns
JOB_TITLE_KEYWORDS = [
    "Software Engineer", "Software Developer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Full Stack Engineer", "Web Developer", "Mobile Developer",
    "Data Scientist", "Data Analyst", "Machine Learning Engineer", "AI Engineer",
    "DevOps Engineer", "Cloud Engineer", "System Administrator", "Database Administrator",
    "QA Engineer", "Quality Assurance Engineer", "Test Engineer", "Automation Engineer",
    "Product Manager", "Project Manager", "Technical Lead", "Team Lead",
    "Engineering Manager", "Solutions Architect", "Systems Analyst", "Business Analyst",
    "Research Assistant", "Teaching Assistant", "Intern", "Software Engineering Intern",
    "Developer Intern", "Graduate Trainee", "Associate Software Engineer", "Consultant"
]

