from collections import defaultdict


def triage_conflicts(conflicts) -> list[dict]:
    """Group contradiction objects into auditable review queues."""
    groups = defaultdict(list)
    for conflict in conflicts:
        key = (conflict.subject.casefold(), conflict.predicate.casefold())
        groups[key].append(conflict)
    output = []
    for (subject, predicate), items in groups.items():
        values = sorted({value for item in items for value in item.values}, key=str.casefold)
        output.append({
            "subject": subject,
            "predicate": predicate,
            "values": values,
            "conflict_count": len(items),
            "review_priority": min(10, 2 + len(values) + len(items)),
        })
    return sorted(output, key=lambda x: (-x["review_priority"], x["subject"], x["predicate"]))
