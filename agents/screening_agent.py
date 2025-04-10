import time
import streamlit as st
from utils import db, parser
import random

class ScreeningAgent:
    def __init__(self):
        self.name = "Screening Agent"
        self.status = "idle"
        self.threshold_score = 60  # Minimum match score to pass screening
    
    def start(self, job_title, job_description):
        """Start the screening process for sourced candidates"""
        self.status = "running"
        db.log_activity(self.name, "start", "success", f"Started screening for {job_title}")
        
        screened_count = 0
        shortlisted_count = 0
        
        try:
            # Get ChromaDB client
            client = st.session_state.chroma_client
            collection = client.get_collection(db.CANDIDATE_COLLECTION)
            
            # Query for candidates in the "sourced" stage for this job
            results = collection.get(
                where={"stage": "sourced", "job_title": job_title}
            )
            
            if not results or 'ids' not in results or not results['ids']:
                self.status = "idle"
                db.log_activity(self.name, "complete", "success", 
                               f"No candidates found to screen for {job_title}")
                return {
                    "success": True,
                    "message": "No candidates found to screen",
                    "screened_count": 0,
                    "shortlisted_count": 0
                }
            
            # Process each candidate
            for i, (candidate_id, metadata, resume_text) in enumerate(
                zip(results['ids'], results['metadatas'], results['documents'])
            ):
                result = self._screen_single_candidate(candidate_id, job_title, job_description)
                if result["success"]:
                    screened_count += 1
                    if result["shortlisted"]:
                        shortlisted_count += 1
            
            self.status = "idle"
            db.log_activity(
                self.name, 
                "complete", 
                "success", 
                f"Completed screening with {screened_count} candidates, {shortlisted_count} shortlisted"
            )
            
            return {
                "success": True,
                "message": f"Successfully screened {screened_count} candidates, {shortlisted_count} shortlisted",
                "screened_count": screened_count,
                "shortlisted_count": shortlisted_count
            }
            
        except Exception as e:
            self.status = "error"
            db.log_activity(self.name, "error", "failed", str(e))
            
            return {
                "success": False,
                "message": f"Error during screening: {str(e)}",
                "screened_count": screened_count,
                "shortlisted_count": shortlisted_count
            }
    
    def _screen_single_candidate(self, candidate_id, job_title, job_description):
        """Screen a single candidate"""
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
                    "shortlisted": False
                }
            
            metadata = result['metadatas'][0]
            resume_text = result['documents'][0]
            
            # Simulate API delay
            time.sleep(0.5)
            
            # Parse the resume
            resume_data = parser.parse_resume(resume_text)
            
            # Match against job description
            match_result = parser.match_job_description(resume_data, job_description)
            
            # Make sure matching_skills and missing_skills are converted to strings
            matching_skills = match_result.get("matching_skills", [])
            if isinstance(matching_skills, list):
                matching_skills = ", ".join(matching_skills)
                
            missing_skills = match_result.get("missing_skills", [])
            if isinstance(missing_skills, list):
                missing_skills = ", ".join(missing_skills)
            
            # Handle the experience_match which might be a boolean
            experience_match = match_result.get("experience_match", False)
            if isinstance(experience_match, bool):
                experience_match = "Yes" if experience_match else "No"
            
            # Update candidate record with screening results
            metadata.update({
                "match_score": match_result.get("match_score", 0),
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "experience_match": experience_match,
                "screened": True
            })
            
            # Determine if candidate should be shortlisted
            match_score = match_result.get("match_score", 0)
            shortlisted = match_score >= self.threshold_score
            if shortlisted:
                metadata["stage"] = "screened"
            
            # Update the record
            collection.update(
                ids=[candidate_id],
                metadatas=[metadata],
                documents=[resume_text]
            )
            
            db.log_activity(
                self.name, 
                "screen_candidate", 
                "success", 
                f"Screened {resume_data['name']} with score {match_score:.1f}%"
            )
            
            return {
                "success": True,
                "message": f"Successfully screened candidate with score {match_score:.1f}%",
                "shortlisted": shortlisted
            }
            
        except Exception as e:
            db.log_activity(self.name, "screen_candidate", "failed", str(e))
            
            return {
                "success": False,
                "message": f"Error during screening: {str(e)}",
                "shortlisted": False
            }
    
    def get_status(self):
        """Get the current status of the agent"""
        return self.status
    
    def set_threshold(self, threshold):
        """Set the matching score threshold for shortlisting"""
        if 0 <= threshold <= 100:
            self.threshold_score = threshold
            return True
        return False
