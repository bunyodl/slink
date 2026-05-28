import json
from pathlib import Path

LINKS_PATH = Path("data/links.json")


def load_links() -> dict[str, dict]:
    if not LINKS_PATH.exists():
        return {}

    with LINKS_PATH.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {}

    return data


def save_links(links: dict[str, dict]) -> None:
    LINKS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LINKS_PATH.open("w", encoding="utf-8") as file:
        json.dump(links, file, indent=2)
        file.write("\n")
