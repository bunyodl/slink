from app.data_store import load_links, save_links
from app.schemas.link import StoredLink
from app.services.url_normalize import url_hash as compute_url_hash


class LinkRepository:
    def get_link(self, code: str) -> StoredLink | None:
        raw = load_links().get(code)
        if raw is None:
            return None
        return StoredLink.model_validate(raw)

    def find_by_url_hash(self, target_hash: str) -> StoredLink | None:
        for raw in load_links().values():
            link = StoredLink.model_validate(raw)
            effective_hash = raw.get("url_hash") or compute_url_hash(link.url)
            if effective_hash == target_hash:
                return link
        return None

    def create_link(self, link: StoredLink) -> None:
        links = load_links()
        links[link.code] = link.model_dump(mode="json")
        save_links(links)

    def list_links(self) -> list[StoredLink]:
        return [StoredLink.model_validate(raw) for raw in load_links().values()]

    def link_exists(self, code: str) -> bool:
        return code in load_links()
