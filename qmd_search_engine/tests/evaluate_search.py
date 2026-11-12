
# ==========================================
# QMD SEARCH ENGINE - PRECISION & RECALL
# ==========================================
from tests.evaluation_dataset import evaluation_queries
from app.core.database import get_connection

from app.search.keyword_search import KeywordSearch
from app.search.semantic_search import SemanticSearch
from app.search.hybrid_search import HybridSearch

from tests.evaluation_dataset import evaluation_queries


# Number of results to evaluate
TOP_K = 5


# ------------------------------------------
# Calculate Precision, Recall and F1
# ------------------------------------------

def calculate_metrics(retrieved_chunks, relevant_chunks):

    retrieved_set = set(retrieved_chunks)
    relevant_set = set(relevant_chunks)

    true_positives = len(retrieved_set & relevant_set)

    false_positives = len(retrieved_set - relevant_set)

    false_negatives = len(relevant_set - retrieved_set)

    precision = (
        true_positives / TOP_K
        if TOP_K > 0 else 0
    )

    recall = (
        true_positives / len(relevant_set)
        if relevant_set else 0
    )

    f1_score = (
        2 * precision * recall / (precision + recall)
        if precision + recall > 0 else 0
    )

    return {
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives
    }


# ------------------------------------------
# Main evaluation
# ------------------------------------------

def evaluate_search():

    connection = get_connection()

    try:

        # Initialize search engines
        keyword_engine = KeywordSearch(connection)

        semantic_engine = SemanticSearch(connection)

        hybrid_engine = HybridSearch(connection)


        search_engines = {
            "Keyword": keyword_engine,
            "Semantic": semantic_engine,
            "Hybrid": hybrid_engine
        }


        # Store metrics for average calculation
        overall_metrics = {
            mode: {
                "precision": [],
                "recall": [],
                "f1_score": []
            }
            for mode in search_engines
        }


        print("\n" + "=" * 75)
        print("QMD SEARCH ENGINE - SEARCH EVALUATION")
        print("=" * 75)


        for test_case in evaluation_queries:

            query = test_case["query"]

            collection = test_case["collection"]

            relevant_chunks = test_case["relevant_chunks"]


            print("\n" + "-" * 75)
            print("QUERY:", query)
            print("COLLECTION:", collection)
            print("EXPECTED RELEVANT CHUNKS:", len(relevant_chunks))
            print("-" * 75)


            for mode, engine in search_engines.items():

                results = engine.search(
                    query=query,
                    top_k=TOP_K,
                    collection=collection
                )


                retrieved_chunks = [
                    result["chunk_id"]
                    for result in results
                ]


                metrics = calculate_metrics(
                    retrieved_chunks,
                    relevant_chunks
                )


                overall_metrics[mode]["precision"].append(
                    metrics["precision"]
                )

                overall_metrics[mode]["recall"].append(
                    metrics["recall"]
                )

                overall_metrics[mode]["f1_score"].append(
                    metrics["f1_score"]
                )


                print(f"\n{mode.upper()} SEARCH")

                print("Retrieved chunks:", retrieved_chunks)

                print(
                    f"Precision@{TOP_K}: "
                    f"{metrics['precision']:.4f}"
                )

                print(
                    f"Recall@{TOP_K}: "
                    f"{metrics['recall']:.4f}"
                )

                print(
                    f"F1-score: "
                    f"{metrics['f1_score']:.4f}"
                )

                print(
                    "TP:", metrics["true_positives"],
                    "| FP:", metrics["false_positives"],
                    "| FN:", metrics["false_negatives"]
                )


        # ----------------------------------
        # Calculate macro averages
        # ----------------------------------

        print("\n" + "=" * 75)
        print("FINAL SEARCH ENGINE COMPARISON")
        print("=" * 75)

        for mode, values in overall_metrics.items():

            avg_precision = (
                sum(values["precision"]) /
                len(values["precision"])
            )

            avg_recall = (
                sum(values["recall"]) /
                len(values["recall"])
            )

            avg_f1 = (
                sum(values["f1_score"]) /
                len(values["f1_score"])
            )


            print(f"\n{mode.upper()} SEARCH")

            print(f"Average Precision: {avg_precision:.4f}")

            print(f"Average Recall:    {avg_recall:.4f}")

            print(f"Average F1-score:  {avg_f1:.4f}")


        print("\nEvaluation completed successfully.")


    finally:

        connection.close()


# ------------------------------------------
# Execute evaluation
# ------------------------------------------

if __name__ == "__main__":

    evaluate_search()
