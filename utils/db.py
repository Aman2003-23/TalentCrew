import os
import uuid
import time
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fake import FakeEmbeddings
import streamlit as st

# Default collection names
RESUME_COLLECTION = "resume_collection"
LOG_COLLECTION = "log_collection"
CANDIDATE_COLLECTION = "candidate_collection"


def initialize_db():
    try:
        if not os.path.exists("./chroma_db"):
            os.makedirs("./chroma_db")

        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )

        collections = client.list_collections()
        collection_names = [c.name for c in collections]

        if RESUME_COLLECTION not in collection_names:
            client.create_collection(RESUME_COLLECTION)
        if LOG_COLLECTION not in collection_names:
            client.create_collection(LOG_COLLECTION)
        if CANDIDATE_COLLECTION not in collection_names:
            client.create_collection(CANDIDATE_COLLECTION)

        st.session_state.chroma_client = client
        return True
    except Exception as e:
        st.error(f"Failed to initialize database: {str(e)}")
        return False


def get_langchain_db(collection_name=CANDIDATE_COLLECTION):
    try:
        embeddings = FakeEmbeddings(size=768)
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory="./chroma_db"
        )
        return vectorstore
    except Exception as e:
        st.error(f"Failed to initialize LangChain vector store: {str(e)}")
        return None


def log_activity(agent_name, action, status, details=""):
    try:
        client = st.session_state.chroma_client
        collection = client.get_collection(LOG_COLLECTION)

        log_id = str(uuid.uuid4())
        timestamp = time.time()

        collection.add(
            ids=[log_id],
            metadatas=[{
                "agent": agent_name,
                "action": action,
                "status": status,
                "details": details,
                "timestamp": timestamp
            }],
            documents=[f"{agent_name} {action}: {status} - {details}"]
        )
        return True
    except Exception as e:
        print(f"Error logging activity: {str(e)}")
        return False


def get_metrics():
    try:
        client = st.session_state.chroma_client
        candidates_collection = client.get_collection(CANDIDATE_COLLECTION)
        logs_collection = client.get_collection(LOG_COLLECTION)

        candidates = candidates_collection.get()
        logs = logs_collection.get()

        total_sourced = 0
        total_screened = 0
        total_engaged = 0
        total_scheduled = 0

        if candidates and 'metadatas' in candidates and candidates['metadatas']:
            for metadata in candidates['metadatas']:
                stage = metadata.get('stage', '')
                if stage == 'sourced':
                    total_sourced += 1
                elif stage == 'screened':
                    total_screened += 1
                elif stage == 'engaged':
                    total_engaged += 1
                elif stage == 'scheduled':
                    total_scheduled += 1

        if total_sourced == 0:
            total_sourced = 1

        engagement_rate = (total_engaged / total_sourced) * 100

        return {
            "total_sourced": total_sourced,
            "total_screened": total_screened,
            "total_engaged": total_engaged,
            "total_scheduled": total_scheduled,
            "engagement_rate": engagement_rate
        }

    except Exception as e:
        st.error(f"Error getting metrics: {str(e)}")
        return {
            "total_sourced": 0,
            "total_screened": 0,
            "total_engaged": 0,
            "total_scheduled": 0,
            "engagement_rate": 0
        }


def add_candidate(name, email, source, resume_text, metadata=None):
    try:
        client = st.session_state.chroma_client
        collection = client.get_collection(CANDIDATE_COLLECTION)
        candidate_id = str(uuid.uuid4())

        if metadata is None:
            metadata = {}

        if 'stage' not in metadata:
            metadata['stage'] = 'sourced'

        metadata.update({
            "name": name,
            "email": email,
            "source": source
        })

        collection.add(
            ids=[candidate_id],
            metadatas=[metadata],
            documents=[resume_text]
        )

        log_activity("system", "add_candidate", "success", f"Added candidate {name}")
        return candidate_id
    except Exception as e:
        log_activity("system", "add_candidate", "failed", str(e))
        return None


def update_candidate_stage(candidate_id, new_stage):
    try:
        client = st.session_state.chroma_client
        collection = client.get_collection(CANDIDATE_COLLECTION)

        result = collection.get(ids=[candidate_id])
        if not result or not result['metadatas']:
            return False

        metadata = result['metadatas'][0]
        metadata['stage'] = new_stage

        collection.update(
            ids=[candidate_id],
            metadatas=[metadata],
            documents=[result['documents'][0]]
        )

        log_activity("system", "update_candidate", "success", f"Updated {metadata.get('name')} to {new_stage}")
        return True
    except Exception as e:
        log_activity("system", "update_candidate", "failed", str(e))
        return False


def get_candidates():
    """Return a list of all candidate metadata"""
    try:
        client = st.session_state.chroma_client
        collection = client.get_collection(CANDIDATE_COLLECTION)
        result = collection.get()
        return result.get("metadatas", [])
    except Exception as e:
        st.error(f"Error getting candidates: {str(e)}")
        return []


def get_hiring_status():
    """Return a summary of current hiring stages"""
    metrics = get_metrics()
    return f"""Current hiring status:
- Candidates Sourced: {metrics["total_sourced"]}
- Candidates Screened: {metrics["total_screened"]}
- Candidates Engaged: {metrics["total_engaged"]}
- Interviews Scheduled: {metrics["total_scheduled"]}
- Engagement Rate: {metrics["engagement_rate"]:.2f}%"""


def get_candidates_per_role():
    """Count number of candidates per job role (from metadata)"""
    try:
        client = st.session_state.chroma_client
        collection = client.get_collection(CANDIDATE_COLLECTION)
        result = collection.get()
        role_counts = {}

        for metadata in result.get("metadatas", []):
            role = metadata.get("role", "Unknown")
            role_counts[role] = role_counts.get(role, 0) + 1

        return role_counts
    except Exception as e:
        st.error(f"Error counting candidates per role: {str(e)}")
        return {}
