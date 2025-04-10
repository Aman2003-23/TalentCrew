import streamlit as st
from components import dashboard, chatbot
from utils import db

# Set up page configuration
st.set_page_config(
    page_title="TalentCrew - AI Recruitment Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing application state
if 'db_initialized' not in st.session_state:
    st.session_state.db_initialized = False

# Initialize database
if not st.session_state.db_initialized:
    db.initialize_db()
    st.session_state.db_initialized = True

# Sidebar
st.sidebar.title("TalentCrew")
st.sidebar.image("https://freesvg.org/img/1538298822.png", width=100)  # Using a free SVG of robot/AI
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "HR Chatbot"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("## About")
st.sidebar.info(
    "TalentCrew is an AI-powered recruitment automation platform "
    "that helps talent acquisition teams streamline their hiring processes."
)

# Main content
if page == "Dashboard":
    dashboard.render()
else:
    chatbot.render()
