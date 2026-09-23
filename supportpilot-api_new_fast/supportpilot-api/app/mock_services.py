# Temporary mock functions — replace with real imports once teammates share their modules

def search_documents(query: str):
    """Mock of Member 3's search_documents()"""
    return {
        "kb_id": "KB-101",
        "title": "VPN Troubleshooting Guide",
        "category": "Network",
        "tags": ["vpn", "connectivity"],
        "content": "Check firewall settings on ports 500 and 4500...",
        "similarity_score": 0.91
    }


def generate_resolution(user_query: str, retrieved_documents: dict):
    """Mock of Member 5's generate_resolution()"""
    return {
        "resolution": "Step 1: Check firewall settings. Step 2: Restart VPN client.",
        "sources": [
            {"title": retrieved_documents["title"], "source": retrieved_documents["kb_id"]}
        ],
        "documents_used": 1,
        "retrieval_confidence": retrieved_documents["similarity_score"],
        "response_time": 1.0
    }