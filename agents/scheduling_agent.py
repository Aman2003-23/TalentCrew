import streamlit as st
from utils import db
import time


class SchedulingAgent:

    def __init__(self):
        self.name = "Scheduling Agent"
        self.status = "idle"

    def start(self, job_title):
        self.status = "running"
        db.log_activity(self.name, "start", "success",
                        f"Started scheduling for job: {job_title}")

        scheduled_count = 0

        try:
            client = st.session_state.chroma_client
            collection = client.get_collection(db.CANDIDATE_COLLECTION)

            # Fix: Correct where clause with operator
            results = collection.get(where={"stage": {"$eq": "engaged"}})

            if not results or 'ids' not in results or not results['ids']:
                self.status = "idle"
                db.log_activity(
                    self.name, "complete", "success",
                    f"No engaged candidates found to schedule for {job_title}")
                return {
                    "success": True,
                    "message": "No candidates to schedule",
                    "scheduled_count": 0
                }

            for i, (candidate_id, metadata, resume_text) in enumerate(
                    zip(results['ids'], results['metadatas'],
                        results['documents'])):

                # Filter manually in code
                if metadata.get("job_title") != job_title or not metadata.get(
                        "is_interested", False):
                    continue

                time.sleep(0.3)
                metadata["stage"] = "interview_scheduled"
                metadata["interview_time"] = f"2025-04-13 10:{i+1:02d} AM"

                collection.update(ids=[candidate_id],
                                  metadatas=[metadata],
                                  documents=[resume_text])
                scheduled_count += 1

            self.status = "idle"
            db.log_activity(
                self.name, "complete", "success",
                f"Scheduled interviews for {scheduled_count} candidates")
            return {
                "success": True,
                "message": f"Scheduled {scheduled_count} candidates",
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
        return self.status
