from abc import ABC, abstractmethod

from sentence_transformers import SentenceTransformer


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        pass

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        pass


class BgeEmbeddingProvider(EmbeddingProvider):
    MODEL_NAME = "BAAI/bge-small-en-v1.5"
    DIMENSIONS = 384

    def __init__(self) -> None:
        self.model = SentenceTransformer(self.MODEL_NAME)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )
        return embedding.tolist()