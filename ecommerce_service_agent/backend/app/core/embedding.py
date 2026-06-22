from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.utils.logger import log

"""
向量化模型 - 将文本转为向量
"""
class EmbeddingModel:
    """向量化模型（单例）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.dim = 768
        log.info(f"Embedding 模型加载完成: {settings.EMBEDDING_MODEL}")

    @staticmethod
    def _l2_normalize(vector: List[float]) -> List[float]:
        arr = np.array(vector)
        norm = np.linalg.norm(arr)
        return (arr / norm).tolist() if norm != 0 else vector

    def encode(self, text: str) -> List[float]:
        vector = self.model.encode(text).tolist()
        return self._l2_normalize(vector)

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        vectors = self.model.encode(texts).tolist()
        return [self._l2_normalize(v) for v in vectors]


embedding_model = EmbeddingModel()