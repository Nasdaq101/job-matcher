import chromadb

# Connect to the existing database
client = chromadb.PersistentClient(path="./chroma_db")

# Get your collection
collection = client.get_collection("job_listings")

# Check how many items are in the collection
count = collection.count()
print(f"Collection contains {count} documents")

# Try a simple query
results = collection.query(
    query_texts=["software engineer with python experience"],
    n_results=3,
    include=["documents", "metadatas"]
)

# Display the results
for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f"\nResult {i+1}:")
    print(f"Title: {metadata['title_clean']}")
    print(f"Company: {metadata['company_name']}")
    print(f"Skills: {metadata['combined_skills']}")