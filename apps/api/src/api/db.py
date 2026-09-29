from sqlalchemy import String, Text, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import VECTOR


DATABASE_URL = "postgresql+psycopg://recall:recall_dev@localhost:5432/recall"
EMBEDDING_DIMENSIONS = 384


class Base(DeclarativeBase):
    pass


class SavedItem(Base):
    __tablename__ = "saved_items"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        VECTOR(EMBEDDING_DIMENSIONS),
        nullable=True,
    )


engine = create_engine(DATABASE_URL)


def init_db() -> None:
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

    Base.metadata.create_all(engine)