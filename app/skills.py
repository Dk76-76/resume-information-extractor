"""Predefined skills taxonomy and boundary-safe skill extraction engine."""

import re
from typing import Dict, List, Optional, Set

# Comprehensive categorized technical & professional skills
SKILLS_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C",
        "Go", "Golang", "Rust", "Kotlin", "Swift", "Ruby", "PHP", "Scala",
        "Dart", "R", "SQL", "Bash", "Shell", "PowerShell", "Perl", "Lua",
        "HTML", "HTML5", "CSS", "CSS3", "Sass", "SCSS"
    ],
    "Frameworks & Libraries": [
        "FastAPI", "Flask", "Django", "React", "React.js", "Angular", "Vue",
        "Vue.js", "Next.js", "Nuxt.js", "Node.js", "Express", "Express.js",
        "Spring", "Spring Boot", "ASP.NET", ".NET", "Ruby on Rails", "Laravel",
        "Tailwind CSS", "Bootstrap", "jQuery", "Redux", "GraphQL", "REST APIs",
        "REST API", "gRPC", "WebSockets", "Streamlit"
    ],
    "Databases & Storage": [
        "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle",
        "Microsoft SQL Server", "Cassandra", "DynamoDB", "Elasticsearch",
        "Firebase", "Supabase", "MariaDB", "Neo4j", "CouchDB"
    ],
    "Cloud & DevOps": [
        "AWS", "Amazon Web Services", "Microsoft Azure", "Azure", "GCP",
        "Google Cloud", "Google Cloud Platform", "Docker", "Kubernetes",
        "Terraform", "Ansible", "Jenkins", "GitHub Actions", "GitLab CI",
        "CI/CD", "Linux", "Nginx", "Apache", "Helm", "Prometheus", "Grafana",
        "Railway", "Render", "Heroku", "Vercel", "Netlify"
    ],
    "AI, Machine Learning & Data": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence",
        "Natural Language Processing", "NLP", "Computer Vision", "Data Analysis",
        "Data Science", "Pandas", "NumPy", "Scikit-Learn", "Scikit-learn", "TensorFlow",
        "PyTorch", "Keras", "OpenCV", "SciPy", "Matplotlib", "Seaborn",
        "Tableau", "Power BI", "Large Language Models", "LLM", "Hugging Face",
        "Spark", "Apache Spark", "Hadoop", "Kafka", "RAG", "LangChain",
        "FAISS", "CNN", "Transfer Learning", "Generative AI"
    ],
    "Tools & Concepts": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Postman", "Swagger",
        "Linux", "Unix", "Agile", "Scrum", "Microservices", "Unit Testing",
        "TDD", "Object-Oriented Programming", "OOP", "Data Structures",
        "Algorithms", "System Design", "CI/CD Pipeline", "Jupyter Notebook",
        "Google Colab"
    ]
}

# Canonical normalization mapping: canonical name -> variants/aliases
SKILL_ALIASES: Dict[str, List[str]] = {
    "C++": ["c++", "cpp"],
    "C#": ["c#", "c-sharp", "csharp"],
    ".NET": [".net", "dotnet"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "Next.js": ["next.js", "nextjs", "next js"],
    "Vue.js": ["vue.js", "vuejs", "vue"],
    "React": ["react", "react.js", "reactjs"],
    "Express.js": ["express.js", "expressjs", "express"],
    "Go": ["golang", "go language"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "AWS": ["aws", "amazon web services"],
    "GCP": ["gcp", "google cloud platform", "google cloud"],
    "Azure": ["azure", "microsoft azure"],
    "Machine Learning": ["machine learning", "ml"],
    "Natural Language Processing": ["natural language processing", "nlp"],
    "Artificial Intelligence": ["artificial intelligence", "ai"],
    "Scikit-learn": ["scikit-learn", "scikit-learn", "scikit learn", "sklearn"],
    "REST APIs": ["rest apis", "rest api", "restful api", "restful apis", "rest"],
    "Jupyter Notebook": ["jupyter notebook", "jupyter notebooks", "jupyter"],
    "Google Colab": ["google colab", "colab"],
    "Transfer Learning": ["transfer learning"],
    "Deep Learning": ["deep learning"],
    "Computer Vision": ["computer vision"],
    "Generative AI": ["generative ai", "genai"],
    "Data Structures & Algorithms": ["dsa", "data structures and algorithms", "data structures"],
    "CI/CD": ["ci/cd", "ci-cd", "continuous integration"]
}

# Soft skills that must NEVER be returned as technical skills
SOFT_SKILL_EXCLUSIONS: Set[str] = {
    "problem solving", "analytical thinking", "critical thinking",
    "team collaboration", "collaboration", "communication",
    "continuous learning", "leadership", "time management", "adaptability",
    "creativity", "work ethic", "attention to detail", "emotional intelligence",
    "decision making", "interpersonal skills", "teamwork", "multitasking"
}

# Special skills requiring custom boundary matching (cannot use standard \b)
SPECIAL_SKILL_PATTERNS = {
    "C++": re.compile(r"(?:\b|(?<=[\s,/(]))C\+\+(?=[\s,;/)\.\n]|$)", re.IGNORECASE),
    "C#": re.compile(r"(?:\b|(?<=[\s,/(]))C#(?=[\s,;/)\.\n]|$)", re.IGNORECASE),
    ".NET": re.compile(r"(?:\b|(?<=[\s,/(]))\.NET(?=[\s,;/)\.\n]|$)", re.IGNORECASE),
    "C": re.compile(r"(?:\b|(?<=[\s,/(]))C(?=[\s,;/)\.\n]|$)", re.IGNORECASE),
    "R": re.compile(r"(?:\b|(?<=[\s,/(]))R(?=[\s,;/)\.\n]|$)", re.IGNORECASE),
}

# Build flat set of all canonical skills
ALL_CANONICAL_SKILLS: Set[str] = set()
for category_skills in SKILLS_TAXONOMY.values():
    ALL_CANONICAL_SKILLS.update(category_skills)


def _build_regex_for_skill(skill: str) -> re.Pattern:
    """Creates a boundary-safe regex pattern for a given skill name."""
    escaped = re.escape(skill)
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


# Pre-compile regex for all standard skills
STANDARD_SKILL_PATTERNS: Dict[str, re.Pattern] = {}
for skill in ALL_CANONICAL_SKILLS:
    if skill not in SPECIAL_SKILL_PATTERNS:
        STANDARD_SKILL_PATTERNS[skill] = _build_regex_for_skill(skill)


def _canonicalize_skill_name(raw_name: str) -> Optional[str]:
    """Resolves a skill name to its canonical version if known, or cleans and returns."""
    cleaned = raw_name.strip().rstrip(".,;:")
    if not cleaned or len(cleaned) < 2:
        return None

    lower = cleaned.lower()
    if lower in SOFT_SKILL_EXCLUSIONS:
        return None

    # Check canonical aliases
    for canonical, aliases in SKILL_ALIASES.items():
        if lower == canonical.lower() or lower in [a.lower() for a in aliases]:
            return canonical

    # Check canonical taxonomy
    for canonical in ALL_CANONICAL_SKILLS:
        if lower == canonical.lower():
            return canonical

    # Avoid common non-skill noise
    if lower in {"and", "with", "using", "various", "other", "tools", "libraries", "programming", "languages"}:
        return None

    # Return as-is if reasonable length and format
    if len(cleaned) <= 35:
        return cleaned

    return None


def extract_skills_from_section_categories(section_text: str) -> List[str]:
    """Parses category lines such as 'Category: Skill1, Skill2, Skill3'."""
    parsed: Set[str] = set()
    category_pattern = re.compile(r"^([A-Za-z0-9\s/&+-]{2,40}):\s*(.+)$")

    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        m = category_pattern.match(stripped)
        if m:
            _, items_str = m.group(1), m.group(2)
            # Split items by comma, semicolon, bullet, or vertical bar
            raw_items = re.split(r"[,;•|]+", items_str)
            for item in raw_items:
                canon = _canonicalize_skill_name(item)
                if canon:
                    parsed.add(canon)

    return list(parsed)


def extract_skills(full_text: str, skills_section_text: Optional[str] = None) -> List[str]:
    """Extracts unique, canonical skills from resume text.
    
    Args:
        full_text: Entire resume text.
        skills_section_text: Specifically isolated technical skills section if detected.
        
    Returns:
        Sorted list of uniquely identified skill names.
    """
    detected_skills: Set[str] = set()

    # 1. If a technical skills section exists, parse category lines directly
    if skills_section_text and skills_section_text.strip():
        category_skills = extract_skills_from_section_categories(skills_section_text)
        for s in category_skills:
            detected_skills.add(s)

    # Determine search scope: prefer skills section if available, but fallback to full text
    search_target = f"{skills_section_text or ''}\n{full_text}"

    # 2. Match special symbols (C++, C#, .NET)
    for skill_name, pattern in SPECIAL_SKILL_PATTERNS.items():
        if skill_name in ("C", "R"):
            # Only match "C" or "R" if present in the skills section
            target = skills_section_text if skills_section_text else ""
            if target and pattern.search(target):
                detected_skills.add(skill_name)
        else:
            if pattern.search(search_target):
                detected_skills.add(skill_name)

    # 3. Check canonical aliases
    for canonical_name, aliases in SKILL_ALIASES.items():
        if canonical_name in detected_skills:
            continue
        for alias in aliases:
            if alias in ["c++", "c#", ".net"]:
                continue
            alias_pattern = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
            if alias_pattern.search(search_target):
                detected_skills.add(canonical_name)
                break

    # 4. Standard boundary-safe matching against taxonomy
    for skill_name, pattern in STANDARD_SKILL_PATTERNS.items():
        if skill_name in detected_skills:
            continue
        
        # Avoid generic "Go" matching plain English verbs
        if skill_name == "Go":
            if skills_section_text and pattern.search(skills_section_text):
                detected_skills.add("Go")
            continue

        if pattern.search(search_target):
            detected_skills.add(skill_name)

    # 5. Filter out soft skills and deduplicate case-insensitively
    seen_lower = set()
    unique_skills = []
    # Sort with preference for canonical capitalization
    for s in sorted(detected_skills, key=lambda x: (x.islower(), x.lower())):
        s_clean = s.strip()
        s_lower = s_clean.lower()
        if s_lower in SOFT_SKILL_EXCLUSIONS or s_lower in seen_lower:
            continue
        seen_lower.add(s_lower)
        unique_skills.append(s_clean)

    # Return sorted alphabetically case-insensitively
    return sorted(unique_skills, key=lambda s: s.lower())

