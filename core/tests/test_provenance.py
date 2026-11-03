from ssswet_core.provenance import ProvenanceRecord, content_digest, provenance_digest, verify_chain


def test_provenance_chain_detects_break():
    first = ProvenanceRecord("s1", "paper", "ref1", content_digest("a"))
    second = ProvenanceRecord("s2", "dataset", "ref2", content_digest("b"), provenance_digest(first))
    assert verify_chain([first, second])["valid"]
    broken = ProvenanceRecord("s3", "note", "ref3", content_digest("c"), "wrong")
    assert not verify_chain([first, second, broken])["valid"]
