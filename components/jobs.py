import streamlit as st
import pandas as pd
from utils import db
import plotly.express as px

def render():
    """
    Render the jobs page showing different job positions and their progress
    """
    st.title("Active Job Positions")
    
    # Get the candidates from the database
    client = st.session_state.chroma_client
    collection = client.get_collection(db.CANDIDATE_COLLECTION)
    
    # Get all candidates
    results = collection.get()
    
    if not results or 'metadatas' not in results or not results['metadatas']:
        st.info("No active job positions found.")
        return
    
    # Create a dataframe from the results
    candidates = []
    
    for i, (candidate_id, metadata, resume_text) in enumerate(
        zip(results['ids'], results['metadatas'], results['documents'])
    ):
        # Convert the metadata to a dict
        candidate = dict(metadata)
        candidate['id'] = candidate_id
        candidates.append(candidate)
    
    # Create a dataframe
    df = pd.DataFrame(candidates)
    
    # Group by job_title and stage
    if 'job_title' in df.columns and 'stage' in df.columns:
        # Get unique job titles
        job_titles = df['job_title'].unique()
        
        # Create a tab for each job title
        tabs = st.tabs(job_titles)
        
        for i, job_title in enumerate(job_titles):
            with tabs[i]:
                st.subheader(f"{job_title}")
                
                # Filter dataframe for this job
                job_df = df[df['job_title'] == job_title]
                
                # Count candidates in each stage
                stage_counts = job_df['stage'].value_counts().to_dict()
                
                # Make sure all stages are represented for consistency
                all_stages = {
                    'sourced': stage_counts.get('sourced', 0),
                    'screened': stage_counts.get('screened', 0),
                    'engaged': stage_counts.get('engaged', 0),
                    'scheduled': stage_counts.get('scheduled', 0)
                }
                
                # Create a dataframe for the funnel chart
                funnel_data = pd.DataFrame({
                    'Stage': ['Sourced', 'Screened', 'Engaged', 'Scheduled'],
                    'Count': list(all_stages.values())
                })
                
                # Create two columns
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Create a funnel chart for this job
                    fig = px.funnel(
                        funnel_data, 
                        x='Count', 
                        y='Stage',
                        title=f'{job_title} Recruitment Funnel'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Show metrics
                    st.metric("Total Candidates", len(job_df))
                    
                    # Calculate fill rate based on candidates that made it to the interview stage
                    fill_rate = (all_stages['scheduled'] / max(1, sum(all_stages.values()))) * 100
                    st.metric("Fill Rate", f"{fill_rate:.1f}%")
                    
                    # Calculate average match score
                    if 'match_score' in job_df.columns and not job_df['match_score'].empty:
                        avg_score = job_df['match_score'].mean()
                        st.metric("Avg Match Score", f"{avg_score:.1f}%")
                
                # Add a section for job details/requirements
                with st.expander("Job Description"):
                    st.write(f"""
                    ## {job_title}
                    
                    ### Required Skills:
                    - Python
                    - Django or Flask
                    - SQL
                    - RESTful API design
                    
                    ### Experience: 
                    3+ years
                    
                    ### Location:
                    Remote
                    
                    ### Salary Range:
                    $100,000 - $130,000
                    """)
                
                # Start Automation Section for this job
                with st.expander("Start Recruitment Automation"):
                    with st.form(f"recruitment_form_{job_title}"):
                        job_description = st.text_area("Job Description", 
                            f"""
                            We are looking for a {job_title} with 3+ years of experience.
                            
                            Required Skills:
                            - Python
                            - Flask or Django
                            - SQL databases
                            - RESTful API design
                            
                            Nice to have:
                            - Machine Learning experience
                            - Cloud services (AWS, GCP, Azure)
                            - Docker and Kubernetes
                            """
                        )
                        
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
    else:
        st.error("The database does not contain the required fields for job tracking")