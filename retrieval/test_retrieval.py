from retrieval import JobRetriever

retriever = JobRetriever()

# Test basic search
results = retriever.search_jobs("Python developer with AWS experience")

print("\n=== Basic Search Results ===")
for job in results:
    print(f"{job['rank']}. {job['title']} at {job['company']} - Match: {job['similarity']:.2f}")
    print(f"   Skills: {job['skills']}")
    print(f"   Location: {job['location']}, Remote: {job['remote']}")
    print()

# Test with filters
filtered_results = retriever.search_jobs(
    "Data scientist", 
    filters={"location": "New York", "remote": False}
)

print("\n=== Filtered Search Results ===")
for job in filtered_results:
    print(f"{job['rank']}. {job['title']} at {job['company']} - Match: {job['similarity']:.2f}")
    print(f"   Skills: {job['skills']}")
    print(f"   Location: {job['location']}, Remote: {job['remote']}")
    print()

# Test with a complex multi-skill query
complex_query = "I'm looking for a job using Java, Python, AWS, Git, and Spring Boot"
complex_results = retriever.search_jobs(complex_query, n_results=5)

print("\n=== Complex Multi-Skill Query Results ===")
print(f"Query: '{complex_query}'")
print(f"Found {len(complex_results)} matching jobs")

for job in complex_results:
    print(f"\n{job['rank']}. {job['title']} at {job['company']} - Match: {job['similarity']:.2f}")
    print(f"   Skills: {job['skills']}")
    print(f"   Location: {job['location']}, Remote: {job['remote']}")