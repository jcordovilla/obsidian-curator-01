from .llm import chat_text

SUM_SYS = "You produce writer-ready, neutral, specific summaries for technical audiences."

def summarize_content(content, meta, cats, cfg):
    kind = content.get('kind')
    text = content.get('text','')[:12000]
    if kind=='pdf':
        prompt = f"TITLE:{meta.get('title','')}\nCATS:{cats}\nEXTRACT:{text}\nWrite: 120-150 word abstract; 8 bullets with strongest claims; 2 short quotes; and a 'Why this matters' paragraph."
        return chat_text(cfg['models']['main'], system=SUM_SYS, user=prompt, tokens=900)
    if kind=='image':
        prompt = f"TITLE:{meta.get('title','')}\nOCR:{text}\nDescribe the image, 4-6 key details, and a 'Use in writing' suggestion."
        return chat_text(cfg['models']['fast'], system=SUM_SYS, user=prompt, tokens=500)
    prompt = f"TITLE:{meta.get('title','')}\nEXTRACT:{text}\nWrite a 70-120 word abstract and 2-3 bullets."
    return chat_text(cfg['models']['fast'], system=SUM_SYS, user=prompt, tokens=300)
