from app.data_store import load_links, save_links
from app.schemas.link import StoredLink


class LinkRepository:
    def get_link(self, code: str) -> StoredLink | None:
        raw = load_links().get(code)
        if raw is None:
            return None
        return StoredLink.model_validate(raw)

    def create_link(self, link: StoredLink) -> None:
        links = load_links()
        links[link.code] = link.model_dump(mode="json")
        save_links(links)

    def list_links(self) -> list[StoredLink]:
        return [StoredLink.model_validate(raw) for raw in load_links().values()]

    def link_exists(self, code: str) -> bool:
        return code in load_links()
