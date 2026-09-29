import json
from pathlib import Path

from sqlalchemy.orm import Session

from api.db import SavedItem, engine, init_db


ITEMS_PATH = Path(__file__).parents[4] / "eval" / "items.json"


def seed_items() -> None:
    init_db()

    with ITEMS_PATH.open(encoding="utf-8") as file:
        items = json.load(file)

    with Session(engine) as session:
        for item_data in items:
            item = SavedItem(
                id=item_data["id"],
                title=item_data["title"],
                source=item_data["source"],
                url=item_data["url"],
                content=item_data["content"],
            )

            session.merge(item)

        session.commit()

    print(f"Seeded {len(items)} items.")


if __name__ == "__main__":
    seed_items()