import time
import streamlit as st
from utils import db


class ScreeningAgent:

    def __init__(self):
        self.name = "Screening Agent"
        self.status = "idle"

    def start(self, job_title, min_match_score=60):
        """Start the screening process for candidates"""
        self.status = "running"
        db.log_activity(self.name, "start", "success",
                        f"Started screening candidates for {job_title}")

        screened_count = 0

        try:
            # Get ChromaDB client
            client = st.session_state.chroma_client
            collection = client.get_collection(db.CANDIDATE_COLLECTION)

            # Retrieve candidates who are in the 'new' stage and match the job title
            results = collection.get(where={"stage": "new"})

            if not results or 'ids' not in results or not results['ids']:
                self.status = "idle"
                db.log_activity(
                    self.name, "complete", "success",
                    f"No new candidates found to screen for {job_title}")
                return {
                    "success": True,
                    "message": "No candidates found to screen",
                    "screened_count": 0
                }

            for i, (candidate_id, metadata, resume_text) in enumerate(
                    zip(results['ids'], results['metadatas'],
                        results['documents'])):

                if metadata.get("job_title") != job_title:
                    continue

                match_score = metadata.get("match_score", 0)
                if isinstance(match_score, str):
                    try:
                        match_score = float(match_score)
                    except ValueError:
                        match_score = 0

                if match_score >= min_match_score:
                    metadata["stage"] = "screened"
                    collection.update(ids=[candidate_id],
                                      metadatas=[metadata],
                                      documents=[resume_text])
                    screened_count += 1
                time.sleep(0.2)

            self.status = "idle"
            db.log_activity(
                self.name, "complete", "success",
                f"Screened {screened_count} candidates for {job_title}")

            return {
                "success": True,
                "message": f"Screened {screened_count} candidates",
                "screened_count": screened_count
            }

        except Exception as e:
            self.status = "error"
            db.log_activity(self.name, "error", "failed", str(e))
            return {
                "success": False,
                "message": f"Error during screening: {str(e)}",
                "screened_count": screened_count
            }

    def get_status(self):
        """Get the current status of the agent"""
        return self.status
