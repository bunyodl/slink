from app.schemas.link import LinkApiModel, StoredLink

def to_api_model(link: StoredLink) -> LinkApiModel:
    return LinkApiModel(code=link.code, url=link.url)
