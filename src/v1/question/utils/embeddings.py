# src/utils/embeddings.py

from sentence_transformers import SentenceTransformer

# Load once at module level
_model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str) -> list[float]:
    """Generates a 384-dimensional vector embedding for the given text."""
    return _model.encode(text).tolist()
