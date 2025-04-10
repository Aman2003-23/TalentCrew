import streamlit as st
from utils import db
from agents import sourcing_agent
import time

def populate_database():
    """Populate the database with some initial sample data"""
    print("Starting database population...")
    
    # Make sure database is initialized
    db.initialize_db()
    
    # Create a session state for the client
    if not hasattr(st, 'session_state'):
        st.session_state = {}
    
    # Initialize the sourcing agent
    agent = sourcing_agent.SourcingAgent()
    
    # Sample job description
    job_title = "Python Developer"
    job_description = """
    We are looking for a Python Developer with 3+ years of experience in web development.
    
    Required Skills:
    - Python
    - Django or Flask
    - RESTful API design
    - SQL (PostgreSQL preferred)
    - Git
    
    Nice to have:
    - JavaScript/TypeScript
    - Docker
    - AWS or other cloud platforms
    - CI/CD experience
    """
    
    # Run sourcing agent to generate sample candidates
    print("Generating sample candidates...")
    result = agent.start(job_title, job_description, target_count=5)
    
    if result["success"]:
        print(f"Successfully added {result['candidates_count']} candidates to the database")
    else:
        print(f"Error populating database: {result['message']}")
    
    print("Database population complete.")
    return result

if __name__ == "__main__":
    # Run the population script
    populate_database()