"""
Semantic search over the Knowledge Base vector store (ChromaDB).
Given a query, returns the top-k most relevant KB chunks with metadata
and a relevance score.
"""

import chromadb

CHROMA_PATH = "./chroma_db"


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name="knowledge_base")


def search_knowledge_base(query: str, top_k: int = 3):
    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=top_k)

    articles = []
    if not results["ids"] or not results["ids"][0]:
        return articles

    for i in range(len(results["ids"][0])):
        distance = results["distances"][0][i]
        # 1/(1+distance) maps any non-negative distance to a clean (0,1] score,
        # regardless of the underlying distance metric's scale
        relevance = round(1 / (1 + distance), 2)
        meta = results["metadatas"][0][i]
        articles.append({
            "kb_id": meta["kb_id"],
            "title": meta["title"],
            "category": meta["category"],
            "tags": meta["tags"].split(", "),
            "last_updated": meta["last_updated"],
            "source": meta["source"],
            "section": meta["section"],
            "content": results["documents"][0][i],
            "relevance_score": relevance,
            "priority": meta.get("priority", ""),
            "version": meta.get("version", ""),
            "author": meta.get("author", ""),
        })
    return articles


if __name__ == "__main__":
    test_queries = [
        "my vpn keeps disconnecting",
        "I forgot my password and I'm locked out",
        "outlook is not receiving emails",
        "my laptop keeps shutting down and getting hot",
    ]
    for q in test_queries:
        print(f"\nQuery: {q}")
        for a in search_knowledge_base(q, top_k=2):
            print(f"  [{a['relevance_score']}] {a['kb_id']} - {a['title']}")
