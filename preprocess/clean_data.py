import pandas as pd
from .utils import extract_skills_efficient, clean_text, is_software_job, normalize_skills, clean_combined_skills
from normalizers import normalize_location, normalize_title

# Read the original data
df = pd.read_csv('data/raw_data/postings.csv', quoting=1)

# Keep only necessary columns
columns_to_keep = ['job_id', 'company_name', 'title', 'description', 'location', 'remote_allowed', 'job_posting_url', 'skills_desc']
df = df[columns_to_keep]

# Filter out records with missing company names
print(f"Original record count: {len(df)}")
df = df.dropna(subset=['company_name', 'title', 'description'])
print(f"Record count after filtering: {len(df)}")

# Optional: Filter for software engineering jobs only
# Uncomment the following lines if you want to focus on software engineering jobs
# df['is_software'] = df.apply(lambda row: is_software_job(row['title'], row['description']), axis=1)
# df = df[df['is_software'] == True]
# print(f"Software engineering jobs count: {len(df)}")

# Handle missing values for other fields
df['location'] = df['location'].fillna('Not Specified')
# Normalize locations
print("Normalizing location data...")
df['location_normalized'] = df['location'].apply(normalize_location)
df['remote_allowed'] = df['remote_allowed'].apply(
    lambda x: bool(x) if not pd.isna(x) else False
)
df['job_posting_url'] = df['job_posting_url'].fillna('')

# Clean title
df['title_clean'] = df['title'].apply(clean_text)
df['title_normalized'] = df['title_clean'].apply(normalize_title)

# Extract skills from descriptions
print("Extracting skills from job descriptions...")
df['extracted_skills'] = extract_skills_efficient(df['description'])

# Combine skills from original data and extraction
df['skills_desc'] = df['skills_desc'].fillna("").apply(normalize_skills)

df['combined_skills'] = df.apply(
    lambda row: 
        (row['skills_desc'] + ", " if row['skills_desc'] else "") + 
        (", ".join(row['extracted_skills']) if row['extracted_skills'] else ""),
    axis=1
)

# Clean up combined skills
df['combined_skills'] = df['combined_skills'].apply(clean_combined_skills)

# Drop rows with no skills information
empty_skills = df['combined_skills'] == ""
print(f"Dropping {empty_skills.sum()} rows with no skills information")
df = df[~empty_skills]
print(f"Final record count: {len(df)}")

df['description_clean'] = df['description'].apply(clean_text)

# Create a combined text field for generating embeddings
df['combined_text'] = (
    "Title: " + df['title_clean'] + 
    ", Location: " + df['location'] +
    ", Skills: " + df['combined_skills']
)

# Select only the columns you need for your RAG system
columns_to_keep_final = [
    'job_id', 
    'company_name', 
    'title_clean',  # Clean version of the title
    'title_normalized', 
    'location',
    'location_normalized', 
    'job_posting_url',
    'remote_allowed',
    'combined_skills', 
    'combined_text'  # The text used for embeddings
]

# Create a sample with only necessary columns
df_sample = df[columns_to_keep_final]

# Display a few examples
print("\nSample records:")
for i, row in df_sample.head(3).iterrows():
    print("\n---")
    print(f"Title: {row['title_clean']}")
    print(f"Company: {row['company_name']}")
    print(f"Location: {row['location']}")
    print(f"Skills: {row['combined_skills']}")
    print(f"Combined text: {row['combined_text'][:100]}...")  # Show first 100 chars

# Save the sample dataset
df_sample.to_csv('data/jobs_sample.csv', index=False)

print(f"Saved {len(df_sample)} records to the sample dataset")