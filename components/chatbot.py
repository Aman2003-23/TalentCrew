import streamlit as st
from utils import llm, db
import time


def render():
    st.title("HR Chatbot Assistant")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role":
            "assistant",
            "content":
            "Hello! I'm your HR Assistant. How can I help you with recruitment today?"
        }]

    # Initialize conversation chain
    if "conversation" not in st.session_state:
        st.session_state.conversation = llm.get_conversation_chain()

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Handle user input
    if prompt := st.chat_input(
            "Ask me about candidates, hiring status, or agent controls..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            lower_prompt = prompt.lower()

            # Handle known commands
            if any(keyword in lower_prompt
                   for keyword in ["statistics", "metrics", "numbers"]):
                metrics = db.get_metrics()
                response = f"""
                Here are the current recruitment metrics:

                - Candidates Sourced: {metrics["total_sourced"]}
                - Candidates Screened: {metrics["total_screened"]}
                - Candidates Engaged: {metrics["total_engaged"]}
                - Interviews Scheduled: {metrics["total_scheduled"]}
                - Engagement Rate: {metrics["engagement_rate"]:.1f}%
                """

            elif "hiring status" in lower_prompt or "job status" in lower_prompt:
                response = db.get_hiring_status()

            elif "agent controls" in lower_prompt or "controls" in lower_prompt:
                response = "Available agent controls: sourcing, screening, engagement, and scheduling. You can say things like 'sourcing update' or 'schedule interviews'."

            elif "candidates" in lower_prompt and "role" in lower_prompt:
                roles_data = db.get_candidates_per_role()
                role_summary = "\n".join([
                    f"- {role}: {count} candidate(s)"
                    for role, count in roles_data.items()
                ])
                response = f"Here are the number of candidates per open role:\n\n{role_summary}"

            elif "candidates" in lower_prompt:
                   
                    candidates = db.get_candidates()
                    if not candidates:
                        response = "There are currently no candidates in the pipeline."
                    else:
                        candidate_list = []
                        for idx, c in enumerate(candidates, start=1):
                            item = (
                                f"{idx}. {c.get('name', 'N/A')} - {c.get('role', 'N/A')} - "
                                f"{c.get('stage', 'N/A')} - {c.get('status', 'N/A')} - "
                                f"Engagement: {c.get('engagement_score', 'N/A')} - "
                                f"Next: {c.get('next_step', 'N/A')}"
                            )
                            candidate_list.append(item)
                        response = "Here are the candidates in the pipeline:\n\n" + "\n".join(candidate_list)


            elif prompt.lower().startswith(("sourcing", "source")):
                response = llm.get_agent_response("sourcing", prompt)

            elif prompt.lower().startswith(("screening", "screen")):
                response = llm.get_agent_response("screening", prompt)

            elif prompt.lower().startswith(("engagement", "engage")):
                response = llm.get_agent_response("engagement", prompt)

            elif prompt.lower().startswith(("scheduling", "schedule")):
                response = llm.get_agent_response("scheduling", prompt)

            else:
                # Handle unknown/random queries
                response = "Sorry, I don’t have information about that."

            # Simulate typing effect
            for chunk in response.split():
                full_response += chunk + " "
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.03)

            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response
        })

        # Log the chat interaction
        db.log_activity(
            "Chatbot", "chat_response", "success",
            f"User asked: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
