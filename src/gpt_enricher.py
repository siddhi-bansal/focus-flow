"""
GPT Enricher scaffold for FocusPulse.

Features:
- Local JSON cache at data/gpt_cache.json to avoid duplicate calls
- Optional real API calls when OPENAI_API_KEY is available and `openai` package is installed
- Deterministic simulated response when no API key is present (for safe local testing)
- Robust JSON parsing of model output with validation and fallback to local rules

Usage:
    from src.gpt_enricher import GPTEnricher
    enricher = GPTEnricher()
    result = enricher.classify("Chrome — YouTube")

"""
from __future__ import annotations

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any


class GPTEnricher:
    """A small wrapper to call an LLM for classification with local caching.

    It intentionally keeps network usage optional and provides a safe simulated
    response when no API key is available.
    """

    DEFAULT_CACHE = Path(__file__).parent.parent / "data" / "gpt_cache.json"

    def __init__(self, cache_path: Optional[str] = None, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.cache_path = Path(cache_path) if cache_path else self.DEFAULT_CACHE
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model
        self._load_cache()

    def _load_cache(self) -> None:
        if not self.cache_path.exists():
            self._cache: Dict[str, Any] = {}
            return
        try:
            with open(self.cache_path, 'r', encoding='utf-8') as fh:
                self._cache = json.load(fh)
        except Exception:
            self._cache = {}

    def _save_cache(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, 'w', encoding='utf-8') as fh:
            json.dump(self._cache, fh, indent=2, ensure_ascii=False)

    @staticmethod
    def _entry_key(text: str, entry_id: Optional[str] = None) -> str:
        # Stable key for caching: sha1 of text + optional entry id
        h = hashlib.sha1()
        key_base = (entry_id or "") + "|" + (text or "")
        h.update(key_base.encode('utf-8'))
        return h.hexdigest()

    def classify(self, text: str, entry_id: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """Classify a single sanitized display title.

        Returns a dict with keys: category, confidence, tags, rationale, model, cached
        """
        if not isinstance(text, str):
            raise ValueError("text must be a string")

        key = self._entry_key(text, entry_id)
        if not force and key in self._cache:
            out = dict(self._cache[key])
            out['cached'] = True
            return out

        # Build the prompt (system + few shots) - minimal, we send only the sanitized text
        prompt = self._build_prompt(text)

        raw = None
        parsed = None
        used_model = None

        # Try real API if api_key present and openai is available
        if self.api_key:
            try:
                import openai
                openai.api_key = self.api_key
                resp = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": prompt['system']},
                        {"role": "user", "content": prompt['user']}
                    ],
                    max_tokens=200,
                    temperature=0.0,
                    n=1,
                )
                raw = resp.choices[0].message.content
                used_model = getattr(resp, 'model', self.model)
            except Exception:
                # On any failure, fall back to simulated response
                raw = None

        if raw is None:
            raw = self._simulate_response(text)
            used_model = 'simulated'

        parsed = self._parse_json(raw)

        if not parsed:
            # fallback to conservative local categorization
            parsed = self._local_fallback(text)
            parsed['model'] = used_model

        # Persist to cache
        entry = dict(parsed)
        entry['raw_response'] = raw
        entry['model'] = used_model
        entry['ts'] = int(time.time())
        self._cache[key] = entry
        try:
            self._save_cache()
        except Exception:
            pass

        out = dict(entry)
        out['cached'] = False
        return out

    def _build_prompt(self, text: str) -> Dict[str, str]:
        system = (
            "You are a concise assistant that classifies short application/tab titles for productivity analysis. "
            "Respond ONLY with a single JSON object with fields: category, confidence, tags, rationale. "
            "Allowed categories: focus, distraction, neutral. Confidence: float 0-100. Tags: array of short labels. "
            "Rationale: one short sentence <= 30 words. Do not include any other text."
        )

        # Include a couple of examples to bias the model
        user = (
            f"Title: \"{text}\"\n\nExamples:\n"
            "Title: \"Chrome — Inbox (Gmail)\"\n"
            "Output: {\"category\":\"neutral\",\"confidence\":85.0,\"tags\":[\"email\",\"communication\"],\"rationale\":\"Email likely neutral work-related communication.\"}\n"
            "Title: \"Chrome — YouTube\"\n"
            "Output: {\"category\":\"distraction\",\"confidence\":95.0,\"tags\":[\"video\",\"entertainment\"],\"rationale\":\"YouTube generally indicates entertainment/video content.\"}\n"
            f"Now classify only: \"{text}\""
        )
        return {'system': system, 'user': user}

    def _parse_json(self, raw: str) -> Optional[Dict[str, Any]]:
        """Robustly extract and parse a JSON object from model output."""
        if not raw or not isinstance(raw, str):
            return None

        raw = raw.strip()
        # Quick attempt: direct json.loads
        try:
            return json.loads(raw)
        except Exception:
            pass

        # Fallback: find first { and last } and try to parse that substring
        try:
            start = raw.find('{')
            end = raw.rfind('}')
            if start != -1 and end != -1 and end > start:
                candidate = raw[start:end+1]
                return json.loads(candidate)
        except Exception:
            return None

        return None

    def _simulate_response(self, text: str) -> str:
        """Return a deterministic simulated JSON response for testing without network."""
        low = text.lower()
        if 'youtube' in low or 'tiktok' in low or 'instagram' in low:
            obj = {'category': 'distraction', 'confidence': 95.0, 'tags': ['video', 'entertainment'], 'rationale': 'Site indicates entertainment/video content.'}
        elif 'gmail' in low or 'inbox' in low or 'mail' in low:
            obj = {'category': 'neutral', 'confidence': 80.0, 'tags': ['email', 'communication'], 'rationale': 'Email/communication - often neutral.'}
        elif any(x in low for x in ['code', 'vscode', 'pycharm', 'terminal']):
            obj = {'category': 'focus', 'confidence': 99.0, 'tags': ['code', 'editor'], 'rationale': 'Developer editor - focused work.'}
        elif 'linkedin' in low or 'twitter' in low or 'x -' in low:
            obj = {'category': 'distraction', 'confidence': 70.0, 'tags': ['social'], 'rationale': 'Social feed - likely distraction.'}
        else:
            obj = {'category': 'neutral', 'confidence': 60.0, 'tags': [], 'rationale': 'Unclear from title; marked neutral by default.'}
        return json.dumps(obj)

    def _local_fallback(self, text: str) -> Dict[str, Any]:
        """A conservative fallback if parsing fails."""
        low = (text or '').lower()
        if any(k in low for k in ['youtube', 'tiktok', 'instagram', 'reddit']):
            return {'category': 'distraction', 'confidence': 80.0, 'tags': ['social'], 'rationale': 'Recognized social/video site.'}
        if any(k in low for k in ['inbox', 'gmail', 'mail']):
            return {'category': 'neutral', 'confidence': 70.0, 'tags': ['email'], 'rationale': 'Email-like title.'}
        if any(k in low for k in ['code', 'vscode', 'pycharm', 'terminal']):
            return {'category': 'focus', 'confidence': 90.0, 'tags': ['code'], 'rationale': 'Developer tool likely focused.'}
        return {'category': 'neutral', 'confidence': 50.0, 'tags': [], 'rationale': 'Default neutral fallback.'}
