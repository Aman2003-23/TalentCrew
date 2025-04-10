import re
import spacy
import streamlit as st

# Load spaCy model for NLP processing
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # If model not found, download it
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

def extract_name(text, nlp=None):
    """Extract candidate name from resume text"""
    if nlp is None:
        nlp = load_spacy_model()
    
    # Process the first 500 characters of text where name is likely to appear
    doc = nlp(text[:500])
    
    # Look for person names in the processed text
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    
    # Fallback: try to find a name pattern at the beginning of the resume
    name_pattern = r'^([A-Z][a-z]+ [A-Z][a-z]+)'
    match = re.search(name_pattern, text.strip())
    if match:
        return match.group(1)
    
    return "Unknown Name"

def extract_email(text):
    """Extract email from resume text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    if match:
        return match.group(0)
    return "unknown@example.com"

def extract_skills(text, nlp=None):
    """Extract skills from resume text"""
    if nlp is None:
        nlp = load_spacy_model()
    
    # Common skills to look for
    skill_keywords = [
        "python", "java", "javascript", "html", "css", "sql", "nosql", 
        "react", "angular", "vue", "node", "django", "flask", "php",
        "aws", "azure", "gcp", "docker", "kubernetes", "devops",
        "machine learning", "ai", "data science", "nlp", "computer vision",
        "project management", "agile", "scrum", "kanban",
        "leadership", "communication", "teamwork", "problem solving",
        "sales", "marketing", "finance", "accounting", "hr", "recruitment"
    ]
    
    found_skills = []
    
    # Create a pattern for each skill (using word boundaries)
    for skill in skill_keywords:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text.lower()):
            found_skills.append(skill)
    
    return found_skills

def extract_experience(text):
    """Extract years of experience from resume text"""
    # Look for experience patterns like "X years of experience"
    experience_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience\s+(?:of\s+)?(\d+)\+?\s*years?',
        r'worked\s+(?:for\s+)?(\d+)\+?\s*years?'
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, text.lower())
        if match:
            years = int(match.group(1))
            return years
    
    return 0  # Default if no experience info found

def parse_resume(resume_text):
    """Parse resume text to extract relevant information"""
    try:
        nlp = load_spacy_model()
        
        # Extract information
        name = extract_name(resume_text, nlp)
        email = extract_email(resume_text)
        skills = extract_skills(resume_text, nlp)
        experience_years = extract_experience(resume_text)
        
        # Create structured resume data
        resume_data = {
            "name": name,
            "email": email,
            "skills": skills,
            "experience_years": experience_years,
            "raw_text": resume_text
        }
        
        return resume_data
    except Exception as e:
        st.error(f"Error parsing resume: {str(e)}")
        return {
            "name": "Unknown Candidate",
            "email": "unknown@example.com",
            "skills": [],
            "experience_years": 0,
            "raw_text": resume_text
        }

def match_job_description(resume_data, job_description):
    """Match resume against job description for screening"""
    try:
        nlp = load_spacy_model()
        
        # Extract required skills from job description
        job_doc = nlp(job_description)
        
        # Extract skills from job description (simple approach)
        skills_in_job = extract_skills(job_description, nlp)
        
        # Compare skills
        matching_skills = [skill for skill in resume_data["skills"] if skill in skills_in_job]
        
        # Calculate a simple match score
        match_score = 0
        if skills_in_job:  # Avoid division by zero
            match_score = len(matching_skills) / len(skills_in_job) * 100
        
        # Check experience requirements
        experience_pattern = r'(\d+)\+?\s*years?\s+(?:of\s+)?experience'
        exp_match = re.search(experience_pattern, job_description.lower())
        
        experience_match = False
        required_experience = 0
        
        if exp_match:
            required_experience = int(exp_match.group(1))
            experience_match = resume_data["experience_years"] >= required_experience
        
        # Return structured result
        return {
            "match_score": match_score,
            "matching_skills": matching_skills,
            "missing_skills": [s for s in skills_in_job if s not in resume_data["skills"]],
            "experience_match": experience_match,
            "experience_gap": max(0, required_experience - resume_data["experience_years"])
        }
    except Exception as e:
        st.error(f"Error matching job description: {str(e)}")
        return {
            "match_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "experience_match": False,
            "experience_gap": 0
        }
