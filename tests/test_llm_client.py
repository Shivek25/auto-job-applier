import pytest
from unittest.mock import MagicMock, patch
from src.ai.llm_client import LLMClient

def test_llm_client_mock_gemini():
    client = LLMClient(provider="gemini", api_key="dummy_key")
    with patch.object(client, "generate_json") as mock_json:
        mock_json.return_value = {"match_score": 85, "reason": "Strong Python experience"}
        res = client.generate_json("Evaluate match", schema={})
        assert res["match_score"] == 85

def test_llm_client_json_cleaning():
    client = LLMClient(provider="gemini", api_key="dummy_key")
    with patch.object(client, "generate_text") as mock_text:
        mock_text.return_value = '```json\n{"score": 90}\n```'
        data = client.generate_json("test")
        assert data["score"] == 90
