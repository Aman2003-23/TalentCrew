import time
import streamlit as st
from utils import db, parser
import random

class SourcingAgent:
    def __init__(self):
        self.name = "Sourcing Agent"
        self.status = "idle"
        self.sources = ["LinkedIn", "Indeed", "Internal Database", "GitHub", "Stack Overflow"]
    
    def start(self, job_title, job_description, target_count=5):
        """Start the sourcing process"""
        self.status = "running"
        db.log_activity(self.name, "start", "success", f"Started sourcing for {job_title}")
        
        # In a real implementation, this would use APIs or web scraping to source candidates
        # For this demo, we'll simulate the process
        
        sourced_count = 0
        
        try:
            for i in range(target_count):
                # Simulate API delay
                time.sleep(0.5)
                
                # Generate a simulated candidate
                candidate = self._simulate_candidate(job_title, job_description)
                
                # Parse the simulated resume
                resume_data = parser.parse_resume(candidate["resume"])
                
                # Add to database
                candidate_id = db.add_candidate(
                    name=resume_data["name"],
                    email=resume_data["email"],
                    source=candidate["source"],
                    resume_text=candidate["resume"],
                    metadata={
                        "stage": "sourced",
                        "job_title": job_title,
                        "skills": resume_data["skills"],
                        "experience_years": resume_data["experience_years"]
                    }
                )
                
                if candidate_id:
                    sourced_count += 1
                    db.log_activity(self.name, "source_candidate", "success", 
                                   f"Sourced candidate {resume_data['name']} from {candidate['source']}")
                else:
                    db.log_activity(self.name, "source_candidate", "failed", 
                                   f"Failed to add candidate to database")
            
            self.status = "idle"
            db.log_activity(self.name, "complete", "success", 
                           f"Completed sourcing with {sourced_count} candidates for {job_title}")
            
            return {
                "success": True,
                "message": f"Successfully sourced {sourced_count} candidates",
                "candidates_count": sourced_count
            }
            
        except Exception as e:
            self.status = "error"
            db.log_activity(self.name, "error", "failed", str(e))
            
            return {
                "success": False,
                "message": f"Error during sourcing: {str(e)}",
                "candidates_count": sourced_count
            }
    
    def get_status(self):
        """Get the current status of the agent"""
        return self.status
    
    def _simulate_candidate(self, job_title, job_description):
        """
        Simulate a candidate for demo purposes
        In a real implementation, this would be replaced with actual API calls
        """
        source = random.choice(self.sources)
        
        # Extract skills mentioned in job description to make the simulation more relevant
        skills = parser.extract_skills(job_description)
        
        # Pick a subset of relevant skills for this candidate
        candidate_skills = random.sample(skills, min(len(skills), random.randint(1, 5)))
        
        # Common first and last names for simulation
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Lisa", "Robert", "Emily"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia"]
        
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"{name.lower().replace(' ', '.')}@example.com"
        
        # Create a simulated resume text
        experience_years = random.randint(1, 10)
        resume = f"""
        {name}
        {email}
        
        Summary:
        Experienced professional with {experience_years} years of experience in {job_title} roles.
        
        Skills:
        {', '.join(candidate_skills)}
        
        Experience:
        - Senior {job_title} at Example Corp (2018-Present)
          Led teams and delivered successful projects
          
        - {job_title} at Sample Inc (2015-2018)
          Developed and implemented solutions
          
        Education:
        - Bachelor's Degree in Computer Science, Example University
        """
        
        return {
            "source": source,
            "resume": resume
        }
