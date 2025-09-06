import os, json, requests
TEST_MODE = os.getenv("OC_TEST_MODE") == "1"

def _chat_payload(model, messages, tokens, temp):
    return {"model": model, "messages": messages, "options": {"temperature": temp, "num_predict": tokens}}

def chat_text(model, system, user, tokens=512, temp=0.2):
    if TEST_MODE:
        return "TEST_MODE_SUMMARY: This is a deterministic stub response for CI."
    r = requests.post("http://localhost:11434/api/chat",
                      json=_chat_payload(model, [{"role":"system","content":system},
                                                 {"role":"user","content":user}], tokens, temp))
    r.raise_for_status()
    return r.json()["message"]["content"]

def chat_json(model, system, user, tokens=512, temp=0.2):
    if TEST_MODE:
        return {"categories": ["PPP"], "tags": ["ppp", "governance"], "entities": {"orgs": [], "places": [], "years": []}}
    text = chat_text(model, system, user + "\\nReturn ONLY strict JSON.", tokens, temp)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{"); end = text.rfind("}")
        if start!=-1 and end!=-1 and end>start:
            return json.loads(text[start:end+1])
        raise

def embed_text(text, model):
    if TEST_MODE:
        return [0.0, 0.1, 0.2, 0.3]  # short, deterministic
    r = requests.post("http://localhost:11434/api/embeddings", json={"model": model, "prompt": text})
    r.raise_for_status()
    return r.json().get("embedding")
