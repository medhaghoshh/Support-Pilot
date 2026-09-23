import logging
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB (relative to this file's directory)
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_PATH))
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
