"""Thin LLM client: Gemini REST first, OpenRouter fallback. No key = LLMUnavailable (we never fake an answer)."""
import json, os, urllib.request, urllib.error, re

class LLMUnavailable(Exception):
    pass

def _post(url, payload, headers, timeout=60):
    req = urllib.request.Request(url, json.dumps(payload).encode(), headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def provider():
    if os.environ.get("GEMINI_API_KEY"): return "gemini"
    if os.environ.get("OPENROUTER_API_KEY"): return "openrouter"
    return None

def complete(system, user, json_mode=False):
    p = provider()
    try:
        if p == "gemini":
            model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user}]}],
                    "generationConfig": {"temperature": 0.1, **({"responseMimeType": "application/json"} if json_mode else {})}}
            out = _post(url, body, {"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
            return out["candidates"][0]["content"]["parts"][0]["text"]
        if p == "openrouter":
            model = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
            body = {"model": model, "temperature": 0.1, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
            out = _post("https://openrouter.ai/api/v1/chat/completions", body, {"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]})
            return out["choices"][0]["message"]["content"]
    except (urllib.error.URLError, KeyError, IndexError) as e:
        raise LLMUnavailable(f"{p} call failed: {e}")
    raise LLMUnavailable("no GEMINI_API_KEY or OPENROUTER_API_KEY set")

def complete_json(system, user):
    txt = complete(system, user, json_mode=True)
    m = re.search(r"\{.*\}", txt, re.S)
    return json.loads(m.group(0))
