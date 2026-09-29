from api.db import init_db


def main() -> None:
    init_db()
    print("Recall database initialized.")