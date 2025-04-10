import os
import chromadb
from chromadb.config import Settings
from datetime import datetime, timedelta
import uuid
import random
import streamlit as st

# Default collection names
RESUME_COLLECTION = "resume_collection"
LOG_COLLECTION = "log_collection"
CANDIDATE_COLLECTION = "candidate_collection"

def seed_more_data():
    """Seed the database with additional jobs and candidates"""
    print("Seeding more data...")
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(
            anonymized_telemetry=False
        )
    )
    
    collection = client.get_collection(CANDIDATE_COLLECTION)
    
    # Additional job positions to seed
    job_positions = [
        "Data Scientist",
        "Product Manager",
        "UX Designer",
        "DevOps Engineer",
        "Marketing Specialist"
    ]
    
    # Sample candidate names for each position
    candidate_names = {
        "Data Scientist": [
            "Alex Rodriguez", "Maya Patel", "Tomas Berg", "Sophia Chen", "Raj Kumar",
            "Fatima Al-Hassan", "Marcus Johnson", "Aisha Thompson"
        ],
        "Product Manager": [
            "Diana Lee", "Carlos Mendez", "Natalie Wong", "David Kim", "Rachel Green",
            "Jamal Scott", "Emma Wilson", "Lucas Martinez"
        ],
        "UX Designer": [
            "Noah Parker", "Lily Jackson", "Kai Tanaka", "Zoe Adams", "Omar Farouk",
            "Isabella Rossi", "Mateo Sanchez", "Ava Murphy"
        ],
        "DevOps Engineer": [
            "Ethan Wright", "Olivia Davis", "Sanjay Patel", "Chloe Baker", "Mohammed Ali",
            "Hiro Nakamura", "Samantha Lee", "Gabriel Thompson"
        ],
        "Marketing Specialist": [
            "Elena Rodriguez", "Benjamin Taylor", "Mia Johnson", "Jackson Wang", "Nadia Abbas",
            "Daniel Miller", "Sofia Garcia", "Liam Campbell"
        ]
    }
    
    # Sample sources
    sources = ["LinkedIn", "Indeed", "Internal Database", "GitHub", "Referral", "Job Fair", "Stack Overflow"]
    
    # Skills by position
    position_skills = {
        "Data Scientist": [
            "Python", "R", "SQL", "Machine Learning", "TensorFlow", "PyTorch", "scikit-learn", 
            "Data Visualization", "Statistics", "Pandas", "NumPy", "Big Data", "Hadoop", "Spark"
        ],
        "Product Manager": [
            "Agile", "Scrum", "User Stories", "Roadmapping", "A/B Testing", "Market Analysis",
            "Stakeholder Management", "Wireframing", "Product Strategy", "Competitive Analysis",
            "User Research", "KPI Tracking", "Prioritization"
        ],
        "UX Designer": [
            "Figma", "Sketch", "Adobe XD", "Wireframing", "Prototyping", "User Testing",
            "Information Architecture", "UI Design", "User Research", "Usability Testing",
            "Design Systems", "Interaction Design", "Accessibility"
        ],
        "DevOps Engineer": [
            "Docker", "Kubernetes", "AWS", "Azure", "GCP", "CI/CD", "Jenkins", "Terraform",
            "Ansible", "GitHub Actions", "Linux", "Shell Scripting", "Monitoring", "Prometheus"
        ],
        "Marketing Specialist": [
            "SEO", "Content Marketing", "Social Media", "Analytics", "Campaign Management",
            "Email Marketing", "Google Ads", "Facebook Ads", "CRM", "Marketing Automation",
            "Copywriting", "Brand Management", "Market Research"
        ]
    }
    
    all_candidates = []
    stage_distrib = ["sourced", "screened", "engaged", "scheduled"]
    
    # Generate candidates for each job position
    for job_title in job_positions:
        # Between 4-8 candidates per position
        num_candidates = random.randint(4, 8)
        names = random.sample(candidate_names[job_title], num_candidates)
        relevant_skills = position_skills[job_title]
        
        for name in names:
            # Create email from name
            email = f"{name.lower().replace(' ', '.')}@example.com"
            
            # Choose source
            source = random.choice(sources)
            
            # Determine stage with distribution skewed towards early stages
            weights = [0.4, 0.3, 0.2, 0.1]  # More candidates in sourced, fewer in scheduled
            stage = random.choices(stage_distrib, weights=weights)[0]
            
            # Choose skills (between 3-7) from the position's relevant skills
            num_skills = random.randint(3, min(7, len(relevant_skills)))
            skills = ", ".join(random.sample(relevant_skills, num_skills))
            
            # Basic metadata
            candidate_id = str(uuid.uuid4())
            experience_years = random.randint(1, 10)
            
            metadata = {
                "name": name,
                "email": email,
                "source": source,
                "job_title": job_title,
                "stage": stage,
                "skills": skills,
                "experience_years": experience_years
            }
            
            # Add stage-specific metadata
            if stage in ["screened", "engaged", "scheduled"]:
                match_score = random.randint(60, 95)
                metadata["match_score"] = match_score
                
                # Matching skills (subset of skills)
                matching_skills_count = random.randint(2, min(4, len(relevant_skills)))
                metadata["matching_skills"] = ", ".join(random.sample(relevant_skills[:8], matching_skills_count))
                
                # Missing skills (skills not in matching)
                missing_skills_count = random.randint(1, 3)
                metadata["missing_skills"] = ", ".join(random.sample(relevant_skills[8:], missing_skills_count))
                
                metadata["experience_match"] = "Yes" if random.random() > 0.3 else "No"
            
            if stage in ["engaged", "scheduled"]:
                is_interested = True if random.random() > 0.2 else False
                metadata["is_interested"] = is_interested
                metadata["engaged"] = True
                
                # Create an engagement message
                metadata["engagement_message"] = f"""
                Subject: Exciting {job_title} Opportunity
                
                Hi {name},
                
                I hope this message finds you well. I'm reaching out because your profile caught our attention.
                
                Your skills in {metadata["matching_skills"]} align well with what we're looking for in our {job_title} position.
                
                Would you be interested in learning more about this opportunity? If so, I'd be happy to provide additional details.
                
                Looking forward to hearing from you.
                
                Best regards,
                TalentCrew AI Recruiting Team
                """
            
            if stage == "scheduled":
                # Generate a future interview date
                days_ahead = random.randint(1, 10)
                interview_date = (datetime.now() + timedelta(days=days_ahead)).replace(
                    hour=random.randint(9, 16),
                    minute=random.choice([0, 15, 30, 45]),
                    second=0,
                    microsecond=0
                )
                
                metadata["scheduled"] = True
                metadata["interview_datetime"] = interview_date.isoformat()
            
            # Generate a resume text
            resume_text = f"""
            {name}
            {email}
            
            Summary:
            Experienced {job_title} with {experience_years} years of experience.
            
            Skills:
            {skills}
            
            Experience:
            - Senior {job_title} at Example Corp (2020-Present)
              Led projects and delivered successful outcomes
              
            - {job_title} at Sample Inc (2017-2020)
              Developed and implemented solutions
              
            Education:
            - Bachelor's Degree in {"Computer Science" if job_title in ["Data Scientist", "DevOps Engineer"] else "Business" if job_title == "Product Manager" else "Design" if job_title == "UX Designer" else "Marketing"}, Example University
            """
            
            # Add to the collection
            collection.add(
                ids=[candidate_id],
                metadatas=[metadata],
                documents=[resume_text]
            )
            
            all_candidates.append(metadata)
    
    # Add log entries for the new candidates
    log_collection = client.get_collection(LOG_COLLECTION)
    
    # Generate some log entries for the activities
    for candidate in all_candidates:
        # Source log
        log_id = str(uuid.uuid4())
        timestamp = (datetime.now() - timedelta(days=random.randint(1, 5))).timestamp()
        log_collection.add(
            ids=[log_id],
            metadatas=[{
                "agent": "Sourcing Agent",
                "action": "source_candidate",
                "status": "success",
                "timestamp": timestamp
            }],
            documents=[f"Sourced candidate {candidate['name']} from {candidate['source']}"]
        )
        
        # Add logs based on stage
        if candidate["stage"] in ["screened", "engaged", "scheduled"]:
            log_id = str(uuid.uuid4())
            timestamp = (datetime.now() - timedelta(days=random.randint(1, 4))).timestamp()
            log_collection.add(
                ids=[log_id],
                metadatas=[{
                    "agent": "Screening Agent",
                    "action": "screen_candidate",
                    "status": "success",
                    "timestamp": timestamp
                }],
                documents=[f"Screened {candidate['name']} with score {candidate.get('match_score', 0)}%"]
            )
        
        if candidate["stage"] in ["engaged", "scheduled"]:
            log_id = str(uuid.uuid4())
            timestamp = (datetime.now() - timedelta(days=random.randint(1, 3))).timestamp()
            interest = "interested" if candidate.get("is_interested", False) else "not interested"
            log_collection.add(
                ids=[log_id],
                metadatas=[{
                    "agent": "Engagement Agent",
                    "action": "engage_candidate",
                    "status": "success",
                    "timestamp": timestamp
                }],
                documents=[f"Engaged {candidate['name']} who was {interest}"]
            )
        
        if candidate["stage"] == "scheduled":
            log_id = str(uuid.uuid4())
            timestamp = (datetime.now() - timedelta(days=random.randint(1, 2))).timestamp()
            log_collection.add(
                ids=[log_id],
                metadatas=[{
                    "agent": "Scheduling Agent",
                    "action": "schedule_interview",
                    "status": "success",
                    "timestamp": timestamp
                }],
                documents=[f"Scheduled interview for {candidate['name']} at {candidate.get('interview_datetime', '')}"]
            )
    
    print(f"Successfully added {len(all_candidates)} new candidates across {len(job_positions)} job positions")
    print("Added corresponding log entries for each candidate's actions")
    return len(all_candidates)
    
if __name__ == "__main__":
    seed_more_data()