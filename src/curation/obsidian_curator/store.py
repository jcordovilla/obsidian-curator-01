import json, os
import numpy as np

class EmbeddingIndex:
    path = None
    model = None
    index = None
    note_paths = []
    
    @classmethod
    def init(cls, path, model, embed_dims=1536):
        """Initialize FAISS index for semantic search.
        
        Args:
            path: Path to index file
            model: Model identifier (for tracking)
            embed_dims: Embedding dimensions (1536 for text-embedding-3-small, 768 for nomic-embed-text)
        """
        cls.path = path
        cls.model = model
        cls.embed_dims = embed_dims
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
                # Use configurable dimensions (1536 for OpenAI, 768 for nomic)
                cls.index = faiss.IndexFlatL2(embed_dims)
            except ImportError:
                print("Warning: FAISS not installed. Embeddings will not be persisted.")
                cls.index = None

    @classmethod
    def add(cls, note_path, embedding):
        """Add note embedding to FAISS index and persist."""
        if cls.index is None:
            print(f"Warning: FAISS index not initialized, skipping embedding storage")
            return
            
        if embedding is None:
            print(f"Warning: No embedding provided for {note_path}, skipping")
            return
        
        try:
            import faiss
            # Convert embedding to numpy array if needed
            if isinstance(embedding, list):
                embedding = np.array(embedding, dtype=np.float32)
            elif not isinstance(embedding, np.ndarray):
                print(f"Warning: Embedding is not list or array: {type(embedding)}")
                return
            
            # Ensure correct shape - use dynamic dims from class
            expected_dims = getattr(cls, 'embed_dims', 1536)
            if embedding.shape[0] != expected_dims:
                print(f"Warning: Embedding has {embedding.shape[0]} dims, expected {expected_dims}")
                return
                
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
    def update(cls, note_path, score, decision, primary, features=None, categories=None):
        """
        Update manifest with enhanced instrumentation.
        
        Args:
            note_path: Path to note
            score: Final usefulness score
            decision: keep/discard/triage
            primary: Primary content type
            features: Optional dict with llm_usefulness, content_richness, reasoning
            categories: Optional list of assigned categories
        """
        entry = {
            "note": note_path,
            "score": score,
            "decision": decision,
            "primary": primary
        }
        
        # Add instrumentation data if available
        if features:
            entry["llm_score"] = features.get('llm_usefulness')
            entry["heuristic_score"] = features.get('content_richness')
            entry["reasoning"] = features.get('reasoning')
            entry["length_chars"] = features.get('length_chars')
        
        if categories:
            entry["categories"] = categories
        
        with open(cls.path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\\n")
