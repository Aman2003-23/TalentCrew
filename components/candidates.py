import streamlit as st
import pandas as pd
from utils import db

def render(view="All Candidates"):
    """
    Render the candidates page with different views based on recruitment stage
    """
    st.title("Candidates")
    
    # Get the candidates from the database
    client = st.session_state.chroma_client
    collection = client.get_collection(db.CANDIDATE_COLLECTION)
    
    # Query the database based on the selected view
    if view == "All Candidates":
        results = collection.get()
    else:
        # Map view names to stages in the database
        stage_map = {
            "Sourced": "sourced",
            "Screened": "screened", 
            "Engaged": "engaged",
            "Scheduled": "scheduled"
        }
        
        # Query based on the stage
        results = collection.get(
            where={"stage": stage_map[view]}
        )
    
    if not results or 'metadatas' not in results or not results['metadatas']:
        st.info(f"No candidates found in {view.lower()} stage.")
        return
    
    # Create a dataframe from the results
    candidates = []
    
    for i, (candidate_id, metadata, resume_text) in enumerate(
        zip(results['ids'], results['metadatas'], results['documents'])
    ):
        # Convert the metadata to a dict (adding the ID)
        candidate = dict(metadata)
        candidate['id'] = candidate_id
        candidates.append(candidate)
    
    # Create a dataframe
    df = pd.DataFrame(candidates)
    
    # Convert columns if needed
    if 'skills' in df.columns:
        # Split the comma-separated skills back into a list for display
        df['skills'] = df['skills'].apply(lambda x: x.split(', ') if isinstance(x, str) else x)
    
    if 'matching_skills' in df.columns:
        # Split the comma-separated matching skills back into a list for display
        df['matching_skills'] = df['matching_skills'].apply(lambda x: x.split(', ') if isinstance(x, str) else x)
    
    if 'missing_skills' in df.columns:
        # Split the comma-separated missing skills back into a list for display
        df['missing_skills'] = df['missing_skills'].apply(lambda x: x.split(', ') if isinstance(x, str) else x)
    
    # Set up tabs for different views
    tab1, tab2 = st.tabs(["List View", "Detailed View"])
    
    with tab1:
        # Decide which columns to show based on stage
        common_columns = ['name', 'email', 'job_title', 'source']
        
        if view == "All Candidates":
            display_columns = common_columns + ['stage']
        elif view == "Sourced":
            display_columns = common_columns + ['skills', 'experience_years']
        elif view == "Screened":
            display_columns = common_columns + ['match_score', 'matching_skills', 'missing_skills']
        elif view == "Engaged":
            display_columns = common_columns + ['match_score', 'is_interested']
        elif view == "Scheduled":
            display_columns = common_columns + ['interview_datetime']
        
        # Filter the dataframe to only show relevant columns
        # Only include columns that exist in the dataframe
        display_columns = [col for col in display_columns if col in df.columns]
        
        # Show the dataframe
        st.dataframe(df[display_columns], use_container_width=True)
    
    with tab2:
        # Detailed view with candidate profiles
        selected_candidate = st.selectbox(
            "Select a candidate to view details",
            options=df['name'].tolist(),
            index=0
        )
        
        # Get the selected candidate
        candidate_row = df[df['name'] == selected_candidate].iloc[0]
        candidate_id = candidate_row['id']
        
        st.subheader(f"{selected_candidate}")
        
        # Layout in columns
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Contact Info**")
            st.write(f"Email: {candidate_row.get('email', 'N/A')}")
            st.write(f"Source: {candidate_row.get('source', 'N/A')}")
            
            st.write("**Job Details**")
            st.write(f"Position: {candidate_row.get('job_title', 'N/A')}")
            st.write(f"Stage: {candidate_row.get('stage', 'N/A').capitalize()}")
            
            # Show stage-specific details
            if candidate_row.get('stage') == 'screened':
                st.write("**Screening Results**")
                st.write(f"Match Score: {candidate_row.get('match_score', 'N/A')}%")
                
                match_skills = candidate_row.get('matching_skills', [])
                if isinstance(match_skills, str):
                    match_skills = match_skills.split(', ')
                st.write(f"Matching Skills: {', '.join(match_skills) if match_skills else 'None'}")
                
                missing = candidate_row.get('missing_skills', [])
                if isinstance(missing, str):
                    missing = missing.split(', ')
                st.write(f"Missing Skills: {', '.join(missing) if missing else 'None'}")
            
            elif candidate_row.get('stage') == 'engaged':
                st.write("**Engagement Results**")
                is_interested = candidate_row.get('is_interested', False)
                if isinstance(is_interested, str):
                    is_interested = is_interested.lower() == 'true'
                
                interest_text = "Interested" if is_interested else "Not Interested"
                interest_color = "green" if is_interested else "red"
                st.markdown(f"<span style='color:{interest_color}'>{interest_text}</span>", unsafe_allow_html=True)
            
            elif candidate_row.get('stage') == 'scheduled':
                st.write("**Interview Schedule**")
                interview_time = candidate_row.get('interview_datetime', 'Not scheduled')
                st.write(f"Interview Time: {interview_time}")
        
        with col2:
            st.write("**Resume**")
            
            # Get the resume text for this candidate
            result = collection.get(ids=[candidate_id])
            if result and 'documents' in result and result['documents']:
                resume_text = result['documents'][0]
                st.text_area("", value=resume_text, height=400, label_visibility="collapsed")
            else:
                st.write("Resume text not available")
        
        # Actions based on current stage
        st.subheader("Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if candidate_row.get('stage') == 'sourced':
                if st.button("Screen Candidate", key=f"screen_{candidate_id}"):
                    # Call the screening logic
                    from agents import screening_agent
                    agent = screening_agent.ScreeningAgent()
                    
                    with st.spinner("Screening candidate..."):
                        # Get job description
                        job_title = candidate_row.get('job_title', '')
                        
                        # In a real app, we would get the job description from somewhere
                        # For this demo, we'll use a generic description
                        job_description = f"""
                        Job Title: {job_title}
                        
                        Required Skills:
                        - Python
                        - Django or Flask
                        - SQL
                        - RESTful API design
                        
                        Experience: 3+ years
                        """
                        
                        # Screen a single candidate
                        result = agent._screen_single_candidate(candidate_id, job_title, job_description)
                        
                        if result['success']:
                            st.success(result['message'])
                        else:
                            st.error(result['message'])
                        
                        # Rerun to update the UI
                        st.rerun()
        
        with col2:
            if candidate_row.get('stage') == 'screened':
                if st.button("Engage Candidate", key=f"engage_{candidate_id}"):
                    # Call the engagement logic
                    from agents import engagement_agent
                    agent = engagement_agent.EngagementAgent()
                    
                    with st.spinner("Engaging candidate..."):
                        job_title = candidate_row.get('job_title', '')
                        
                        # Engage a single candidate
                        result = agent._engage_single_candidate(candidate_id, job_title)
                        
                        if result['success']:
                            st.success(result['message'])
                        else:
                            st.error(result['message'])
                        
                        # Rerun to update the UI
                        st.rerun()
        
        with col3:
            if candidate_row.get('stage') == 'engaged' and candidate_row.get('is_interested'):
                if st.button("Schedule Interview", key=f"schedule_{candidate_id}"):
                    # Call the scheduling logic
                    from agents import scheduling_agent
                    agent = scheduling_agent.SchedulingAgent()
                    
                    with st.spinner("Scheduling interview..."):
                        job_title = candidate_row.get('job_title', '')
                        
                        # Schedule a single candidate
                        result = agent._schedule_single_candidate(candidate_id, job_title)
                        
                        if result['success']:
                            st.success(result['message'])
                        else:
                            st.error(result['message'])
                        
                        # Rerun to update the UI
                        st.rerun()