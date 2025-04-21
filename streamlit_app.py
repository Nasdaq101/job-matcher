# streamlit_app.py (Streamlit frontend)
import streamlit as st
import requests
import json
import os

# Default for local development
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Set up the Streamlit page
st.set_page_config(page_title="LinkedIn Job Matcher", layout="wide")

# Header
st.title("LinkedIn Job Matcher")
st.markdown("Find the perfect job match based on your skills and preferences")

# Create a sidebar for search inputs
with st.sidebar:
    st.header("Search Criteria")
    
    # Job query
    query = st.text_input(
        "What kind of job are you looking for?",
        placeholder="E.g., Python developer, Marketing Specialist"
    )
    
    # Skills
    skills = st.text_input(
        "Required Skills (comma separated)",
        placeholder="E.g., python, aws, react"
    )
    
    # Location
    location = st.text_input(
        "Preferred Location",
        placeholder="E.g., New York, San Francisco"
    )
    
    # Remote option
    remote = st.checkbox("Remote positions only")
    
    # Number of results
    num_results = st.slider("Number of results", min_value=1, max_value=20, value=5)
    
    # Search button
    search_button = st.button("Search Jobs")

# Main content area
if search_button and query:
    st.header("Search Results")
    
    # Display search criteria
    st.write(f"**Query:** {query}")
    if skills:
        st.write(f"**Skills:** {skills}")
    if location:
        st.write(f"**Location:** {location}")
    if remote:
        st.write("**Remote only:** Yes")
    
    # Prepare request data
    data = {
        "query": query,
        "location": location if location else None,
        "remote": remote,
        "skills": skills if skills else None,
        "num_results": num_results
    }
    
    # Call the API
    with st.spinner("Searching for matching jobs..."):
        try:
            response = requests.post(f"{API_URL}/search", json=data)
            if response.status_code == 200:
                results = response.json()
                
                # Show results
                if results:
                    for job in results:
                        with st.expander(f"{job['title']} at {job['company']} - {job['similarity']:.0%} match"):
                            st.write(f"**Company:** {job['company']}")
                            st.write(f"**Location:** {job['location']}")
                            if job['remote']:
                                st.write("**Remote:** Yes")
                            st.write(f"**Skills:** {job['skills']}")
                            # Add Gemini's explanation in a highlighted box
                            if "explanation" in job and job["explanation"]:
                                st.info(f"**Why this matches your search:** {job['explanation']}")
                            st.write(f"**Job Description:** {job['document']}")
                            st.markdown(f"[View on LinkedIn](https://www.linkedin.com/jobs/view/{job['job_id']})")
                else:
                    st.warning("No matching jobs found. Try broadening your search criteria.")
            else:
                st.error(f"Error: API returned status code {response.status_code}")
                st.write(response.text)
        except requests.exceptions.ConnectionError:
            st.error(f"Could not connect to API at {API_URL}. Is the server running?")
else:
    st.info("Enter your search criteria and click 'Search Jobs' to find matching positions.")