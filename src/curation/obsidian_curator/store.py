import json, os
import numpy as np

class EmbeddingIndex:
    path = None
    model = None
    index = None
    note_paths = []
    
    @classmethod
    def init(cls, path, model):
        """Initialize FAISS index for semantic search."""
        cls.path = path
        cls.model = model
        cls.note_paths = []
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Try to load existing index
        if os.path.exists(path):
            try:
                import faiss
                cls.index = faiss.read_index(path)
                # Load note paths mapping
                mapping_path = path + '.mapping'
                if os.path.exists(mapping_path):
                    with open(mapping_path, 'r', encoding='utf-8') as f:
                        cls.note_paths = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing index: {e}")
                cls.index = None
        
        # Create new index if needed
        if cls.index is None:
            try:
                import faiss
                # Use 768 dimensions for nomic-embed-text embeddings
                cls.index = faiss.IndexFlatL2(768)
            except ImportError:
                print("Warning: FAISS not installed. Embeddings will not be persisted.")
                cls.index = None

    @classmethod
    def add(cls, note_path, embedding):
        """Add note embedding to FAISS index and persist."""
        if cls.index is None or embedding is None:
            return
        
        try:
            import faiss
            # Convert embedding to numpy array if needed
            if isinstance(embedding, list):
                embedding = np.array(embedding, dtype=np.float32)
            elif not isinstance(embedding, np.ndarray):
                return
            
            # Ensure correct shape (1, 768)
            if embedding.ndim == 1:
                embedding = embedding.reshape(1, -1)
            
            # Add to index
            cls.index.add(embedding)
            cls.note_paths.append(note_path)
            
            # Persist index and mapping
            faiss.write_index(cls.index, cls.path)
            mapping_path = cls.path + '.mapping'
            with open(mapping_path, 'w', encoding='utf-8') as f:
                json.dump(cls.note_paths, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not add embedding to index: {e}")

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
