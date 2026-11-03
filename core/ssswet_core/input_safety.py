import re

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_public_text(value: str, *, max_length: int = 12000) -> str:
    if not isinstance(value, str):
        raise TypeError("public text must be a string")
    if max_length <= 0:
        raise ValueError("max_length must be positive")
    cleaned = _CONTROL.sub(" ", value).strip()
    if len(cleaned) > max_length:
        raise ValueError("public text exceeds configured length")
    return cleaned


def validate_identifier(value: str, *, max_length: int = 128) -> str:
    cleaned = sanitize_public_text(value, max_length=max_length)
    if not re.fullmatch(r"[A-Za-z0-9_.:-]+", cleaned):
        raise ValueError("identifier contains unsupported characters")
    return cleaned
