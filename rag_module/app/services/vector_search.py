from sentence_transformers import SentenceTransformer
import chromadb

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./database/chromadb")
collection = client.get_collection("knowledge_base")


def search_documents(query):
    """
    Retrieves the most relevant knowledge base article
    for the given user query.
    """

    # Generate embedding for the query
    query_embedding = model.encode(query).tolist()

    # Search the Vector Database
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )

    # Check if no document was found
    if not results["documents"] or not results["documents"][0]:
        return {
            "agent_name": "Retrieval Agent",
            "status": "No Match Found",
            "retrieved_docs": []
        }

    # Extract search results
    document = results["documents"][0][0]
    metadata = results["metadatas"][0][0]
    distance = results["distances"][0][0]

    # Convert distance to similarity score (0-1)
    similarity_score = 1 / (1 + distance)

    # Return structured response
    return {
        "agent_name": "Retrieval Agent",
        "status": "Completed",
        "retrieved_docs": [
            {
                "kb_id": metadata["kb_id"],
                "title": metadata["title"],
                "category": metadata["category"],
                "tags": metadata["tags"],
                "content": document,
                "similarity_score": round(similarity_score, 4)
            }
        ]
    }


# ------------------ Testing ------------------

if __name__ == "__main__":

    query = input("Enter your query: ")

    result = search_documents(query)

    print("\n========== Retrieval Agent ==========\n")
    print(f"Agent Name : {result['agent_name']}")
    print(f"Status     : {result['status']}")

    if result["retrieved_docs"]:
        doc = result["retrieved_docs"][0]

        print(f"KB ID            : {doc['kb_id']}")
        print(f"Title            : {doc['title']}")
        print(f"Category         : {doc['category']}")
        print(f"Tags             : {doc['tags']}")
        print(f"Similarity Score : {doc['similarity_score']}")
        print("\nKnowledge Base Article:\n")
        print(doc["content"])
    else:
        print("\nNo matching knowledge base article found.")