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

    document = results["documents"][0][0]
    metadata = results["metadatas"][0][0]
    distance = results["distances"][0][0]

    # Return structured response
    return {
    "agent_name": "Retrieval Agent",
    "status": "Completed",

    "retrieved_document": {
        "kb_id": metadata["kb_id"],
        "title": metadata["title"],
        "category": metadata["category"],
        "tags": metadata["tags"],
        "content": document,
        "retrieval_distance": round(distance, 4)
    }
}


# Testing
if __name__ == "__main__":

    query = input("Enter your query: ")

    result = search_documents(query)

    print("\n========== Retrieval Agent ==========\n")
    print(f"Agent Name          : {result['agent_name']}")
    print(f"Status              : {result['status']}")
    print(f"KB ID               : {result['kb_id']}")
    print(f"Title               : {result['title']}")
    print(f"Category            : {result['category']}")
    print(f"Tags                : {result['tags']}")
    print(f"Retrieval Distance  : {result['retrieval_distance']}")
    print("\nKnowledge Base Article:\n")
    print(result["content"])