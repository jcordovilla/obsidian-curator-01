import json, os

class EmbeddingIndex:
    path = None
    model = None
    @classmethod
    def init(cls, path, model):
        cls.path = path; cls.model = model
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # TODO: load/create FAISS index

    @classmethod
    def add(cls, note_path, embedding):
        # TODO: add to FAISS and persist
        pass

class Manifest:
    path = None
    @classmethod
    def init(cls, path):
        cls.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, 'w', encoding='utf-8').close()

    @classmethod
    def update(cls, note_path, score, decision, primary):
        with open(cls.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"note": note_path, "score": score, "decision": decision, "primary": primary})+"\\n")
