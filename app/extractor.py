"""Main resume information extractor module."""

import re
from typing import Any, Dict, List, Optional
from app.cleaner import clean_text, detect_sections
from app.patterns import (
    CGPA_PATTERN,
    DATE_RANGE_PATTERN,
    DEGREE_PATTERN,
    EMAIL_PATTERN,
    GITHUB_PATTERN,
    JOB_TITLE_KEYWORDS,
    LINKEDIN_PATTERN,
    NAME_EXCLUDE_KEYWORDS,
    PERCENTAGE_PATTERN,
    PHONE_PATTERNS,
    YEAR_PATTERN,
)
from app.schemas import EducationItem, ExperienceItem, ResumeData
from app.skills import extract_skills


class ResumeExtractor:
    """Orchestrates rule-based resume information extraction."""

    def __init__(self, raw_text: str, blocks_metadata: Optional[List[Dict[str, Any]]] = None):
        """Initializes extractor with raw document text and optional visual block metadata.
        
        Args:
            raw_text: Text extracted from PDF/DOCX parser.
            blocks_metadata: Optional list of PDF text spans with coordinates and styling.
        """
        self.raw_text = raw_text
        self.cleaned_text = clean_text(raw_text)
        self.sections = detect_sections(self.cleaned_text)
        self.blocks_metadata = blocks_metadata or []

    def extract_email(self) -> Optional[str]:
        """Extracts the primary email address from the resume."""
        matches = EMAIL_PATTERN.findall(self.cleaned_text)
        if not matches:
            return None

        for email in matches:
            cleaned_email = email.strip().rstrip(".,;:")
            if "@" in cleaned_email and "." in cleaned_email.split("@")[1]:
                return cleaned_email.lower()
        return None

    def extract_phone(self) -> Optional[str]:
        """Extracts candidate's phone number with multi-format support."""
        search_scope = f"{self.sections.get('HEADER', '')}\n{self.cleaned_text}"

        for pattern in PHONE_PATTERNS:
            matches = pattern.finditer(search_scope)
            for match in matches:
                cleaned_match = match.group(0).strip().rstrip(".,;:|")
                digits_only = re.sub(r"\D", "", cleaned_match)
                if 10 <= len(digits_only) <= 14:
                    if digits_only.startswith(("19", "20")) and len(digits_only) == 4:
                        continue
                    return cleaned_match
        return None

    def extract_linkedin(self) -> Optional[str]:
        """Extracts candidate's LinkedIn profile URL."""
        match = LINKEDIN_PATTERN.search(self.cleaned_text)
        if not match:
            return None

        matched_str = match.group(0).strip().rstrip(".,;:")
        if not matched_str.startswith("http"):
            matched_str = f"https://{matched_str}"
        return matched_str

    def extract_github(self) -> Optional[str]:
        """Extracts candidate's GitHub profile URL."""
        matches = GITHUB_PATTERN.finditer(self.cleaned_text)
        for match in matches:
            username = match.group(1).lower()
            if username in {"topics", "features", "pricing", "collections", "events", "trending"}:
                continue
            matched_str = match.group(0).strip().rstrip(".,;:/")
            if not matched_str.startswith("http"):
                matched_str = f"https://{matched_str}"
            return matched_str
        return None

    def extract_name(self) -> Optional[str]:
        """Extracts candidate's full name using coordinate-aware candidate scoring."""
        # 1. Coordinate-aware candidate scoring from PDF blocks if available
        if self.blocks_metadata:
            # Determine median font size of document for comparison
            sizes = [s["size"] for s in self.blocks_metadata if s.get("text", "").strip()]
            median_size = sorted(sizes)[len(sizes) // 2] if sizes else 10.0

            scored_candidates = []
            for span in self.blocks_metadata:
                text = span.get("text", "").strip()
                bbox = span.get("bbox", (0, 0, 0, 0))
                y0 = bbox[1]
                size = span.get("size", 10.0)
                is_bold = span.get("bold", False)
                page = span.get("page", 0)

                # Focus on page 0 near the visual top
                if page != 0 or y0 > 280.0:
                    continue

                score = self._score_name_candidate(
                    candidate=text,
                    font_size=size,
                    median_size=median_size,
                    is_bold=is_bold,
                    y0=y0
                )
                if score > 50:
                    scored_candidates.append((score, text))

            if scored_candidates:
                scored_candidates.sort(key=lambda x: x[0], reverse=True)
                best_name = scored_candidates[0][1]
                return self._format_name(best_name)

        # 2. Text-based candidate scoring fallback (for DOCX or plain text)
        header_text = self.sections.get("HEADER", "")
        lines = [l.strip() for l in header_text.splitlines() if l.strip()][:10]

        scored_text_candidates = []
        for idx, line in enumerate(lines):
            score = self._score_name_candidate(
                candidate=line,
                font_size=None,
                median_size=None,
                is_bold=False,
                y0=None,
                line_idx=idx
            )
            if score > 40:
                scored_text_candidates.append((score, line))

        # If no valid candidate found in HEADER, inspect the beginning of the full document
        if not scored_text_candidates:
            fallback_lines = [l.strip() for l in self.cleaned_text.splitlines() if l.strip()][:15]
            for idx, line in enumerate(fallback_lines):
                score = self._score_name_candidate(
                    candidate=line,
                    font_size=None,
                    median_size=None,
                    is_bold=False,
                    y0=None,
                    line_idx=idx
                )
                if score > 40:
                    scored_text_candidates.append((score, line))

        if scored_text_candidates:
            scored_text_candidates.sort(key=lambda x: x[0], reverse=True)
            best_name = scored_text_candidates[0][1]
            return self._format_name(best_name)

        return None


    def _score_name_candidate(
        self,
        candidate: str,
        font_size: Optional[float],
        median_size: Optional[float],
        is_bold: bool,
        y0: Optional[float],
        line_idx: Optional[int] = None
    ) -> float:
        """Calculates a heuristic likelihood score for a name candidate string."""
        raw = candidate.strip()
        if not raw or len(raw) < 3 or len(raw) > 45:
            return 0.0

        # Reject contact patterns and URLs
        if "@" in raw or "http" in raw.lower() or "github" in raw.lower() or "linkedin" in raw.lower():
            return 0.0

        # Reject lines with telephone/pincode digits
        if re.search(r"\d{3,}", raw):
            return 0.0

        # Must have 2 to 4 words
        words = re.findall(r"\b[A-Za-z]+(?:\.[A-Za-z]+)?\b", raw)
        if len(words) < 2 or len(words) > 4:
            return 0.0

        lower_words = {w.lower().rstrip(".") for w in words}

        # Reject if matches exclusion keywords (soft skills, section headers, addresses)
        if lower_words.intersection(NAME_EXCLUDE_KEYWORDS):
            return 0.0

        # Reject if matches job titles or degrees
        if any(w.lower() in [j.lower() for j in JOB_TITLE_KEYWORDS] for w in words):
            return 0.0
        if DEGREE_PATTERN.search(raw):
            return 0.0

        # Scoring heuristics
        score = 50.0

        # Font prominence bonus (PDF only)
        if font_size and median_size:
            score += (font_size - median_size) * 4.5
        if is_bold:
            score += 15.0

        # Vertical position bonus
        if y0 is not None:
            score += max(0.0, 30.0 - (y0 / 5.0))
        elif line_idx is not None:
            score += max(0.0, 30.0 - (line_idx * 6.0))

        # Casing patterns
        if raw.isupper():
            score += 15.0
        elif all(w[0].isupper() and (w[1:].islower() or len(w) == 1) for w in words):
            score += 15.0

        # Word count bonus (2-3 words is most common)
        if len(words) in (2, 3):
            score += 10.0

        # Penalize punctuation like colons, dashes, pipes
        if re.search(r"[:;—–\-|/]", raw):
            score -= 30.0

        return score

    def _format_name(self, candidate: str) -> str:
        """Formats the extracted name, preserving original ALL CAPS if present."""
        words = re.findall(r"\b[A-Za-z]+(?:\.[A-Za-z]+)?\b", candidate)
        if candidate.isupper():
            return " ".join(w.upper() for w in words)
        return " ".join(w.capitalize() if not w.endswith(".") else w.upper() for w in words)

    def extract_skills(self) -> List[str]:
        """Extracts candidate's skills list prioritizing technical skills section."""
        skills_sec = self.sections.get("TECHNICAL_SKILLS") or self.sections.get("SKILLS", "")
        return extract_skills(self.cleaned_text, skills_sec)

    def extract_education(self) -> List[EducationItem]:
        """Extracts education credentials, institutions, and metrics."""
        edu_text = self.sections.get("EDUCATION", "")
        if not edu_text:
            edu_text = self.cleaned_text

        items: List[EducationItem] = []
        lines = [l.strip() for l in edu_text.splitlines() if l.strip()]

        # Find all lines containing degree patterns
        degree_indices = []
        for i, line in enumerate(lines):
            if DEGREE_PATTERN.search(line):
                degree_indices.append(i)

        inst_kw = re.compile(
            r"\b(?:College|Institute|School|Vidyalaya|Academy|Campus|IIT|NIT|BITS)\b",
            re.IGNORECASE
        )
        univ_kw = re.compile(
            r"\b(?:University|Univ\.?)\b",
            re.IGNORECASE
        )

        for k, deg_idx in enumerate(degree_indices):
            deg_line = lines[deg_idx]

            # Extract degree title from the line
            deg_parts = [p.strip() for p in re.split(r"\s*\|\s*", deg_line) if p.strip()]
            deg_name = None
            for p in deg_parts:
                if DEGREE_PATTERN.search(p):
                    deg_name = p
                    break
            if not deg_name:
                deg_match = DEGREE_PATTERN.search(deg_line)
                deg_name = deg_match.group(0).strip() if deg_match else deg_line

            # Determine line scope partition around this degree
            start_idx = 0 if k == 0 else (degree_indices[k - 1] + deg_idx) // 2 + 1
            end_idx = len(lines) if k == len(degree_indices) - 1 else (deg_idx + degree_indices[k + 1]) // 2 + 1
            scope_lines = lines[start_idx:end_idx]

            inst_val = None
            univ_val = None
            year_val = None
            cgpa_val = None
            pct_val = None

            for l in scope_lines:
                parts = [p.strip() for p in re.split(r"\s*\|\s*", l) if p.strip()]
                for part in parts:
                    if DEGREE_PATTERN.search(part):
                        continue

                    # Dates
                    dm = DATE_RANGE_PATTERN.search(part)
                    if dm and not year_val:
                        year_val = dm.group(0).strip()
                    elif not year_val:
                        ym = YEAR_PATTERN.findall(part)
                        if ym:
                            year_val = ym[-1]

                    # CGPA
                    cm = CGPA_PATTERN.search(part)
                    if cm and not cgpa_val:
                        cgpa_val = cm.group(1).strip()

                    # Percentage
                    pm = PERCENTAGE_PATTERN.search(part)
                    if pm and not pct_val:
                        pct_val = pm.group(1).strip()

                    # University
                    if univ_kw.search(part) and not univ_val:
                        univ_val = part.rstrip(".,;-|")
                    # Institution
                    elif inst_kw.search(part) and not inst_val:
                        inst_val = part.rstrip(".,;-|")

            # Fallback institution if not found
            if not inst_val and univ_val:
                inst_val = univ_val
                univ_val = None

            # Deduplicate by degree name
            if not any(item.degree.lower() == deg_name.lower() for item in items):
                items.append(EducationItem(
                    degree=deg_name,
                    institution=inst_val,
                    year=year_val,
                    university=univ_val,
                    cgpa=cgpa_val,
                    percentage=pct_val
                ))

        return items

    def extract_experience(self) -> List[ExperienceItem]:
        """Extracts work experience roles, companies, and durations."""
        exp_text = self.sections.get("EXPERIENCE", "")
        if not exp_text:
            return []

        items: List[ExperienceItem] = []
        lines = [l.strip() for l in exp_text.splitlines() if l.strip()]
        sorted_titles = sorted(JOB_TITLE_KEYWORDS, key=len, reverse=True)

        for i, line in enumerate(lines):
            matched_title = None
            for title_keyword in sorted_titles:
                if re.search(rf"\b{re.escape(title_keyword)}\b", line, re.IGNORECASE):
                    matched_title = title_keyword
                    break

            if matched_title:
                # 1. Extract duration
                duration_val = None
                dur_match = DATE_RANGE_PATTERN.search(line)
                if dur_match:
                    duration_val = dur_match.group(0).strip()
                else:
                    for forward_line in lines[i + 1: min(len(lines), i + 3)]:
                        dur_match = DATE_RANGE_PATTERN.search(forward_line)
                        if dur_match:
                            duration_val = dur_match.group(0).strip()
                            break

                # 2. Extract company name
                company_val = None
                comp_match = re.search(
                    r"(?:at|@|with|-|\|)\s+([A-Z][A-Za-z0-9\s&.,'-]+)",
                    line
                )
                if comp_match:
                    cand = comp_match.group(1).strip().rstrip(".,;-|")
                    if duration_val and cand.startswith(duration_val):
                        cand = None
                    elif cand and cand.lower() != matched_title.lower() and len(cand.split()) <= 6:
                        cand = DATE_RANGE_PATTERN.sub("", cand).strip().rstrip(".,;-(|")
                        if cand:
                            company_val = cand

                if not company_val:
                    for forward_line in lines[i + 1: min(len(lines), i + 3)]:
                        if duration_val and duration_val in forward_line:
                            continue
                        if forward_line.startswith(("-", "•", "*")):
                            continue
                        if any(re.search(rf"\b{re.escape(tk)}\b", forward_line, re.IGNORECASE) for tk in sorted_titles):
                            break
                        if 1 <= len(forward_line.split()) <= 6:
                            company_val = forward_line.rstrip(".,;-|")
                            break

                items.append(ExperienceItem(
                    title=matched_title,
                    company=company_val,
                    duration=duration_val
                ))

        return items

    def extract_all(self) -> ResumeData:
        """Runs full extraction pipeline and returns validated ResumeData."""
        return ResumeData(
            name=self.extract_name(),
            email=self.extract_email(),
            phone=self.extract_phone(),
            skills=self.extract_skills(),
            education=self.extract_education(),
            experience=self.extract_experience(),
            linkedin=self.extract_linkedin(),
            github=self.extract_github()
        )

