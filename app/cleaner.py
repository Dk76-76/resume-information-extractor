"""Text normalization and section segmentation module."""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple

# Section heading keywords
SECTION_HEADERS: Dict[str, List[str]] = {
    "HEADER": [
        "header", "contact", "contact info", "contact information", "contact details",
        "personal details", "personal info", "personal information"
    ],
    "SUMMARY": [
        "summary", "professional summary", "profile", "professional profile",
        "career summary", "executive summary", "objective", "career objective",
        "about me", "personal statement", "academic summary"
    ],
    "TECHNICAL_SKILLS": [
        "technical skills", "technical skill", "technical expertise",
        "technical competencies", "technologies", "programming skills",
        "skills & tools", "skills and tools", "technical proficiencies", "tech stack"
    ],
    "SKILLS": [
        "skills", "skills & abilities", "core competencies", "key skills",
        "skill set", "core competencies & skills", "areas of expertise"
    ],
    "SOFT_SKILLS": [
        "soft skills", "interpersonal skills", "core strengths", "strengths",
        "personal skills", "behavioral skills"
    ],
    "EDUCATION": [
        "education", "academic qualification", "academic qualifications",
        "academic background", "educational background", "educational qualifications",
        "academic details", "qualifications", "academics"
    ],
    "EXPERIENCE": [
        "experience", "work experience", "professional experience",
        "employment", "employment history", "work history", "career history",
        "internship", "internships", "relevant experience"
    ],
    "PROJECTS": [
        "projects", "academic projects", "key projects", "personal projects",
        "technical projects", "academic & practical projects", "academic and practical projects",
        "practical projects"
    ],
    "TRAINING": [
        "professional training", "training", "trainings", "courses",
        "coursework", "professional development", "training & certifications"
    ],
    "CERTIFICATIONS": [
        "certifications", "certificates", "licenses & certifications",
        "courses and certifications", "achievements", "awards", "honors"
    ]
}


def clean_text(raw_text: str) -> str:
    """Normalizes whitespace, unicode artifacts, and standardizes punctuation.
    
    Args:
        raw_text: Raw string extracted from document parser.
        
    Returns:
        Cleaned, normalized string.
    """
    if not raw_text:
        return ""

    # Normalize unicode characters to NFKC form
    text = unicodedata.normalize("NFKC", raw_text)

    # Standardize fancy bullets and symbols to standard space/bullet
    text = re.sub(r"[\u2022\u2023\u25E6\u2043\u2219\u25CB\u25CF\u25A0\u25AA]", " \n- ", text)
    
    # Standardize fancy quotes and dashes
    text = re.sub(r"[\u2018\u2019]", "'", text)
    text = re.sub(r"[\u201C\u201D]", '"', text)
    text = re.sub(r"[\u2013\u2014]", "-", text)
    text = text.replace("\xa0", " ")

    # Clean per line
    lines = []
    for line in text.splitlines():
        # Collapse multiple spaces within the line
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(cleaned_line)

    # Join and collapse 3+ consecutive newlines to 2
    normalized = "\n".join(lines)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def _is_section_header(line: str) -> Optional[str]:
    """Determines if a line is a recognized section heading.
    
    Args:
        line: Single text line.
        
    Returns:
        Section category name (e.g. 'EDUCATION', 'TECHNICAL_SKILLS') or None.
    """
    cleaned = line.strip().lower()
    # Strip leading icons, bullets, dashes, digits/roman numerals with dots
    cleaned = re.sub(r"^[^\w\s]+", "", cleaned)
    cleaned = re.sub(r"^[-–—*\d.]+\s*", "", cleaned)
    # Strip trailing colons, dashes, pipes, semicolons
    cleaned = re.sub(r"[:;—–\-|]+$", "", cleaned).strip()

    # Headings are typically short (1-5 words)
    words = cleaned.split()
    if not (1 <= len(words) <= 6):
        return None

    # Direct match against SECTION_HEADERS
    for section_name, keywords in SECTION_HEADERS.items():
        for keyword in keywords:
            if cleaned == keyword:
                return section_name

    # Try matching without '&' vs 'and'
    normalized_cleaned = cleaned.replace("&", "and")
    for section_name, keywords in SECTION_HEADERS.items():
        for keyword in keywords:
            if normalized_cleaned == keyword.replace("&", "and"):
                return section_name

    return None


def detect_sections(cleaned_text: str) -> Dict[str, str]:
    """Segments resume text into distinct logical sections.
    
    Args:
        cleaned_text: Normalized resume text.
        
    Returns:
        Dictionary mapping section names (e.g. 'HEADER', 'EDUCATION', 'TECHNICAL_SKILLS')
        to their respective text blocks.
    """
    lines = cleaned_text.splitlines()
    sections: Dict[str, List[str]] = {"HEADER": []}
    current_section = "HEADER"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        detected_section = _is_section_header(stripped)
        if detected_section:
            current_section = detected_section
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(stripped)

    return {k: "\n".join(v) for k, v in sections.items() if v}


# Alias for backward compatibility
segment_sections = detect_sections

