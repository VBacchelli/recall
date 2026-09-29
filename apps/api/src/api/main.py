import uuid

from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session
from sqlalchemy import select

from api.db import SavedItem, engine
from api.embeddings import BgeEmbeddingProvider
from api.extractors import WebPageExtractor
from api.search import search_items

app = FastAPI(title="Recall API")

web_extractor = WebPageExtractor()
embedding_provider = BgeEmbeddingProvider()


class SaveItemRequest(BaseModel):
    url: HttpUrl

@app.post("/items")
def save_item(request: SaveItemRequest):
    try:
        extracted = web_extractor.extract(str(request.url))
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to extract webpage: {exc}",
        ) from exc

    text_to_embed = f"{extracted.title}\n\n{extracted.content}"
    embedding = embedding_provider.embed_documents([text_to_embed])[0]

    url = str(request.url)

    with Session(engine) as session:
        existing_item = session.scalar(
            select(SavedItem).where(SavedItem.url == url)
        )

        if existing_item is not None:
            existing_item.title = extracted.title
            existing_item.source = extracted.source
            existing_item.content = extracted.content
            existing_item.embedding = embedding

            item = existing_item
        else:
            item = SavedItem(
                id=str(uuid.uuid4()),
                title=extracted.title,
                source=extracted.source,
                url=url,
                content=extracted.content,
                embedding=embedding,
            )
            session.add(item)

        session.commit()

        return {
            "id": item.id,
            "title": item.title,
            "source": item.source,
            "url": item.url,
        }

@app.get("/search")
def search(q: str):
    results = search_items(q, embedding_provider)

    return [
        {
            "id": item.id,
            "title": item.title,
            "source": item.source,
            "url": item.url,
            "distance": distance,
        }
        for item, distance in results
    ]