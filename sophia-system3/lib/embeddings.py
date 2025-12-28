"""
embeddings.py - Optional embedding generation for semantic search

Implements 3-tier fallback:
1. Keyword search (always available)
2. OpenAI API (if OPENAI_API_KEY set)
3. Local model (if sentence-transformers installed)

Lazy indexing: Episodes without embeddings use keyword fallback.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path


class EmbeddingProvider:
    """Base class for embedding providers."""

    def embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text. Returns None if unavailable."""
        raise NotImplementedError

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        return [self.embed(t) for t in texts]

    @property
    def available(self) -> bool:
        """Check if this provider is available."""
        return False

    @property
    def dimension(self) -> int:
        """Embedding dimension."""
        return 0


class OpenAIProvider(EmbeddingProvider):
    """OpenAI API embedding provider."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self._client = None
        self._dimension = 1536

    @property
    def available(self) -> bool:
        return "OPENAI_API_KEY" in os.environ

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI()
            except ImportError:
                return None
        return self._client

    def embed(self, text: str) -> Optional[List[float]]:
        if not self.available:
            return None

        client = self._get_client()
        if client is None:
            return None

        try:
            response = client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception:
            return None

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        if not self.available or not texts:
            return [None] * len(texts)

        client = self._get_client()
        if client is None:
            return [None] * len(texts)

        try:
            response = client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception:
            return [None] * len(texts)


class LocalProvider(EmbeddingProvider):
    """Local sentence-transformers embedding provider."""

    def __init__(self, model: str = "all-MiniLM-L6-v2"):
        self.model_name = model
        self._model = None
        self._dimension = 384

    @property
    def available(self) -> bool:
        try:
            import sentence_transformers
            return True
        except ImportError:
            return False

    @property
    def dimension(self) -> int:
        return self._dimension

    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except Exception:
                return None
        return self._model

    def embed(self, text: str) -> Optional[List[float]]:
        model = self._get_model()
        if model is None:
            return None

        try:
            embedding = model.encode(text)
            return embedding.tolist()
        except Exception:
            return None

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        if not texts:
            return []

        model = self._get_model()
        if model is None:
            return [None] * len(texts)

        try:
            embeddings = model.encode(texts)
            return [e.tolist() for e in embeddings]
        except Exception:
            return [None] * len(texts)


class EmbeddingManager:
    """Manages embedding generation with fallback providers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or {}
        provider_name = config.get("embedding_provider", "none")

        self.providers: List[EmbeddingProvider] = []

        # Add providers based on config
        if provider_name == "openai":
            model = config.get("embedding_model", "text-embedding-3-small")
            self.providers.append(OpenAIProvider(model))
        elif provider_name == "local":
            self.providers.append(LocalProvider())

        # Always add local as fallback if not primary
        if provider_name != "local":
            self.providers.append(LocalProvider())

    def get_provider(self) -> Optional[EmbeddingProvider]:
        """Get the first available provider."""
        for provider in self.providers:
            if provider.available:
                return provider
        return None

    def embed(self, text: str) -> Optional[List[float]]:
        """Generate embedding using first available provider."""
        provider = self.get_provider()
        if provider:
            return provider.embed(text)
        return None

    def embed_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts."""
        provider = self.get_provider()
        if provider:
            return provider.embed_batch(texts)
        return [None] * len(texts)

    @property
    def available(self) -> bool:
        """Check if any embedding provider is available."""
        return self.get_provider() is not None


def embeddings_available() -> bool:
    """Quick check if embeddings are available."""
    manager = EmbeddingManager()
    return manager.available


def embed_text(text: str, config: Optional[Dict[str, Any]] = None) -> Optional[List[float]]:
    """Generate embedding for text using configured provider."""
    manager = EmbeddingManager(config)
    return manager.embed(text)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(a) != len(b):
        return 0.0

    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)
