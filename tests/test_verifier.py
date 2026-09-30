import pytest
from pathlib import Path
from src.storage.verifier import SubmissionVerifier

def test_verifier_receipt_path(tmp_path):
    verifier = SubmissionVerifier(receipts_dir=tmp_path)
    path = verifier.get_receipt_path("Acme Corp", "li-12345")
    assert "Acme_Corp" in path.name
    assert "li-12345" in path.name
    assert path.suffix == ".png"
    assert path.parent == tmp_path
