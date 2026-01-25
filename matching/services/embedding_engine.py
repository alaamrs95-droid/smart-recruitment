# matching/services/embedding_engine.py

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache
import numpy as np

_MODEL = None
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def get_model():
    """
    تحميل النموذج مرة واحدة فقط
    """
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(MODEL_NAME)
    return _MODEL


@lru_cache(maxsize=512)
def get_embedding(text: str) -> tuple:
    """
    حساب embedding مع caching
    نُرجع tuple لأن lru_cache لا يقبل numpy array
    """
    if not text or not text.strip():
        return tuple(np.zeros(384))

    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return tuple(vector)


def similarity(text1: str, text2: str) -> float:
    """
    حساب التشابه الدلالي بين نصين
    """
    v1 = np.array(get_embedding(text1)).reshape(1, -1)
    v2 = np.array(get_embedding(text2)).reshape(1, -1)

    return float(cosine_similarity(v1, v2)[0][0])
