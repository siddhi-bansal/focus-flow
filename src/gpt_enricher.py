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

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        pass  # No-op if python-dotenv not installed

# Load .env file at module import time with override to ensure fresh values
load_dotenv(override=True)


class GPTEnricher:
    """A small wrapper to call an LLM for classification with local caching.

    It intentionally keeps network usage optional and provides a safe simulated
    response when no API key is available.
    """

    DEFAULT_CACHE = Path(__file__).parent.parent / "data" / "gpt_cache.json"

    def __init__(self, cache_path: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.cache_path = Path(cache_path) if cache_path else self.DEFAULT_CACHE
        self.api_key = os.environ.get('OPENAI_API_KEY')
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
            cached_entry = self._cache[key]
            # Prioritize user overrides, then real API results (skip simulated)
            if cached_entry.get('user_override'):
                out = dict(cached_entry)
                out['cached'] = True
                return out
            elif cached_entry.get('model') and cached_entry.get('model') != 'simulated':
                out = dict(cached_entry)
                out['cached'] = True
                return out

        # Build the prompt (system + few shots) - minimal, we send only the sanitized text
        prompt = self._build_prompt(text)

        raw = None
        parsed = None
        used_model = None

        # Try real API if api_key present and openai is available
        api_error = None
        if self.api_key:
            try:
                import openai

                # Prefer the new OpenAI client if available
                if hasattr(openai, 'OpenAI'):
                    client = openai.OpenAI(api_key=self.api_key)
                    resp = client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": prompt['system']},
                            {"role": "user", "content": prompt['user']}
                        ],
                        max_tokens=200,
                        temperature=0.0,
                    )
                    # Robust extraction of text
                    try:
                        # new client: resp.choices[0].message.content or resp.choices[0].message['content']
                        raw = resp.choices[0].message.content
                    except Exception:
                        try:
                            raw = resp.choices[0].message['content']
                        except Exception:
                            # fallback to string conversion
                            raw = str(resp)
                    used_model = getattr(resp, 'model', self.model)
                else:
                    # Older openai package (pre-1.0)
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
            except Exception as e:
                # On any failure, fall back to simulated response
                api_error = repr(e)
                print(f"gpt_enricher: OpenAI call failed: {api_error}")
                raw = None

        if raw is None:
            # No API response - return error state
            return {
                'category': 'not set',
                'confidence': 0.0,
                'tags': [],
                'rationale': 'AI classification failed',
                'model': 'error',
                'api_error': api_error or 'No API response',
                'cached': False
            }

        parsed = self._parse_json(raw)

        if not parsed:
            # Failed to parse response - return error state
            return {
                'category': 'not set',
                'confidence': 0.0,
                'tags': [],
                'rationale': 'Failed to parse AI response',
                'model': used_model,
                'api_error': api_error or 'Parse error',
                'cached': False
            }

        # Persist to cache only if this result came from the real API
        out = dict(parsed)
        out['raw_response'] = raw
        out['model'] = used_model
        out['ts'] = int(time.time())
        if api_error:
            out['api_error'] = api_error

        if used_model and used_model != 'simulated':
            # store only OpenAI-produced results
            try:
                self._cache[key] = dict(out)
                self._save_cache()
            except Exception:
                pass

        out['cached'] = False
        return out

    def _build_prompt(self, text: str) -> Dict[str, str]:
        system = (
            "You are a concise assistant that classifies short application/tab titles for productivity analysis. "
            "Respond ONLY with a single JSON object with fields: category, confidence, tags, rationale. "
            "\n\nCategory definitions:\n"
            "- focus: Apps/sites used for productive work (coding, writing, email, work research, design tools, documentation)\n"
            "- distraction: Apps/sites primarily for entertainment, social media, gaming, or leisure (YouTube, social feeds, streaming)\n"
            "- neutral: Ambiguous or utility apps that depend on context (browser without clear purpose, system tools, general search)\n"
            "\nConfidence: float 0-100. Tags: array of short labels. "
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



    def save_override(self, text: str, category: str, confidence: float = 100.0, 
                      tags: list = None, rationale: str = None, entry_id: Optional[str] = None) -> None:
        """Save a user override for a classification.
        
        Args:
            text: The sanitized display title
            category: User's chosen category (focus, distraction, neutral)
            confidence: Confidence score (default 100 for user overrides)
            tags: Optional list of tags
            rationale: Optional user rationale
            entry_id: Optional entry identifier for cache key
        """
        if category not in ('focus', 'distraction', 'neutral'):
            raise ValueError(f"Invalid category: {category}")
        
        key = self._entry_key(text, entry_id)
        entry = {
            'category': category,
            'confidence': confidence,
            'tags': tags or [],
            'rationale': rationale or f'User override: {category}',
            'user_override': True,
            'ts': int(time.time())
        }
        self._cache[key] = entry
        self._save_cache()

    def get_all_cached(self) -> Dict[str, Any]:
        """Return all cached entries (for UI display)."""
        return dict(self._cache)
