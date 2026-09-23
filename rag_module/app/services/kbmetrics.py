import json
import time
from vector_search import search_documents

# Team-approved similarity threshold
SIMILARITY_THRESHOLD = 0.45


def calculate_kb_metrics():
    # Load sample queries
    with open("analytics/sample_queries.json", "r") as file:
        queries = json.load(file)

    total_queries = len(queries)
    successful_matches = 0
    failed_matches = 0
    similarity_scores = []
    retrieval_times = []

    print("\n========== Query-wise Retrieval Results ==========\n")

    # Process each query
    for query in queries:

        start_time = time.time()

        result = search_documents(query)

        end_time = time.time()

        retrieval_time = end_time - start_time
        retrieval_times.append(retrieval_time)

        # Check if any document was retrieved
        if result["status"] == "Completed" and len(result["retrieved_docs"]) > 0:

            score = result["retrieved_docs"][0]["similarity_score"]
            similarity_scores.append(score)

            print(f"Query: {query}")
            print(f"Similarity Score: {score}")

            if score >= SIMILARITY_THRESHOLD:
                successful_matches += 1
                print("Status: MATCH\n")
            else:
                failed_matches += 1
                print("Status: NO MATCH\n")

        else:
            failed_matches += 1
            print(f"Query: {query}")
            print("Status: NO DOCUMENT FOUND\n")

    # Calculate metrics
    kb_coverage = (successful_matches / total_queries) * 100

    average_similarity = (
        sum(similarity_scores) / len(similarity_scores)
        if similarity_scores else 0
    )

    average_retrieval_time = (
        sum(retrieval_times) / len(retrieval_times)
        if retrieval_times else 0
    )

    return {
        "total_queries": total_queries,
        "successful_matches": successful_matches,
        "failed_matches": failed_matches,
        "knowledge_base_coverage": round(kb_coverage, 2),
        "average_similarity_score": round(average_similarity, 4),
        "average_retrieval_time": round(average_retrieval_time, 4),
        "similarity_threshold": SIMILARITY_THRESHOLD
    }


if __name__ == "__main__":

    metrics = calculate_kb_metrics()

    print("\n========== Knowledge Base Metrics ==========\n")

    print(f"Similarity Threshold      : {metrics['similarity_threshold']}")
    print(f"Total Queries             : {metrics['total_queries']}")
    print(f"Successful Matches        : {metrics['successful_matches']}")
    print(f"Failed Matches            : {metrics['failed_matches']}")
    print(f"Knowledge Base Coverage   : {metrics['knowledge_base_coverage']} %")
    print(f"Average Similarity Score  : {metrics['average_similarity_score']}")
    print(f"Average Retrieval Time    : {metrics['average_retrieval_time']} seconds")