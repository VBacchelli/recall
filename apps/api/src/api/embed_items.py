from sqlalchemy import select
from sqlalchemy.orm import Session

from api.db import SavedItem, engine
from api.embeddings import BgeEmbeddingProvider


def embed_items() -> None:
    provider = BgeEmbeddingProvider()

    with Session(engine) as session:
        items = session.scalars(
            select(SavedItem).where(SavedItem.embedding.is_(None))
        ).all()

        if not items:
            print("No items need embeddings.")
            return

        texts = [
            f"{item.title}\n\n{item.content}"
            for item in items
        ]

        embeddings = provider.embed_documents(texts)

        for item, embedding in zip(items, embeddings, strict=True):
            item.embedding = embedding

        session.commit()

    print(f"Embedded {len(items)} items.")


if __name__ == "__main__":
    embed_items()