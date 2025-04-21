import logging
import os
from google import genai
from typing import List, Dict
import logging
import traceback

# Configure logging to show all information
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True  # This will override any existing configuration
)
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        # Set the API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        # Initialize the client
        self.client = genai.Client(api_key=api_key)
    
    def explain_job_matches(self, query: str, jobs: List[Dict], skills: str = None):
        """
        Generate explanations for why these jobs match the user's query
        
        Args:
            query: The user's original search query
            jobs: List of job matches from the retriever
            skills: Optional comma-separated skills
        
        Returns:
            Dictionary with job IDs as keys and explanations as values
        """
        # Skip if no jobs
        if not jobs:
            return {}
        
        # Create context for Gemini
        user_context = f"Search query: '{query}'"
        if skills:
            user_context += f"\nSkills: {skills}"
        
        job_explanations = {}
        
        # Process each job to get personalized explanation
        for job in jobs:
            # Create a prompt for Gemini to explain the match
            prompt = f"""
            {user_context}

            I'm looking at this job listing:
            - Title: {job['title']}
            - Company: {job['company']}
            - Location: {job['location']}
            - Remote: {'Yes' if job['remote'] else 'No'}
            - Skills: {job['skills']}
            
            Provide a brief, personalized explanation (2-3 sentences) of why this job is a good match for my search query. 
            Focus on how the job requirements align with my query and skills. Be specific about the match quality.
            """
            logging.info(f"Prompt for job {job['job_id']}: {prompt}")

            try:
                # Get response from Gemini
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash-001",
                    contents=prompt,
                )
                # Debug the response object structure
                logger.info(f"Response type: {type(response)}")
                logger.info(f"Response attributes: {dir(response)}")
                
                # Extract the explanation based on the actual response structure
                if hasattr(response, 'text'):
                    explanation = response.text
                elif hasattr(response, 'parts') and response.parts:
                    explanation = response.parts[0].text
                else:
                    # Inspect the response more deeply
                    logger.info(f"Full response: {response}")
                    explanation = "Could not extract explanation from response."
                
                explanation = explanation.strip()
                job_explanations[str(job['job_id'])] = explanation
                
                logger.info(f"Generated explanation for job {job['job_id']}: {explanation}")

            except Exception as e:
                print(f"Error getting explanation for job {job['job_id']}: {e}")
                job_explanations[str(job['job_id'])] = "No explanation available."
        
        return job_explanations