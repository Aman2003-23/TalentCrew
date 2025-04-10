import os
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import HuggingFaceHub
import streamlit as st

def get_llm():
    """
    Initialize the Google Flan T5 Large model from Hugging Face Hub
    """
    try:
        # Using a smaller, open-access model
        repo_id = "deepseek-ai/DeepSeek-V3-0324"  # This is an open model that doesn't require API key
        
        # Fallback models if the primary one fails
        fallback_models = [
            "openfree/Llama-3_3-Nemotron-Super-49B-v1-Q6_K-GGUF",
           
        ]
        
        # Get HF token from environment
        hf_token = os.getenv("HUGGINGFACE_API_KEY", None)
        
        # Initialize Hugging Face model
        try:
            if hf_token:
                llm = HuggingFaceHub(
                    repo_id=repo_id,
                    huggingfacehub_api_token=hf_token,
                    task="text-generation",
                    model_kwargs={"temperature": 0.7, "max_length": 512}
                )
            else:
                # Without API key, try model without authentication
                llm = HuggingFaceHub(
                    repo_id=repo_id,
                    model_kwargs={"temperature": 0.7, "max_length": 512}
                )
            return llm
        except Exception as primary_error:
            st.error(f"Error with primary model: {str(primary_error)}")
            
            # Try fallback models
            for fallback in fallback_models:
                try:
                    st.warning(f"Trying fallback model: {fallback}")
                    if hf_token:
                        llm = HuggingFaceHub(
                            repo_id=fallback,
                            huggingfacehub_api_token=hf_token,
                            model_kwargs={"temperature": 0.7, "max_length": 256}
                        )
                    else:
                        llm = HuggingFaceHub(
                            repo_id=fallback,
                            model_kwargs={"temperature": 0.7, "max_length": 256}
                        )
                    return llm
                except Exception as fallback_error:
                    st.error(f"Failed with fallback model {fallback}: {str(fallback_error)}")
                    continue
            
            raise Exception("All models failed to initialize")
    except Exception as e:
        st.error(f"Error initializing LLM: {str(e)}")
        return None

def get_conversation_chain():
    """
    Create a conversation chain with the LLM
    """
    try:
        llm = get_llm()
        if not llm:
            return None
            
        # Create a prompt template for HR assistant
        template = """
        You are TalentCrew, an AI HR assistant for a recruitment team. You help talent acquisition managers 
        to get insights about candidates, hiring processes, and recruitment metrics.
        
        Current conversation:
        {history}
        Human: {input}
        AI Assistant:
        """
        
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=template
        )
        
        # Create conversation memory
        memory = ConversationBufferMemory(return_messages=True)
        
        # Create the conversation chain
        conversation = ConversationChain(
            llm=llm,
            prompt=prompt,
            memory=memory,
            verbose=True
        )
        
        return conversation
    except Exception as e:
        st.error(f"Error creating conversation chain: {str(e)}")
        return None

def get_agent_response(agent_name, query):
    """
    Get a response from a specific agent
    """
    try:
        llm = get_llm()
        if not llm:
            return "The AI model is not available at the moment."
            
        # Create a specific prompt for each agent
        prompts = {
            "sourcing": """
            You are the Sourcing Agent in TalentCrew, an AI recruitment platform.
            Your role is to find and extract candidate profiles from various sources.
            
            The human is asking for information about: {query}
            
            Answer as if you are the specialized Sourcing Agent, focusing on how you would approach this task.
            """,
            
            "screening": """
            You are the Screening Agent in TalentCrew, an AI recruitment platform.
            Your role is to assess candidate resumes using NLP and rank candidates based on job fitment.
            
            The human is asking for information about: {query}
            
            Answer as if you are the specialized Screening Agent, focusing on how you would approach this task.
            """,
            
            "engagement": """
            You are the Engagement Agent in TalentCrew, an AI recruitment platform.
            Your role is to engage candidates through AI-driven conversational messaging.
            
            The human is asking for information about: {query}
            
            Answer as if you are the specialized Engagement Agent, focusing on how you would approach this task.
            """,
            
            "scheduling": """
            You are the Scheduling Agent in TalentCrew, an AI recruitment platform.
            Your role is to automate interview scheduling between recruiters and candidates.
            
            The human is asking for information about: {query}
            
            Answer as if you are the specialized Scheduling Agent, focusing on how you would approach this task.
            """
        }
        
        if agent_name in prompts:
            # Format the prompt with the query
            formatted_prompt = prompts[agent_name].format(query=query)
            
            # Generate a response
            response = llm(formatted_prompt)
            return response
        else:
            return f"Agent '{agent_name}' not recognized."
    except Exception as e:
        return f"Error getting agent response: {str(e)}"
