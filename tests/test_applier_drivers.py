import pytest
from unittest.mock import MagicMock, AsyncMock
from src.applier.linkedin import LinkedInApplier
from src.applier.indeed import IndeedApplier

def test_applier_drivers_init():
    mock_bm = MagicMock()
    mock_filler = MagicMock()
    mock_verifier = MagicMock()
    mock_db = MagicMock()

    li = LinkedInApplier(mock_bm, mock_filler, mock_verifier, mock_db, mode="auto")
    assert li.mode == "auto"

    ind = IndeedApplier(mock_bm, mock_filler, mock_verifier, mock_db, mode="review")
    assert ind.mode == "review"
