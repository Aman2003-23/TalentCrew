import streamlit as st
from utils import llm, db
import time

def render():
    st.title("HR Chatbot Assistant")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your HR Assistant. How can I help you with recruitment today?"}
        ]
    
    # Initialize conversation chain
    if "conversation" not in st.session_state:
        st.session_state.conversation = llm.get_conversation_chain()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("Ask me about candidates, hiring status, or agent controls..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Check if the message is a command for a specific agent
            if prompt.lower().startswith(("sourcing", "source")):
                response = llm.get_agent_response("sourcing", prompt)
                
            elif prompt.lower().startswith(("screening", "screen")):
                response = llm.get_agent_response("screening", prompt)
                
            elif prompt.lower().startswith(("engagement", "engage")):
                response = llm.get_agent_response("engagement", prompt)
                
            elif prompt.lower().startswith(("scheduling", "schedule")):
                response = llm.get_agent_response("scheduling", prompt)
                
            elif "metrics" in prompt.lower() or "statistics" in prompt.lower() or "numbers" in prompt.lower():
                # Get metrics from the database
                metrics = db.get_metrics()
                
                response = f"""
                Here are the current recruitment metrics:
                
                - Candidates Sourced: {metrics["total_sourced"]}
                - Candidates Screened: {metrics["total_screened"]}
                - Candidates Engaged: {metrics["total_engaged"]}
                - Interviews Scheduled: {metrics["total_scheduled"]}
                - Engagement Rate: {metrics["engagement_rate"]:.1f}%
                
                Is there anything specific about these metrics you'd like to know?
                """
            
            else:
                # Use the conversation chain for general queries
                if st.session_state.conversation:
                    response = st.session_state.conversation.predict(input=prompt)
                else:
                    response = "I'm sorry, but my language model is not available at the moment. Please try again later."
            
            # Simulate typing
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Log the chat interaction
        db.log_activity(
            "Chatbot",
            "chat_response", 
            "success", 
            f"User asked: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
        )
