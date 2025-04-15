import re
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
from typing import List

def extract_skills_efficient(descriptions: pd.Series) -> List[List[str]]:
    """
    Extract skills from job descriptions using CountVectorizer.
    Much more efficient for large datasets.
    
    Args:
        descriptions: Series of job descriptions
    
    Returns:
        List of lists containing extracted skills for each description
    """
    # Define skills vocabulary - extend as needed
    skill_vocab = [
        # Programming Languages
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "php", "ruby", "scala", "kotlin", "swift", "perl", "r",
        # Web Development
        "html", "css", "jquery", "bootstrap", "react", "angular", "vue", "node", "express", "django", "flask", "spring", "asp.net", "mvc",
        # Mobile
        "android", "ios", "react native", "flutter", "xamarin", "mobile development",
        # Databases
        "sql", "mysql", "postgresql", "mongodb", "nosql", "oracle", "sqlserver", "redis", "elasticsearch", "cassandra", "dynamodb",
        # Cloud & DevOps
        "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "terraform", "ansible", "ci/cd", "devops", "cloud", "serverless",
        # Data Science & ML
        "machine learning", "ai", "artificial intelligence", "data science", "deep learning", "nlp", "computer vision", "tensorflow", "pytorch", "pandas", "numpy", "scikit", "jupyter",
        # Big Data
        "hadoop", "spark", "kafka", "big data", "data engineering", "etl", "data warehouse", "data lake", "airflow",
        # Design & Frontend
        "ui", "ux", "user interface", "user experience", "figma", "sketch", "adobe", "photoshop", "illustrator", "responsive design", "sass", "less",
        # Testing & QA
        "testing", "qa", "quality assurance", "selenium", "junit", "pytest", "cucumber", "cypress", "jest", "mocha",
        # Version Control
        "git", "github", "gitlab", "bitbucket", "svn", "version control",
        # Methodologies
        "agile", "scrum", "kanban", "jira", "confluence", "tdd", "bdd", "waterfall", "lean",
        # Soft Skills
        "communication", "teamwork", "leadership", "problem solving", "critical thinking", "creativity", "collaboration", "time management",
        # Business Skills
        "project management", "product management", "business analysis", "marketing", "sales", "finance", "accounting", "hr", "recruiting"
    ]
    
    # Fill NaN values
    clean_descriptions = descriptions.fillna("").str.lower()
    
    # Initialize vectorizer with our skills vocabulary
    vectorizer = CountVectorizer(vocabulary=skill_vocab)
    
    # Transform descriptions to document-term matrix
    skill_matrix = vectorizer.fit_transform(clean_descriptions)
    
    # Convert to lists of skills
    all_skills = []
    feature_names = vectorizer.get_feature_names_out()
    
    for i in range(skill_matrix.shape[0]):
        # Get indices of non-zero elements (skills that appear in the description)
        indices = skill_matrix[i].nonzero()[1]
        # Get the corresponding skill names
        doc_skills = [feature_names[idx].title() for idx in indices]
        all_skills.append(doc_skills)
    
    return all_skills

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing HTML tags, extra whitespace, etc.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    import re
    
    if pd.isna(text):
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<.*?>', ' ', text)
    # Replace newlines with spaces
    text = re.sub(r'\n', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def normalize_skills(skills_str):
    """Normalize skills string formatting."""
    if pd.isna(skills_str) or skills_str == "":
        return ""
    
    # Remove any 'skills:' prefix that might appear in the text
    skills_str = re.sub(r'^(skills:\s*)', '', skills_str, flags=re.IGNORECASE)
    
    # Remove phrases like "This position requires the following skills:"
    skills_str = re.sub(r'.*?(requires|following)\s*skills:?', '', skills_str, flags=re.IGNORECASE)
    
    # Split by commas, clean each skill, and rejoin
    if "," in skills_str:
        skills = [skill.strip() for skill in skills_str.split(',')]
        skills = [skill for skill in skills if skill]  # Remove empty strings
        return ", ".join(skills)
    
    return skills_str.strip()

def clean_combined_skills(skills_str):
    """Clean up and deduplicate skills."""
    if not skills_str:
        return ""
    
    # Split by comma and clean each skill
    skills = [skill.strip() for skill in skills_str.split(',')]
    
    # Remove empty strings
    skills = [skill for skill in skills if skill]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_skills = []
    for skill in skills:
        if skill.lower() not in seen:
            seen.add(skill.lower())
            unique_skills.append(skill)
    
    return ", ".join(unique_skills)

def is_software_job(title, description):
    """
    Determine if a job is software engineering related.
    Returns True for software/tech jobs, False otherwise.
    """
    # Expand software keywords for better filtering
    software_keywords = [
        # Core software roles
        'software', 'developer', 'programmer', 'coder', 'engineer', 
        'web developer', 'mobile developer', 'app developer',
        
        # Specialized software roles
        'frontend', 'backend', 'fullstack', 'full stack', 'full-stack',
        'devops', 'sre', 'site reliability', 'cloud engineer',
        
        # Programming languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
        'scala', 'kotlin', 'swift', '.net', 'perl',
        
        # Web tech
        'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring', 'rails',
        
        # Data tech
        'data scientist', 'data engineer', 'machine learning', 'ml engineer', 
        'ai engineer', 'deep learning', 'nlp', 'computer vision',
        
        # CS terms
        'computer science', 'algorithm', 'data structure'
    ]
    
    # Terms that might appear in non-tech jobs but should not count alone
    weak_tech_terms = [
        'development', 'technical', 'technology', 'it', 'computer',
        'system', 'platform', 'digital', 'web', 'application'
    ]
    
    # Definitely not software jobs if these appear in title
    exclusion_terms = [
        'sales', 'marketing', 'recruiter', 'hr', 'finance', 'accounting',
        'customer service', 'support', 'manager', 'director', 'vp',
        'assistant', 'coordinator', 'specialist', 'representative',
        'operation', 'driver', 'nurse', 'doctor', 'teacher'
    ]
    
    title_lower = title.lower() if not pd.isna(title) else ""
    desc_lower = description.lower() if not pd.isna(description) else ""
    
    # Check for explicit exclusions in the title
    for term in exclusion_terms:
        if term in title_lower and not any(sw in title_lower for sw in software_keywords):
            return False
    
    # Check for strong signals in the title (highest confidence)
    for keyword in software_keywords:
        if keyword in title_lower:
            return True
    
    # Check for combinations of weak signals in the title
    weak_term_count = sum(1 for term in weak_tech_terms if term in title_lower)
    if weak_term_count >= 2:
        return True
    
    # Fall back to description checks if title didn't give a clear signal
    strong_keyword_count = sum(1 for keyword in software_keywords if keyword in desc_lower)
    weak_keyword_count = sum(1 for term in weak_tech_terms if term in desc_lower)
    
    # Require multiple strong keywords or a combination of strong and weak
    if strong_keyword_count >= 2 or (strong_keyword_count >= 1 and weak_keyword_count >= 2):
        return True
    
    return False