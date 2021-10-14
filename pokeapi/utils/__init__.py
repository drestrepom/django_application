def extract_id_from_uri(url: str, position: int = -1) -> str:
    return url.split("/")[position - 1]
