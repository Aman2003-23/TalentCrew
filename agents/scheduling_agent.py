import time
import datetime
import streamlit as st
from utils import db
import random

class SchedulingAgent:
    def __init__(self):
        self.name = "Scheduling Agent"
        self.status = "idle"
    
    def start(self, job_title):
        """Start the scheduling process for engaged candidates"""
        self.status = "running"
        db.log_activity(self.name, "start", "success", f"Started scheduling interviews for {job_title}")
        
        scheduled_count = 0
        
        try:
            # Get ChromaDB client
            client = st.session_state.chroma_client
            collection = client.get_collection(db.CANDIDATE_COLLECTION)
            
            # Query for candidates in the "engaged" stage for this job
            results = collection.get(
                where={"stage": "engaged", "job_title": job_title, "is_interested": True}
            )
            
            if not results or 'ids' not in results or not results['ids']:
                self.status = "idle"
                db.log_activity(self.name, "complete", "success", 
                               f"No engaged candidates found to schedule for {job_title}")
                return {
                    "success": True,
                    "message": "No candidates found to schedule",
                    "scheduled_count": 0
                }
            
            # Process each candidate
            for i, (candidate_id, metadata, resume_text) in enumerate(
                zip(results['ids'], results['metadatas'], results['documents'])
            ):
                result = self._schedule_single_candidate(candidate_id, job_title)
                if result["success"]:
                    scheduled_count += 1
            
            self.status = "idle"
            db.log_activity(
                self.name, 
                "complete", 
                "success", 
                f"Completed scheduling with {scheduled_count} interviews arranged"
            )
            
            return {
                "success": True,
                "message": f"Successfully scheduled {scheduled_count} interviews",
                "scheduled_count": scheduled_count
            }
            
        except Exception as e:
            self.status = "error"
            db.log_activity(self.name, "error", "failed", str(e))
            
            return {
                "success": False,
                "message": f"Error during scheduling: {str(e)}",
                "scheduled_count": scheduled_count
            }
    
    def get_status(self):
        """Get the current status of the agent"""
        return self.status
    
    def _schedule_single_candidate(self, candidate_id, job_title):
        """Schedule a single candidate"""
        try:
            # Get ChromaDB client
            client = st.session_state.chroma_client
            collection = client.get_collection(db.CANDIDATE_COLLECTION)
            
            # Get the candidate record
            result = collection.get(ids=[candidate_id])
            
            if not result or 'metadatas' not in result or not result['metadatas']:
                return {
                    "success": False,
                    "message": f"Candidate not found"
                }
            
            metadata = result['metadatas'][0]
            resume_text = result['documents'][0]
            
            # Simulate API delay
            time.sleep(0.5)
            
            # Generate interview slot
            interview_datetime = self._generate_interview_slot()
            
            # Update candidate metadata
            metadata.update({
                "scheduled": True,
                "interview_datetime": interview_datetime.isoformat(),
                "stage": "scheduled"
            })
            
            # Update the record
            collection.update(
                ids=[candidate_id],
                metadatas=[metadata],
                documents=[resume_text]
            )
            
            db.log_activity(
                self.name, 
                "schedule_interview", 
                "success", 
                f"Scheduled interview for {metadata.get('name', 'Candidate')} at {interview_datetime.isoformat()}"
            )
            
            return {
                "success": True,
                "message": f"Successfully scheduled interview at {interview_datetime.isoformat()}"
            }
            
        except Exception as e:
            db.log_activity(self.name, "schedule_interview", "failed", str(e))
            
            return {
                "success": False,
                "message": f"Error during scheduling: {str(e)}"
            }
    
    def _generate_interview_slot(self):
        """
        Generate a future interview slot
        In a real system, this would integrate with calendar APIs
        """
        # Start with current time
        now = datetime.datetime.now()
        
        # Generate a slot 2-7 days in the future
        days_ahead = random.randint(2, 7)
        future_date = now + datetime.timedelta(days=days_ahead)
        
        # Set to business hours (9 AM to 5 PM)
        hour = random.randint(9, 16)  # 9 AM to 4 PM (to end by 5 PM)
        minute = random.choice([0, 15, 30, 45])  # On the quarter hour
        
        interview_datetime = future_date.replace(
            hour=hour, 
            minute=minute, 
            second=0, 
            microsecond=0
        )
        
        return interview_datetime
