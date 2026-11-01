"""Run one local SSSWET research pass against a supplied source."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .documents import load_pdf_documents
from .pipeline import ResearchPipeline
from .persistence import SQLiteResearchStore
from .providers import (
    CorpusDocument,
    CrossrefProvider,
    DeterministicDemoProvider,
    DocumentAnalysisProvider,
    LocalCorpusProvider,
    OpenAICompatibleProvider,
    OpenAlexProvider,
    ArxivProvider,
    MultiSourceLiteratureProvider,
)


def load_corpus(path: str) -> list[CorpusDocument]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Corpus file must contain a JSON array of documents.")
    documents: list[CorpusDocument] = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Each corpus entry must be a JSON object.")
        documents.append(CorpusDocument(
            source_id=str(item["source_id"]),
            title=str(item["title"]),
            text=str(item["text"]),
            url=str(item.get("url", "")),
        ))
    return documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local SSSWET research pass")
    parser.add_argument("--objective", required=True)
    parser.add_argument("--domain", default="general")
    parser.add_argument("--corpus", help="Optional JSON file containing local source documents")
    parser.add_argument("--pdf", action="append", default=[], help="Local PDF to extract and search; may be repeated")
    parser.add_argument("--database", default=".ssswet/ssswet.sqlite3", help="SQLite research history path")
    parser.add_argument("--provider", choices=("demo", "crossref", "openalex", "arxiv", "literature", "llm"), default="demo")
    parser.add_argument("--mailto", default="", help="Optional contact email for Crossref requests")
    parser.add_argument("--model", default=os.getenv("SSSWET_LLM_MODEL", ""))
    parser.add_argument(
        "--endpoint",
        default=os.getenv("SSSWET_LLM_ENDPOINT", "https://api.openai.com/v1/chat/completions"),
    )
    args = parser.parse_args()

    documents = load_corpus(args.corpus) if args.corpus else []
    if args.pdf:
        documents.extend(load_pdf_documents(args.pdf))

    if documents and args.provider == "llm":
        model_provider = OpenAICompatibleProvider(
            api_key=os.getenv("SSSWET_LLM_API_KEY", ""),
            model=args.model,
            endpoint=args.endpoint,
        )
        provider = DocumentAnalysisProvider(model_provider, documents)
    elif documents:
        provider = LocalCorpusProvider(documents)
    elif args.provider == "crossref":
        provider = CrossrefProvider(mailto=args.mailto)
    elif args.provider == "openalex":
        provider = OpenAlexProvider(mailto=args.mailto)
    elif args.provider == "arxiv":
        provider = ArxivProvider()
    elif args.provider == "literature":
        provider = MultiSourceLiteratureProvider(mailto=args.mailto)
    elif args.provider == "llm":
        provider = OpenAICompatibleProvider(
            api_key=os.getenv("SSSWET_LLM_API_KEY", ""),
            model=args.model,
            endpoint=args.endpoint,
        )
    else:
        provider = DeterministicDemoProvider()

    store = SQLiteResearchStore(args.database)
    pipeline = ResearchPipeline(provider=provider, store=store)
    task_id, steps = pipeline.start(args.objective, args.domain)

    print(f"Task: {task_id}")
    print(f"History database: {store.path}")
    print("Classification: research output only; NOT VERIFIED")
    for step in steps:
        print(f"\n[{step.subtask.role}] {step.agent_id} — {step.provider}")
        print(step.result.summary)
        for source_id in step.result.source_ids:
            print(f"Source: {source_id}")
        for evidence in step.result.evidence:
            print(f"Evidence: {evidence}")
        print(f"Uncertainty: {step.result.uncertainty:.2f}")


if __name__ == "__main__":
    main()
