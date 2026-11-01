import sys
from types import SimpleNamespace

import pytest

from ssswet_core.documents import (
    MAX_PAGE_CHARACTERS,
    load_pdf_documents,
)


class FakePage:
    def __init__(self, text):
        self.text = text

    def extract_text(self):
        return self.text


class FakeReader:
    pages = [FakePage("  First page\\nwith methods.  "), FakePage("Second page results.")]
    metadata = SimpleNamespace(title="A Research Paper")
    is_encrypted = False

    def __init__(self, path, strict=True):
        self.path = path
        self.strict = strict


def install_fake_pypdf(monkeypatch, reader=FakeReader):
    monkeypatch.setitem(sys.modules, "pypdf", SimpleNamespace(PdfReader=reader))


def test_pdf_extraction_preserves_page_ids_and_normalizes_text(tmp_path, monkeypatch):
    install_fake_pypdf(monkeypatch)
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-fake")

    documents = load_pdf_documents([pdf])

    assert len(documents) == 2
    assert documents[0].source_id == "pdf:paper.pdf:p0001"
    assert documents[0].title == "A Research Paper — page 1"
    assert documents[0].text == "First page with methods."
    assert documents[1].source_id.endswith(":p0002")
    assert "#page=2" in documents[1].url


def test_pdf_extraction_skips_empty_pages(tmp_path, monkeypatch):
    class EmptyReader(FakeReader):
        pages = [FakePage("  "), FakePage("Text on page two")]

    install_fake_pypdf(monkeypatch, EmptyReader)
    pdf = tmp_path / "paper.pdf"
    pdf.write_bytes(b"%PDF-fake")

    documents = load_pdf_documents([pdf])

    assert len(documents) == 1
    assert documents[0].source_id.endswith(":p0002")


def test_pdf_extraction_rejects_non_pdf_and_missing_file(tmp_path, monkeypatch):
    install_fake_pypdf(monkeypatch)
    not_pdf = tmp_path / "notes.txt"
    not_pdf.write_text("not a PDF")

    with pytest.raises(ValueError, match="Not a PDF"):
        load_pdf_documents([not_pdf])
    with pytest.raises(FileNotFoundError):
        load_pdf_documents([tmp_path / "missing.pdf"])


def test_pdf_extraction_rejects_encrypted_files(tmp_path, monkeypatch):
    class EncryptedReader(FakeReader):
        is_encrypted = True

    install_fake_pypdf(monkeypatch, EncryptedReader)
    pdf = tmp_path / "locked.pdf"
    pdf.write_bytes(b"%PDF-fake")

    with pytest.raises(ValueError, match="Encrypted"):
        load_pdf_documents([pdf])


def test_pdf_page_text_is_bounded(tmp_path, monkeypatch):
    class LongReader(FakeReader):
        pages = [FakePage("x" * (MAX_PAGE_CHARACTERS + 100))]

    install_fake_pypdf(monkeypatch, LongReader)
    pdf = tmp_path / "long.pdf"
    pdf.write_bytes(b"%PDF-fake")

    documents = load_pdf_documents([pdf])

    assert len(documents[0].text) == MAX_PAGE_CHARACTERS


def test_pdf_support_error_explains_optional_install(monkeypatch, tmp_path):
    monkeypatch.delitem(sys.modules, "pypdf", raising=False)
    monkeypatch.setattr("builtins.__import__", __import__)
    # Simulate an environment without the optional package.
    import builtins
    original_import = builtins.__import__

    def no_pypdf(name, *args, **kwargs):
        if name == "pypdf":
            raise ImportError("not installed")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", no_pypdf)
    with pytest.raises(RuntimeError, match="ssswet-core\\[pdf\\]"):
        load_pdf_documents([tmp_path / "paper.pdf"])
