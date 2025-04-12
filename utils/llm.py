import os
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import HuggingFaceHub
import streamlit as st


def get_llm():
    """
    Initialize the Google Flan T5 Small model from Hugging Face Hub
    """
    try:
        repo_id = "google/flan-t5-small"
        fallback_models = ["facebook/opt-125m", "EleutherAI/pythia-70m"]
        hf_token = os.getenv("HUGGINGFACE_API_KEY", None)

        try:
            if hf_token:
                llm = HuggingFaceHub(repo_id=repo_id,
                                     huggingfacehub_api_token=hf_token,
                                     task="text2text-generation",
                                     model_kwargs={
                                         "temperature": 0.7,
                                         "max_length": 512
                                     })
            else:
                llm = HuggingFaceHub(repo_id=repo_id,
                                     task="text2text-generation",
                                     model_kwargs={
                                         "temperature": 0.7,
                                         "max_length": 512
                                     })
            return llm
        except Exception as primary_error:
            st.error(f"Error with primary model: {str(primary_error)}")

            for fallback in fallback_models:
                try:
                    st.warning(f"Trying fallback model: {fallback}")
                    if hf_token:
                        llm = HuggingFaceHub(repo_id=fallback,
                                             huggingfacehub_api_token=hf_token,
                                             task="text2text-generation",
                                             model_kwargs={
                                                 "temperature": 0.7,
                                                 "max_length": 256
                                             })
                    else:
                        llm = HuggingFaceHub(repo_id=fallback,
                                             task="text2text-generation",
                                             model_kwargs={
                                                 "temperature": 0.7,
                                                 "max_length": 256
                                             })
                    return llm
                except Exception as fallback_error:
                    st.error(
                        f"Failed with fallback model {fallback}: {str(fallback_error)}"
                    )
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

        template = """
        You are TalentCrew, an AI HR assistant for a recruitment team. You help talent acquisition managers 
        to get insights about candidates, hiring processes, and recruitment metrics.

        Current conversation:
        {history}
        Human: {input}
        AI Assistant:
        """

        prompt = PromptTemplate(input_variables=["history", "input"],
                                template=template)

        memory = ConversationBufferMemory(return_messages=True)

        conversation = ConversationChain(llm=llm,
                                         prompt=prompt,
                                         memory=memory,
                                         verbose=True)

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

        prompts = {
            "sourcing":
            """
            You are the Sourcing Agent in TalentCrew, an AI recruitment platform.
            Your role is to find and extract candidate profiles from various sources.

            The human is asking for: {query}

            Provide the list of candidates in one line per candidate format.
            """,
            "screening":
            """
            You are the Screening Agent in TalentCrew, an AI recruitment platform.
            Your role is to assess candidate resumes using NLP and rank candidates based on job fitment.

            The human is asking for: {query}

            Provide the list of top candidates in one line per candidate format.
            """,
            "engagement":
            """
            You are the Engagement Agent in TalentCrew, an AI recruitment platform.
            Your role is to engage candidates through AI-driven conversational messaging.

            The human is asking for: {query}

            Provide engagement insights in a bullet point format.
            """,
            "scheduling":
            """
            You are the Scheduling Agent in TalentCrew, an AI recruitment platform.
            Your role is to automate interview scheduling between recruiters and candidates.

            The human is asking for: {query}

            Respond with scheduling actions or updates in a clear format.
            """
        }

        if agent_name in prompts:
            formatted_prompt = prompts[agent_name].format(query=query)
            raw_response = llm.invoke(formatted_prompt)

            if isinstance(raw_response, str):
                return raw_response
            elif hasattr(raw_response, 'content'):
                return raw_response.content
            elif isinstance(raw_response, list):
                return "\n".join(str(item) for item in raw_response)
            elif isinstance(raw_response, dict):
                return raw_response.get("generated_text", str(raw_response))
            else:
                return str(raw_response)
        else:
            return f"Agent '{agent_name}' not recognized."
    except Exception as e:
        return f"Error getting agent response: {str(e)}"
