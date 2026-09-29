import uuid

from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from api.db import SavedItem, engine
from api.embeddings import BgeEmbeddingProvider
from api.extractors import WebPageExtractor


app = FastAPI(title="Recall API")

web_extractor = WebPageExtractor()
embedding_provider = BgeEmbeddingProvider()


class SaveItemRequest(BaseModel):
    url: HttpUrl


@app.post("/items")
def save_item(request: SaveItemRequest):
    extracted = web_extractor.extract(str(request.url))

    text_to_embed = f"{extracted.title}\n\n{extracted.content}"
    embedding = embedding_provider.embed_documents([text_to_embed])[0]

    item = SavedItem(
        id=str(uuid.uuid4()),
        title=extracted.title,
        source=extracted.source,
        url=extracted.url,
        content=extracted.content,
        embedding=embedding,
    )

    with Session(engine) as session:
        session.add(item)
        session.commit()

        return {
            "id": item.id,
            "title": item.title,
            "source": item.source,
            "url": item.url,
        }