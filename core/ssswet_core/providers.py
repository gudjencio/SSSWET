from dataclasses import dataclass
import re
from typing import Protocol


@dataclass(frozen=True)
class ProviderResult:
    summary: str
    evidence: tuple[str, ...] = ()
    uncertainty: float = 1.0
    source_ids: tuple[str, ...] = ()


class ResearchProvider(Protocol):
    name: str

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        ...


@dataclass(frozen=True)
class CorpusDocument:
    source_id: str
    title: str
    text: str
    url: str = ""

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.title.strip() or not self.text.strip():
            raise ValueError("Corpus documents require a source ID, title and text.")


class LocalCorpusProvider:
    """Search a caller-supplied document corpus without inventing findings."""

    name = "local-document-corpus"

    def __init__(self, documents: list[CorpusDocument] | None = None, max_results: int = 5):
        self.documents = list(documents or [])
        self.max_results = max(1, max_results)

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token for token in re.findall(r"[\w-]{2,}", text.casefold())
            if token not in {"the", "and", "for", "with", "that", "this", "les", "des", "une", "pour", "dans"}
        }

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        query_tokens = self._tokens(objective)
        if not query_tokens:
            return ProviderResult("No searchable terms were found in the research objective.")

        ranked: list[tuple[float, CorpusDocument]] = []
        for document in self.documents:
            document_tokens = self._tokens(document.title + " " + document.text)
            overlap = query_tokens & document_tokens
            if not overlap:
                continue
            score = len(overlap) / max(1, len(query_tokens))
            ranked.append((score, document))

        ranked.sort(key=lambda item: (-item[0], item[1].source_id))
        selected = ranked[:self.max_results]
        if not selected:
            return ProviderResult(
                "No matching documents were found in the supplied local corpus.",
                uncertainty=1.0,
            )

        evidence = tuple(
            f"[{doc.source_id}] {doc.title}: " +
            re.sub(r"\s+", " ", doc.text).strip()[:500]
            for _, doc in selected
        )
        source_ids = tuple(doc.source_id for _, doc in selected)
        return ProviderResult(
            summary=f"Found {len(selected)} potentially relevant document(s) in the supplied corpus. Relevance is lexical, not scientific validation.",
            evidence=evidence,
            uncertainty=1.0,
            source_ids=source_ids,
        )


class DeterministicDemoProvider:
    """Safe local provider used until real research/model providers are configured."""

    name = "deterministic-demo"

    def investigate(self, objective: str, strategy: str) -> ProviderResult:
        return ProviderResult(
            summary=f"Demo research pass for: {objective}",
            evidence=(f"Strategy recorded: {strategy}",),
            uncertainty=1.0,
        )
