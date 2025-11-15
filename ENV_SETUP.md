# FocusPulse Environment Configuration Guide

## Setup Instructions

### 1. Copy the template
```bash
cp .env.example .env
```

### 2. Add your OpenAI API key
Edit `.env` and replace `sk-your-api-key-here` with your actual key:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxx
```

Get your key from: https://platform.openai.com/account/api-keys

### 3. Never commit `.env` to git
The `.env` file contains secrets and should NEVER be committed. It's already in `.gitignore` (or should be).

Verify:
```bash
echo ".env" >> .gitignore
git check-ignore .env  # Should return .env (meaning it's ignored)
```

## How it works

- **gpt_enricher.py** loads `.env` automatically on import via `python-dotenv`.
- **OPENAI_API_KEY** is read from `.env` (or environment variables as fallback).
- If no key is found, the enricher will use deterministic simulated responses (safe fallback for local testing).

## Troubleshooting

If the API key isn't being picked up:
1. Make sure `.env` is in the project root (same directory as `app.py`, `requirements.txt`, etc.)
2. Verify the file is named exactly `.env` (not `.env.txt` or similar)
3. Restart your Python process or Streamlit app after creating `.env`

## Testing

Quick test to confirm the key is loaded:
```bash
python3.12 -c "from src.gpt_enricher import GPTEnricher; g = GPTEnricher(); print('API Key present:', bool(g.api_key))"
```

If it prints `API Key present: True`, you're good to go!
