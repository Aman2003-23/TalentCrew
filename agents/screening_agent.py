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
                # Simulate API delay
                time.sleep(0.5)
                
                # Parse the resume
                resume_data = parser.parse_resume(resume_text)
                
                # Match against job description
                match_result = parser.match_job_description(resume_data, job_description)
                
                # Update candidate record with screening results
                metadata.update({
                    "match_score": match_result["match_score"],
                    "matching_skills": match_result["matching_skills"],
                    "missing_skills": match_result["missing_skills"],
                    "experience_match": match_result["experience_match"],
                    "screened": True
                })
                
                # Determine if candidate should be shortlisted
                shortlisted = match_result["match_score"] >= self.threshold_score
                if shortlisted:
                    metadata["stage"] = "screened"
                    shortlisted_count += 1
                
                # Update the record
                collection.update(
                    ids=[candidate_id],
                    metadatas=[metadata],
                    documents=[resume_text]
                )
                
                screened_count += 1
                db.log_activity(
                    self.name, 
                    "screen_candidate", 
                    "success", 
                    f"Screened {resume_data['name']} with score {match_result['match_score']:.1f}%"
                )
            
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
    
    def get_status(self):
        """Get the current status of the agent"""
        return self.status
    
    def set_threshold(self, threshold):
        """Set the matching score threshold for shortlisting"""
        if 0 <= threshold <= 100:
            self.threshold_score = threshold
            return True
        return False
