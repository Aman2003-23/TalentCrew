import os
import chromadb
from chromadb.config import Settings
from datetime import datetime, timedelta
import uuid
import random

# Default collection names
RESUME_COLLECTION = "resume_collection"
LOG_COLLECTION = "log_collection"
CANDIDATE_COLLECTION = "candidate_collection"

def init_database():
    """Initialize and seed the database with sample data"""
    print("Initializing and seeding database...")
    
    # Create the directory if it doesn't exist
    if not os.path.exists("./chroma_db"):
        os.makedirs("./chroma_db")
        
    # Create a persistent client
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(
            anonymized_telemetry=False
        )
    )
    
    # Initialize collections
    collections = client.list_collections()
    collection_names = [c.name for c in collections]
    
    # Create collections if they don't exist
    if RESUME_COLLECTION not in collection_names:
        resume_collection = client.create_collection(RESUME_COLLECTION)
        print(f"Created {RESUME_COLLECTION} collection")
    else:
        resume_collection = client.get_collection(RESUME_COLLECTION)
        print(f"{RESUME_COLLECTION} collection already exists")
        
    if LOG_COLLECTION not in collection_names:
        log_collection = client.create_collection(LOG_COLLECTION)
        print(f"Created {LOG_COLLECTION} collection")
    else:
        log_collection = client.get_collection(LOG_COLLECTION)
        print(f"{LOG_COLLECTION} collection already exists")
        
    if CANDIDATE_COLLECTION not in collection_names:
        candidate_collection = client.create_collection(CANDIDATE_COLLECTION)
        print(f"Created {CANDIDATE_COLLECTION} collection")
    else:
        candidate_collection = client.get_collection(CANDIDATE_COLLECTION)
        print(f"{CANDIDATE_COLLECTION} collection already exists")
    
    # Check if we already have candidates
    existing_candidates = candidate_collection.get()
    if existing_candidates and 'ids' in existing_candidates and len(existing_candidates['ids']) > 0:
        print(f"Database already contains {len(existing_candidates['ids'])} candidates. Skipping seeding.")
        return
    
    # Sample candidate data for seeding the database
    sample_candidates = [
        {
            "id": str(uuid.uuid4()),
            "name": "John Smith",
            "email": "john.smith@example.com",
            "source": "LinkedIn",
            "stage": "sourced",
            "job_title": "Software Engineer",
            "skills": ["Python", "Django", "SQL", "Git"],
            "experience_years": 5,
            "resume_text": """
            John Smith
            john.smith@example.com
            
            Summary:
            Experienced software engineer with 5 years of experience in web development.
            
            Skills:
            Python, Django, SQL, Git, JavaScript
            
            Experience:
            - Senior Developer at Tech Solutions (2020-Present)
              Led development of customer-facing web applications
              
            - Web Developer at CodeCraft (2018-2020)
              Developed and maintained backend systems
              
            Education:
            - BS in Computer Science, Tech University
            """
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Sarah Johnson",
            "email": "sarah.johnson@example.com",
            "source": "Indeed",
            "stage": "screened",
            "job_title": "Software Engineer",
            "skills": ["Python", "Flask", "MongoDB", "Docker"],
            "matching_skills": ["Python", "MongoDB"],
            "missing_skills": ["Django", "SQL"],
            "match_score": 82,
            "experience_years": 3,
            "resume_text": """
            Sarah Johnson
            sarah.johnson@example.com
            
            Summary:
            Passionate developer with 3 years of experience in backend development.
            
            Skills:
            Python, Flask, MongoDB, Docker, AWS
            
            Experience:
            - Backend Developer at DataSys (2021-Present)
              Designed and implemented RESTful APIs
              
            - Junior Developer at StartupX (2020-2021)
              Full-stack development with Python and JavaScript
              
            Education:
            - MS in Software Engineering, State University
            """
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Michael Chen",
            "email": "michael.chen@example.com",
            "source": "GitHub",
            "stage": "engaged",
            "job_title": "Software Engineer",
            "skills": ["Python", "Django", "React", "AWS"],
            "match_score": 75,
            "experience_years": 4,
            "is_interested": True,
            "resume_text": """
            Michael Chen
            michael.chen@example.com
            
            Summary:
            Full-stack developer with 4 years of experience building web applications.
            
            Skills:
            Python, Django, React, AWS, TypeScript
            
            Experience:
            - Full-Stack Developer at WebApps Inc (2019-Present)
              Developed and deployed scalable web applications
              
            - Frontend Developer at UXDesign (2018-2019)
              Created responsive user interfaces
              
            Education:
            - BS in Computer Engineering, Tech Institute
            """
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Emily Davis",
            "email": "emily.davis@example.com",
            "source": "Internal Database",
            "stage": "scheduled",
            "job_title": "Software Engineer",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
            "match_score": 88,
            "experience_years": 6,
            "is_interested": True,
            "interview_datetime": (datetime.now() + timedelta(days=3)).isoformat(),
            "resume_text": """
            Emily Davis
            emily.davis@example.com
            
            Summary:
            Senior software engineer with 6 years of experience in backend systems.
            
            Skills:
            Python, FastAPI, PostgreSQL, Docker, Kubernetes
            
            Experience:
            - Senior Backend Engineer at DataCloud (2020-Present)
              Architected high-performance APIs and microservices
              
            - Software Engineer at TechGlobal (2017-2020)
              Developed database solutions and web services
              
            Education:
            - MS in Computer Science, Major University
            """
        },
        {
            "id": str(uuid.uuid4()),
            "name": "David Wilson",
            "email": "david.wilson@example.com",
            "source": "Stack Overflow",
            "stage": "sourced",
            "job_title": "Software Engineer",
            "skills": ["Python", "Django", "JavaScript", "Git"],
            "experience_years": 2,
            "resume_text": """
            David Wilson
            david.wilson@example.com
            
            Summary:
            Software developer with 2 years of experience in web applications.
            
            Skills:
            Python, Django, JavaScript, Git, HTML/CSS
            
            Experience:
            - Junior Developer at WebSolutions (2022-Present)
              Developed features for client websites
              
            - Intern at TechStart (2021-2022)
              Assisted in frontend and backend development
              
            Education:
            - BS in Information Technology, City College
            """
        }
    ]
    
    # Add sample candidates to the database
    for candidate in sample_candidates:
        candidate_id = candidate.pop("id")
        resume_text = candidate.pop("resume_text")
        
        # Convert lists to strings for ChromaDB (as it doesn't accept list values)
        for key, value in list(candidate.items()):
            if isinstance(value, list):
                candidate[key] = ", ".join(value)
        
        candidate_collection.add(
            ids=[candidate_id],
            metadatas=[candidate],
            documents=[resume_text]
        )
    
    # Add some sample log entries
    log_entries = [
        {
            "id": str(uuid.uuid4()),
            "agent": "Sourcing Agent",
            "action": "source_candidate",
            "status": "success",
            "details": "Sourced candidate John Smith from LinkedIn",
            "timestamp": (datetime.now() - timedelta(days=2, hours=3)).timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "agent": "Sourcing Agent",
            "action": "source_candidate",
            "status": "success",
            "details": "Sourced candidate Sarah Johnson from Indeed",
            "timestamp": (datetime.now() - timedelta(days=2, hours=2)).timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "agent": "Screening Agent",
            "action": "screen_candidate",
            "status": "success",
            "details": "Screened Sarah Johnson with score 82%",
            "timestamp": (datetime.now() - timedelta(days=1, hours=6)).timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "agent": "Engagement Agent",
            "action": "engage_candidate",
            "status": "success",
            "details": "Engaged Michael Chen who was interested",
            "timestamp": (datetime.now() - timedelta(hours=12)).timestamp()
        },
        {
            "id": str(uuid.uuid4()),
            "agent": "Scheduling Agent",
            "action": "schedule_interview",
            "status": "success",
            "details": f"Scheduled interview for Emily Davis at {(datetime.now() + timedelta(days=3)).isoformat()}",
            "timestamp": (datetime.now() - timedelta(hours=5)).timestamp()
        }
    ]
    
    # Add log entries
    for log in log_entries:
        log_id = log.pop("id")
        log_details = log.pop("details")
        
        log_collection.add(
            ids=[log_id],
            metadatas=[log],
            documents=[log_details]
        )
    
    print(f"Successfully seeded database with {len(sample_candidates)} candidates and {len(log_entries)} log entries")
    return True

if __name__ == "__main__":
    init_database()