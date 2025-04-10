import time
import streamlit as st
from utils import db, llm
import random

class EngagementAgent:
    def __init__(self):
        self.name = "Engagement Agent"
        self.status = "idle"
    
    def start(self, job_title):
        """Start the engagement process for screened candidates"""
        self.status = "running"
        db.log_activity(self.name, "start", "success", f"Started engaging candidates for {job_title}")
        
        engaged_count = 0
        interested_count = 0
        
        try:
            # Get ChromaDB client
            client = st.session_state.chroma_client
            collection = client.get_collection(db.CANDIDATE_COLLECTION)
            
            # Query for candidates in the "screened" stage for this job
            results = collection.get(
                where={"stage": "screened", "job_title": job_title}
            )
            
            if not results or 'ids' not in results or not results['ids']:
                self.status = "idle"
                db.log_activity(self.name, "complete", "success", 
                               f"No screened candidates found to engage for {job_title}")
                return {
                    "success": True,
                    "message": "No candidates found to engage",
                    "engaged_count": 0,
                    "interested_count": 0
                }
            
            # Process each candidate
            for i, (candidate_id, metadata, resume_text) in enumerate(
                zip(results['ids'], results['metadatas'], results['documents'])
            ):
                result = self._engage_single_candidate(candidate_id, job_title)
                if result["success"]:
                    engaged_count += 1
                    if result["interested"]:
                        interested_count += 1
            
            self.status = "idle"
            db.log_activity(
                self.name, 
                "complete", 
                "success", 
                f"Completed engagement with {engaged_count} candidates, {interested_count} interested"
            )
            
            return {
                "success": True,
                "message": f"Successfully engaged {engaged_count} candidates, {interested_count} interested",
                "engaged_count": engaged_count,
                "interested_count": interested_count
            }
            
        except Exception as e:
            self.status = "error"
            db.log_activity(self.name, "error", "failed", str(e))
            
            return {
                "success": False,
                "message": f"Error during engagement: {str(e)}",
                "engaged_count": engaged_count,
                "interested_count": interested_count
            }
    
    def get_status(self):
        """Get the current status of the agent"""
        return self.status
    
    def _generate_engagement_message(self, candidate_name, job_title, matching_skills):
        """Generate an engagement message for a candidate"""
        try:
            # Try to use the LLM for a personalized message
            prompt = f"""
            Write a short, professional email to engage a potential job candidate.
            Candidate name: {candidate_name}
            Job title: {job_title}
            Candidate skills that match the job: {', '.join(matching_skills[:3]) if matching_skills else 'various relevant skills'}
            
            The message should be brief, professional, and highlight that their skills match our requirements.
            Ask if they're interested in discussing the opportunity further.
            """
            
            # Get LLM
            model = llm.get_llm()
            if model:
                response = model(prompt)
                return response
        except:
            pass
        
        # Fallback to template if LLM fails
        skills_mention = f"Your skills in {', '.join(matching_skills[:3])}" if matching_skills else "Your skills"
        
        template = f"""
        Subject: Exciting {job_title} Opportunity
        
        Hi {candidate_name},
        
        I hope this message finds you well. I'm reaching out because your profile caught our attention.
        
        {skills_mention} align well with what we're looking for in our {job_title} position.
        
        Would you be interested in learning more about this opportunity? If so, I'd be happy to provide additional details.
        
        Looking forward to hearing from you.
        
        Best regards,
        TalentCrew AI Recruiting Team
        """
        
        return template
    
    def _engage_single_candidate(self, candidate_id, job_title):
        """Engage a single candidate"""
        try:
            # Get ChromaDB client
            client = st.session_state.chroma_client
            collection = client.get_collection(db.CANDIDATE_COLLECTION)
            
            # Get the candidate record
            result = collection.get(ids=[candidate_id])
            
            if not result or 'metadatas' not in result or not result['metadatas']:
                return {
                    "success": False,
                    "message": f"Candidate not found",
                    "interested": False
                }
            
            metadata = result['metadatas'][0]
            resume_text = result['documents'][0]
            
            # Simulate API delay
            time.sleep(0.5)
            
            # Extract matching skills
            matching_skills = metadata.get("matching_skills", [])
            if isinstance(matching_skills, str):
                matching_skills = matching_skills.split(", ")
            
            # Generate engagement message
            engagement_message = self._generate_engagement_message(
                candidate_name=metadata.get("name", "Candidate"),
                job_title=job_title,
                matching_skills=matching_skills
            )
            
            # Simulate candidate response (in a real system, this would be an actual response)
            is_interested = self._simulate_candidate_interest(metadata.get("match_score", 0))
            
            # Update candidate metadata
            metadata.update({
                "engaged": True,
                "engagement_message": engagement_message,
                "is_interested": is_interested
            })
            
            # Update stage if interested
            if is_interested:
                metadata["stage"] = "engaged"
            
            # Update the record
            collection.update(
                ids=[candidate_id],
                metadatas=[metadata],
                documents=[resume_text]
            )
            
            interest_status = "interested" if is_interested else "not interested"
            db.log_activity(
                self.name, 
                "engage_candidate", 
                "success", 
                f"Engaged {metadata.get('name', 'Candidate')} who was {interest_status}"
            )
            
            return {
                "success": True,
                "message": f"Successfully engaged candidate who was {interest_status}",
                "interested": is_interested
            }
            
        except Exception as e:
            db.log_activity(self.name, "engage_candidate", "failed", str(e))
            
            return {
                "success": False,
                "message": f"Error during engagement: {str(e)}",
                "interested": False
            }
    
    def _simulate_candidate_interest(self, match_score):
        """
        Simulate candidate interest based on match score
        In a real system, this would be based on actual candidate responses
        """
        # Higher match score increases likelihood of interest
        interest_probability = min(90, match_score) / 100
        
        # Add some randomness
        return random.random() < interest_probability
