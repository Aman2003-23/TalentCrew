import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import db
from agents import sourcing_agent, screening_agent, engagement_agent, scheduling_agent

def render():
    st.title("TalentCrew Dashboard")
    
    # Status indicators for agents
    st.subheader("Agent Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sourcing_status = st.session_state.sourcing_agent.get_status()
        status_color = "🟢" if sourcing_status == "idle" else "🔴" if sourcing_status == "error" else "🟡"
        st.info(f"{status_color} Sourcing Agent: {sourcing_status}")
    
    with col2:
        screening_status = st.session_state.screening_agent.get_status()
        status_color = "🟢" if screening_status == "idle" else "🔴" if screening_status == "error" else "🟡"
        st.info(f"{status_color} Screening Agent: {screening_status}")
    
    with col3:
        engagement_status = st.session_state.engagement_agent.get_status()
        status_color = "🟢" if engagement_status == "idle" else "🔴" if engagement_status == "error" else "🟡"
        st.info(f"{status_color} Engagement Agent: {engagement_status}")
    
    with col4:
        scheduling_status = st.session_state.scheduling_agent.get_status()
        status_color = "🟢" if scheduling_status == "idle" else "🔴" if scheduling_status == "error" else "🟡"
        st.info(f"{status_color} Scheduling Agent: {scheduling_status}")
    
    # Recruitment metrics
    st.subheader("Recruitment Pipeline")
    metrics = db.get_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Candidates Sourced", metrics["total_sourced"])
    
    with col2:
        st.metric("Candidates Screened", metrics["total_screened"])
    
    with col3:
        st.metric("Candidates Engaged", metrics["total_engaged"])
    
    with col4:
        st.metric("Interviews Scheduled", metrics["total_scheduled"])
    
    # Charts
    st.subheader("Analytics")
    col1, col2 = st.columns(2)
    
    with col1:
        # Funnel Chart
        funnel_data = pd.DataFrame({
            'Stage': ['Sourced', 'Screened', 'Engaged', 'Scheduled'],
            'Count': [
                metrics["total_sourced"],
                metrics["total_screened"],
                metrics["total_engaged"],
                metrics["total_scheduled"]
            ]
        })
        
        fig = px.funnel(
            funnel_data, 
            x='Count', 
            y='Stage',
            title='Recruitment Funnel'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Engagement Rate
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=metrics["engagement_rate"],
            title={'text': "Engagement Rate (%)"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "red"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "green"}
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
    
    # Start Automation Section
    st.subheader("Start Recruitment Automation")
    
    with st.form("recruitment_form"):
        job_positions = [
            "Software Engineer",
            "Data Scientist",
            "Product Manager",
            "UX Designer",
            "DevOps Engineer",
            "Marketing Specialist",
            "Sales Representative",
            "HR Manager"
        ]
        
        job_title = st.selectbox("Job Title", job_positions)
        
        # Default job descriptions based on selected position
        job_descriptions = {
            "Software Engineer": """
            We are looking for a Software Engineer with 3+ years of experience in Python development.
            
            Required Skills:
            - Python
            - Flask or Django
            - SQL databases
            - RESTful API design
            
            Nice to have:
            - Machine Learning experience
            - Cloud services (AWS, GCP, Azure)
            - Docker and Kubernetes
            """,
            
            "Data Scientist": """
            We are seeking a Data Scientist with experience in machine learning and data analysis.
            
            Required Skills:
            - Python or R
            - Machine Learning frameworks (TensorFlow, PyTorch, scikit-learn)
            - SQL and NoSQL databases
            - Data visualization
            
            Nice to have:
            - PhD or MS in a quantitative field
            - Industry experience
            - Production ML systems
            """,
            
            "Product Manager": """
            We are looking for a Product Manager to drive our product strategy and roadmap.
            
            Required Skills:
            - 4+ years of product management experience
            - Agile methodologies
            - User research and analytics
            - Cross-functional leadership
            
            Nice to have:
            - Technical background
            - UX design experience
            - Market research expertise
            """,
            
            "UX Designer": """
            We are hiring a UX Designer to create intuitive and engaging user experiences.
            
            Required Skills:
            - 3+ years of UX design experience
            - Wireframing and prototyping
            - User research and testing
            - Figma, Sketch, or Adobe XD
            
            Nice to have:
            - UI design skills
            - Front-end development knowledge
            - Experience with design systems
            """,
            
            "DevOps Engineer": """
            We need a DevOps Engineer to automate and optimize our infrastructure.
            
            Required Skills:
            - 3+ years of DevOps experience
            - Docker and Kubernetes
            - CI/CD pipelines
            - Cloud platforms (AWS, GCP, Azure)
            
            Nice to have:
            - Infrastructure as Code (Terraform, CloudFormation)
            - Security expertise
            - Monitoring and observability
            """,
            
            "Marketing Specialist": """
            We're looking for a Marketing Specialist to drive brand awareness and lead generation.
            
            Required Skills:
            - 2+ years of marketing experience
            - Content creation and management
            - Social media campaigns
            - Analytics and reporting
            
            Nice to have:
            - SEO/SEM expertise
            - Graphic design skills
            - Marketing automation
            """,
            
            "Sales Representative": """
            We are seeking a Sales Representative to grow our customer base and revenue.
            
            Required Skills:
            - 3+ years of sales experience
            - CRM software proficiency
            - Prospecting and lead qualification
            - Negotiation and closing
            
            Nice to have:
            - Industry experience
            - Sales methodology training
            - Enterprise sales experience
            """,
            
            "HR Manager": """
            We need an HR Manager to oversee recruitment and employee relations.
            
            Required Skills:
            - 5+ years of HR experience
            - Employee relations
            - Recruitment and talent acquisition
            - HR policies and compliance
            
            Nice to have:
            - HRIS implementation
            - Training and development
            - Compensation and benefits
            """
        }
        
        default_description = job_descriptions.get(job_title, "Please provide a job description.")
        job_description = st.text_area("Job Description", default_description)
        
        candidate_count = st.slider("Number of Candidates to Source", 3, 15, 5)
        
        submit = st.form_submit_button("Start Automation")
        
        if submit:
            # Check if any agent is already running
            if (st.session_state.sourcing_agent.get_status() == "running" or
                st.session_state.screening_agent.get_status() == "running" or
                st.session_state.engagement_agent.get_status() == "running" or
                st.session_state.scheduling_agent.get_status() == "running"):
                st.error("An agent is already running. Please wait for it to complete.")
            else:
                # Start the workflow
                with st.spinner("Running Sourcing Agent..."):
                    sourcing_result = st.session_state.sourcing_agent.start(
                        job_title, job_description, candidate_count
                    )
                    if sourcing_result["success"]:
                        st.success(sourcing_result["message"])
                    else:
                        st.error(sourcing_result["message"])
                
                with st.spinner("Running Screening Agent..."):
                    screening_result = st.session_state.screening_agent.start(
                        job_title, job_description
                    )
                    if screening_result["success"]:
                        st.success(screening_result["message"])
                    else:
                        st.error(screening_result["message"])
                
                with st.spinner("Running Engagement Agent..."):
                    engagement_result = st.session_state.engagement_agent.start(job_title)
                    if engagement_result["success"]:
                        st.success(engagement_result["message"])
                    else:
                        st.error(engagement_result["message"])
                
                with st.spinner("Running Scheduling Agent..."):
                    scheduling_result = st.session_state.scheduling_agent.start(job_title)
                    if scheduling_result["success"]:
                        st.success(scheduling_result["message"])
                    else:
                        st.error(scheduling_result["message"])
                
                st.success("Automation workflow completed!")
                st.rerun()
