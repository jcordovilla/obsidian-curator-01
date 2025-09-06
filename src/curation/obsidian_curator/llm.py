import json, requests

def _chat_payload(model, messages, tokens, temp):
    return {"model": model, "messages": messages, "options": {"temperature": temp, "num_predict": tokens}, "stream": False}

def chat_text(model, system, user, tokens=512, temp=0.2):
    r = requests.post("http://localhost:11434/api/chat",
                      json=_chat_payload(model, [{"role":"system","content":system},
                                                 {"role":"user","content":user}], tokens, temp))
    r.raise_for_status()
    return r.json()["message"]["content"]

def chat_json(model, system, user, tokens=512, temp=0.2):
    text = chat_text(model, system, user + "\\nReturn ONLY strict JSON.", tokens, temp)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Try to extract JSON from the response
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_text = text[start:end+1]
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                # If still failing, return a safe default
                print(f"Warning: Could not parse JSON from LLM response: {e}")
                return {"categories": ["Unknown"], "tags": ["unknown"], "entities": {"orgs": [], "places": [], "years": []}}
        else:
            # No JSON found, return safe default
            print(f"Warning: No JSON found in LLM response")
            return {"categories": ["Unknown"], "tags": ["unknown"], "entities": {"orgs": [], "places": [], "years": []}}

def embed_text(text, model):
    r = requests.post("http://localhost:11434/api/embeddings", json={"model": model, "prompt": text})
    r.raise_for_status()
    return r.json().get("embedding")
