from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db import SavedItem, engine
from api.embeddings import BgeEmbeddingProvider


def search_items(
    query: str,
    provider: BgeEmbeddingProvider,
    limit: int = 5,
) -> list[tuple[SavedItem, float]]:
    query_embedding = provider.embed_query(query)

    distance = SavedItem.embedding.cosine_distance(query_embedding)

    statement = (
        select(SavedItem, distance.label("distance"))
        .where(SavedItem.embedding.is_not(None))
        .order_by(distance)
        .limit(limit)
    )

    with Session(engine) as session:
        rows = session.execute(statement).all()

    return [(item, distance_value) for item, distance_value in rows]

if __name__ == "__main__":
    query = "running services on a tiny computer"
    provider = BgeEmbeddingProvider()

    results = search_items(query, provider)

    print(f"Query: {query}\n")

    for rank, (item, distance) in enumerate(results, start=1):
        print(f"{rank}. {item.id} — {item.title}")
        print(f"   cosine distance: {distance:.4f}")