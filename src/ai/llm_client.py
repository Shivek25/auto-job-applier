# src/ai/llm_client.py
import os
import json
import re
import time
import logging
from typing import Dict, Any, Optional
import requests

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(
        self,
        provider: str = "gemini",
        model: str = "gemini-3.5-flash-lite",
        api_key: Optional[str] = None,
        ollama_base_url: str = "http://localhost:11434"
    ):
        self.provider = provider.lower()
        self.model = model or "gemini-3.5-flash-lite"
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
        
        target_model = self.model or "gemini-3.5-flash-lite"
        # Route models to 3.5-flash-lite / 3.1-flash-lite which provide 500 RPD vs 20 RPD on standard flash
        if any(m in target_model for m in ["gemini-3-flash", "gemini-2.0", "gemini-1.5", "gemini-2.5"]):
            target_model = "gemini-3.5-flash-lite"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        last_resp = None
        for attempt in range(2):
            resp = requests.post(url, json=payload, timeout=30)
            last_resp = resp
            
            # If 404 or 429 on 3.5-flash-lite, fallback to 3.1-flash-lite
            if resp.status_code in [404, 429] and target_model != "gemini-3.1-flash-lite":
                target_model = "gemini-3.1-flash-lite"
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{target_model}:generateContent?key={self.api_key}"
                resp = requests.post(url, json=payload, timeout=30)
                last_resp = resp
            
            if resp.status_code == 429:
                wait_time = (attempt + 1) * 2
                logger.warning(f"Gemini API rate limit (429) hit. Pausing {wait_time}s before retry (attempt {attempt + 1}/2)...")
                time.sleep(wait_time)
                continue

            resp.raise_for_status()
            data = resp.json()
            time.sleep(0.5) # Polite pause to stay within free tier RPM limits
            return data["candidates"][0]["content"]["parts"][0]["text"]

        if last_resp is not None:
            last_resp.raise_for_status()
        raise RuntimeError("Failed to generate content from Gemini API after retries.")

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
