# utils/matcher.py
def match_score(resume_text, required_skills):
    resume_text_lower = resume_text.lower()
    matching_skills = [
        skill for skill in required_skills
        if skill.lower() in resume_text_lower
    ]
    score = len(matching_skills) / len(
        required_skills) if required_skills else 0
    return round(score * 100, 2), matching_skills
