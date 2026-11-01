"""Bounded extraction of text from local PDF research documents."""
from __future__ import annotations

from pathlib import Path

from .providers import CorpusDocument


MAX_PDF_BYTES = 50 * 1024 * 1024
MAX_PDF_PAGES = 500
MAX_PAGE_CHARACTERS = 12_000


def load_pdf_documents(paths: list[str | Path]) -> list[CorpusDocument]:
    """Extract page-level text from local PDFs using the optional pypdf extra.

    Files are never uploaded. Each page is a separate corpus document so
    citations can point to a stable local page identifier.
    """
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF support requires the optional dependency. Install with: "
            "python -m pip install 'ssswet-core[pdf]'"
        ) from exc

    documents: list[CorpusDocument] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"PDF file not found: {path}")
        if path.stat().st_size > MAX_PDF_BYTES:
            raise ValueError(f"PDF exceeds the {MAX_PDF_BYTES // (1024 * 1024)} MiB size limit: {path.name}")
        if path.suffix.casefold() != ".pdf":
            raise ValueError(f"Not a PDF file: {path.name}")

        try:
            reader = PdfReader(str(path), strict=True)
            if reader.is_encrypted:
                raise ValueError(f"Encrypted PDF is not supported: {path.name}")
            if len(reader.pages) > MAX_PDF_PAGES:
                raise ValueError(
                    f"PDF exceeds the {MAX_PDF_PAGES}-page extraction limit: {path.name}"
                )
            metadata = reader.metadata
            title = str(getattr(metadata, "title", None) or path.stem).strip() or path.stem
            for page_number, page in enumerate(reader.pages, start=1):
                extracted = page.extract_text() or ""
                normalized = " ".join(extracted.split())[:MAX_PAGE_CHARACTERS]
                if not normalized:
                    continue
                documents.append(CorpusDocument(
                    source_id=f"pdf:{path.name}:p{page_number:04d}",
                    title=f"{title} — page {page_number}",
                    text=normalized,
                    url=f"file://{path.resolve()}#page={page_number}",
                ))
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(
                f"Could not safely extract PDF {path.name}: {type(exc).__name__}"
            ) from exc

    return documents
