import json
from pathlib import Path

LINKS_PATH = Path("data/links.json")


class StorageError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def load_links() -> dict[str, dict]:
    if not LINKS_PATH.exists():
        return {}

    try:
        with LINKS_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except OSError as exc:
        raise StorageError("Unable to access link storage") from exc
    except json.JSONDecodeError as exc:
        raise StorageError("Link storage is corrupted") from exc

    if not isinstance(data, dict):
        return {}

    return data


def save_links(links: dict[str, dict]) -> None:
    try:
        LINKS_PATH.parent.mkdir(parents=True, exist_ok=True)

        with LINKS_PATH.open("w", encoding="utf-8") as file:
            json.dump(links, file, indent=2)
            file.write("\n")
    except OSError as exc:
        raise StorageError("Unable to access link storage") from exc
