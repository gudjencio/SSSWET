from dataclasses import dataclass


@dataclass(frozen=True)
class RetentionPolicy:
    max_items: int = 10000
    keep_latest_per_key: bool = True


def compact_records(records: list[dict], *, key_field: str = "key", policy: RetentionPolicy = RetentionPolicy()) -> list[dict]:
    if policy.max_items <= 0:
        raise ValueError("max_items must be positive")
    selected = records
    if policy.keep_latest_per_key:
        latest = {}
        for record in records:
            key = record.get(key_field)
            latest.pop(key, None)
            latest[key] = record
        selected = list(latest.values())
    return selected[-policy.max_items:]
