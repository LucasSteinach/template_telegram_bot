def truncate(text: str, max_length: int = 64) -> str:
    if len(text) <= max_length:
        return text

    return text[: max_length - 3] + "..."
