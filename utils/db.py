import os
import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import streamlit as st

# Default collection names
RESUME_COLLECTION = "resume_collection"
LOG_COLLECTION = "log_collection"
CANDIDATE_COLLECTION = "candidate_collection"

def initialize_db():
    """Initialize ChromaDB for storing vectors and metadata"""
    try:
        # Create a client with persistence
        if not os.path.exists("./chroma_db"):
            os.makedirs("./chroma_db")
            
        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # Initialize collections if they don't exist
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
    """Get a LangChain vector store for the specified collection"""
    try:
        # Use HuggingFace embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Create/get vector store
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
    """Log agent activity to ChromaDB"""
    try:
        client = st.session_state.chroma_client
        collection = client.get_collection(LOG_COLLECTION)
        
        # Generate a unique ID for the log entry
        import uuid
        import time
        
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
    """Get recruitment metrics from the database"""
    try:
        client = st.session_state.chroma_client
        
        # Get metrics from collections
        candidates_collection = client.get_collection(CANDIDATE_COLLECTION)
        logs_collection = client.get_collection(LOG_COLLECTION)
        
        # Get all candidates and logs
        candidates = candidates_collection.get()
        logs = logs_collection.get()
        
        # Count candidates in different stages from metadata
        total_sourced = 0
        total_screened = 0
        total_engaged = 0
        total_scheduled = 0
        
        if candidates and 'metadatas' in candidates and candidates['metadatas']:
            # Count candidates by stage
            for metadata in candidates['metadatas']:
                if metadata.get('stage') == 'sourced':
                    total_sourced += 1
                elif metadata.get('stage') == 'screened':
                    total_screened += 1
                elif metadata.get('stage') == 'engaged':
                    total_engaged += 1
                elif metadata.get('stage') == 'scheduled':
                    total_scheduled += 1
        
        # If no data, return some placeholder numbers for now
        if total_sourced == 0:
            total_sourced = 1  # Set to 1 to avoid divide by zero errors
        
        engagement_rate = (total_engaged / total_sourced) * 100 if total_sourced > 0 else 0
        
        metrics = {
            "total_sourced": total_sourced,
            "total_screened": total_screened,
            "total_engaged": total_engaged,
            "total_scheduled": total_scheduled,
            "engagement_rate": engagement_rate
        }
        
        return metrics
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
    """Add a candidate to the database"""
    try:
        client = st.session_state.chroma_client
        collection = client.get_collection(CANDIDATE_COLLECTION)
        
        import uuid
        candidate_id = str(uuid.uuid4())
        
        if metadata is None:
            metadata = {}
        
        # Add default stage if not provided
        if 'stage' not in metadata:
            metadata['stage'] = 'sourced'
        
        # Add basic candidate info to metadata
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
        
        log_activity("system", "add_candidate", "success", f"Added candidate {name} from {source}")
        return candidate_id
    except Exception as e:
        log_activity("system", "add_candidate", "failed", str(e))
        return None

def update_candidate_stage(candidate_id, new_stage):
    """Update a candidate's stage in the recruitment process"""
    try:
        client = st.session_state.chroma_client
        collection = client.get_collection(CANDIDATE_COLLECTION)
        
        # Get current candidate data
        result = collection.get(ids=[candidate_id])
        
        if not result or not result['metadatas']:
            return False
        
        # Update the stage in metadata
        metadata = result['metadatas'][0]
        metadata['stage'] = new_stage
        
        # Update the record
        collection.update(
            ids=[candidate_id],
            metadatas=[metadata],
            documents=[result['documents'][0]]
        )
        
        log_activity("system", "update_candidate", "success", 
                   f"Updated candidate {metadata.get('name', 'Unknown')} to stage {new_stage}")
        return True
    except Exception as e:
        log_activity("system", "update_candidate", "failed", str(e))
        return False
