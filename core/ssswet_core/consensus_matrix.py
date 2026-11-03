"""Deterministic agreement matrix for normalized categorical claims."""
from __future__ import annotations


def build(claims: list[dict]) -> dict:
    subjects = sorted({str(c["subject"]).casefold() for c in claims})
    values = {subject: sorted({str(c["value"]).casefold() for c in claims if str(c["subject"]).casefold() == subject}) for subject in subjects}
    agreement = {subject: {value: sum(1 for c in claims if str(c["subject"]).casefold() == subject and str(c["value"]).casefold() == value) for value in vals} for subject, vals in values.items()}
    return {"subjects": subjects, "counts": agreement}
