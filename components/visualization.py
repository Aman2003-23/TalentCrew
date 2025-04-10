import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_funnel_chart(stages, values, title="Recruitment Funnel"):
    """Create a recruitment funnel visualization"""
    funnel_data = pd.DataFrame({
        'Stage': stages,
        'Count': values
    })
    
    fig = px.funnel(
        funnel_data, 
        x='Count', 
        y='Stage',
        title=title
    )
    
    return fig

def create_gauge_chart(value, title="Metric", min_val=0, max_val=100):
    """Create a gauge chart for metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val/3], 'color': "red"},
                {'range': [max_val/3, max_val*2/3], 'color': "yellow"},
                {'range': [max_val*2/3, max_val], 'color': "green"}
            ]
        }
    ))
    
    return fig

def create_timeline_chart(events_data):
    """Create a timeline visualization of recruitment events"""
    if not events_data:
        # Create sample data if no events available
        today = pd.Timestamp.now()
        date_range = pd.date_range(end=today, periods=7, freq='D')
        events_data = pd.DataFrame({
            'Date': date_range,
            'Events': np.random.randint(0, 5, size=7)
        })
    
    fig = px.line(
        events_data,
        x='Date',
        y='Events',
        title='Recent Recruitment Activities',
        markers=True
    )
    
    return fig

def create_skills_chart(skills_data):
    """Create a bar chart of most requested/matched skills"""
    if not skills_data or len(skills_data) == 0:
        # Create sample data if no skills available
        skills_data = pd.DataFrame({
            'Skill': ['Python', 'JavaScript', 'SQL', 'React', 'Machine Learning'],
            'Count': [15, 12, 9, 7, 5]
        })
    
    fig = px.bar(
        skills_data,
        y='Skill',
        x='Count',
        title='Most In-Demand Skills',
        orientation='h'
    )
    
    return fig

def create_source_pie_chart(source_data):
    """Create a pie chart showing candidate sources"""
    if not source_data or len(source_data) == 0:
        # Create sample data if no source data available
        source_data = pd.DataFrame({
            'Source': ['LinkedIn', 'Indeed', 'Internal Database', 'GitHub', 'Other'],
            'Count': [45, 25, 15, 10, 5]
        })
    
    fig = px.pie(
        source_data,
        names='Source',
        values='Count',
        title='Candidate Sources'
    )
    
    return fig
