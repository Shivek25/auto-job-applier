# src/ai/llm_client.py
import os
import json
import re
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(
        self,
        provider: str = "gemini",
        model: str = "gemini-3-flash-preview",
        api_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434"
    ):
        self.provider = provider.lower()
        self.model = model or "gemini-3-flash-preview"
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY")
        self.ollama_base_url = ollama_base_url

    def generate_text(self, prompt: str) -> str:
        if self.provider == "gemini":
            return self._call_gemini(prompt)
        elif self.provider == "groq":
            return self._call_groq(prompt)
        elif self.provider == "ollama":
            return self._call_ollama(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        json_prompt = f"{prompt}\n\nIMPORTANT: Respond with pure JSON only, no markdown wrapping, no ```json formatting."
        raw = self.generate_text(json_prompt).strip()
        if "```" in raw:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
            if match:
                raw = match.group(1).strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            first_brace = raw.find("{")
            last_brace = raw.rfind("}")
            if first_brace != -1 and last_brace != -1:
                return json.loads(raw[first_brace:last_brace + 1])
            raise

    def _call_gemini(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        
        target_model = self.model or "gemini-3-flash-preview"
        if "gemini-2.0" in target_model or "gemini-1.5" in target_model:
            target_model = "gemini-3-flash-preview"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        resp = requests.post(url, json=payload, timeout=45)
        
        # If 404, fallback to gemini-3-flash-preview
        if resp.status_code == 404 and target_model != "gemini-3-flash-preview":
            fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={self.api_key}"
            resp = requests.post(fallback_url, json=payload, timeout=45)

        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _call_groq(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set.")
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": self.model or "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _call_ollama(self, prompt: str) -> str:
        url = f"{self.ollama_base_url}/api/generate"
        payload = {"model": self.model or "llama3.2", "prompt": prompt, "stream": False}
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json()["response"]
