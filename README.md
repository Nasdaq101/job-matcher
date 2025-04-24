# LinkedIn Job Matcher - RAG System

A Retrieval-Augmented Generation (RAG) system that provides personalized job recommendations from LinkedIn data based on user queries, skills, and location preferences.

## 🎯 Project Overview

This application helps job seekers find relevant LinkedIn opportunities by:
- Matching users' skills, experience, and location preferences to job postings
- Highlighting factors influencing job relevance (skills match, industry trends, etc.)
- Providing explainable recommendations with proper citations to source data

## 🌟 Key Features

- **Advanced Query Processing**: Handles natural language questions about job opportunities
- **Personalized Recommendations**: Matches jobs based on user skills and location preferences
- **Semantic Search**: Goes beyond keyword matching with embedding-based retrieval
- **Explainable Results**: Highlights why specific jobs match user requirements
- **Citation Support**: References original job listing sources for verification
- **User-Friendly Interface**: Streamlined experience for job exploration

## 🛠️ Technical Architecture

### Data Pipeline
- **Data Source**: LinkedIn Job Postings dataset (2023-2024) from Kaggle
- **Preprocessing**: Cleaning, normalization, and structured extraction of job features
- **Vectorization**: Sentence-BERT embeddings using 'all-MiniLM-L6-v2' model for semantic matching
- **Storage**: Vector database (FAISS) for efficient similarity search
- **Sample Data**: Pre-processed sample data included in the repository

### RAG System Components
- **Retriever**: Embedding-based retrieval with sentence-window approach
- **Context Processing**: Auto-merging of relevant chunks from same job posting
- **Generator**: Google Vertex AI-Gemini for synthesizing job recommendations
- **Citations**: Linking recommendations to original LinkedIn postings

### LLM Integration
- Google Vertex AI-Gemini for response generation
- Advanced context processing for relevant job recommendations
- Natural language explanations of job matches

## 🚀 Deployment

This application will be deployed on Google Cloud Platform (GCP) to meet the project requirements. The deployment strategy may include:

- Containerized application hosting (such as Google Cloud Run)
- Data storage solutions
- Google Vertex AI for LLM integration

*Note: Specific GCP services will be determined during the implementation phase.*

## 💻 Development

```bash
# Clone this repository
git clone https://github.com/CongYidan/linkedin-rag-job-matcher.git
cd linkedin-rag-job-matcher

# create .env file
Create a .env file and add your Google API key to it.
export GOOGLE_API_KEY='your-google-api-key'

# clean up data
bash scripts/clean_up.sh

# start application end to end
bash scripts/setup_and_run.sh 

# stop application
bash scripts/stop_app.sh

```

## 🚀 Usage

1. Access the web interface at `http://localhost:8000`
2. Enter your query (e.g., "Remote NLP job in Boston")
3. Optionally specify additional filters (skills, location)
4. Review personalized job recommendations with explanation of matches

## 📊 Evaluation Metrics

Our system is evaluated using the RAG triad of metrics:
- **Context Relevance**: How well retrieved job descriptions match user profiles
- **Groundedness**: Ensuring recommendations strictly reference LinkedIn data
- **Answer Relevance**: Quality of final job recommendations for user needs

## 👥 Team & Contributions

- **Yidan Cong**
- **Dongjun Xie**
- **Yunfei Zhou**
- **Siyi Gao**

## 📚 References

1. [LinkedIn Job Postings Dataset (2023-2024)](https://www.kaggle.com/datasets/arshkon/linkedin-job-postings) on Kaggle
