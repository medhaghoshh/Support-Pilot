from services.vector_search import search_documents


def retrieval_agent(user_query):
    """
    Retrieval Agent

    Receives the user query,
    searches the Vector Database,
    and returns the best matching KB article.
    """

    print("\n===== Retrieval Agent Started =====")

    result = search_documents(user_query)

    print("===== Retrieval Agent Completed =====\n")

    return result