from .llm import chat_json

CLASSIFY_SYS = "You are a precise classifier for infrastructure/PPP/governance. Return strict JSON."

def classify_json(content, meta, cfg):
    text = content.get('text','')[:4000]
    user = f'TITLE:{meta.get("title","")}\nEXTRACT:{text}\nCATS:{",".join(cfg["taxonomy"]["categories"])}\nReturn JSON with "categories","tags","entities".'
    data = chat_json(cfg['models']['fast'], system=CLASSIFY_SYS, user=user, tokens=512)
    cats = data.get('categories',[])
    tags = data.get('tags',[])
    ents = data.get('entities',{})
    return cats, tags, ents
