import json
from pathlib import Path

from api.embeddings import BgeEmbeddingProvider
from api.search import search_items


QUERIES_PATH = Path(__file__).parents[4] / "eval" / "queries.json"


def evaluate(k: int = 5) -> None:
    with QUERIES_PATH.open(encoding="utf-8") as file:
        queries = json.load(file)

    provider = BgeEmbeddingProvider()

    recalls = []
    reciprocal_ranks = []

    for query_data in queries:
        query = query_data["query"]
        expected_ids = set(query_data.get("expected_item_ids", []))
        expected_urls = set(query_data.get("expected_urls", []))

        results = search_items(
            query,
            provider=provider,
            limit=k,
        )

        result_ids = [item.id for item, _ in results]
        result_urls = [item.url for item, _ in results]

        relevant_ranks = [
            rank
            for rank, (item_id, item_url) in enumerate(
                zip(result_ids, result_urls),
                start=1,
            )
            if item_id in expected_ids or item_url in expected_urls
        ]

        recall = 1.0 if relevant_ranks else 0.0
        reciprocal_rank = (
            1.0 / relevant_ranks[0]
            if relevant_ranks
            else 0.0
        )

        recalls.append(recall)
        reciprocal_ranks.append(reciprocal_rank)

        print(f"\nQuery: {query}")
        print(
            f"Expected IDs: {sorted(expected_ids)} | "
            f"Expected URLs: {sorted(expected_urls)}"
        )
        print(f"Top {k}: {result_ids}")

        if relevant_ranks:
            print(f"Relevant rank: {relevant_ranks[0]}")
        else:
            print("Relevant rank: not found")

    recall_at_k = sum(recalls) / len(recalls)
    mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

    print("\n=== Evaluation ===")
    print(f"Queries: {len(queries)}")
    print(f"Recall@{k}: {recall_at_k:.3f}")
    print(f"MRR: {mrr:.3f}")


if __name__ == "__main__":
    evaluate(k=5)