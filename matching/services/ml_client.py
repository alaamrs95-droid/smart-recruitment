"""
Client to call Hugging Face Space (Gradio) for similarity predictions.

Usage:
    from matching.services.ml_client import predict_similarity
    score = predict_similarity(cv_text, job_text)

Behavior:
- Uses gradio_client (official)
- Optional caching via Django cache
- Reads settings: ML_SERVICE_URL, HF_TOKEN, ML_SERVICE_CACHE_TTL
"""

from __future__ import annotations

import hashlib
import logging
from typing import Optional

from django.conf import settings
from django.core.cache import cache

from gradio_client import Client

logger = logging.getLogger(__name__)


class MLServiceError(RuntimeError):
    pass


def _cache_key(cv_text: str, job_text: str) -> str:
    h = hashlib.sha256((cv_text + "\n" + job_text).encode("utf-8")).hexdigest()
    return f"ml:sim:{h}"


def _get_client() -> Client:
    """
    Create Gradio Client.
    """
    if not settings.ML_SERVICE_URL:
        raise MLServiceError("ML_SERVICE_URL is not configured")

    try:
        if getattr(settings, "HF_TOKEN", None):
            return Client(settings.ML_SERVICE_URL, hf_token=settings.HF_TOKEN)
        return Client(settings.ML_SERVICE_URL)
    except Exception as exc:
        logger.exception("Failed to initialize Gradio Client")
        raise MLServiceError(f"Failed to initialize ML client: {exc}") from exc


def predict_similarity(
    cv_text: str,
    job_text: str,
    use_cache: bool = True,
    cache_ttl: Optional[int] = None,
) -> float:
    """
    Call the Hugging Face Gradio Space and return similarity score.
    """

    if use_cache:
        key = _cache_key(cv_text, job_text)
        cached = cache.get(key)
        if cached is not None:
            logger.debug("ML cache hit for %s", key)
            return float(cached)

    client = _get_client()

    try:
        result = client.predict(
            cv_text,
            job_text,
            api_name="/predict",  # MUST match api_name in app.py
        )
        score = float(result)
    except Exception as exc:
        logger.exception("ML service prediction failed")
        raise MLServiceError(f"ML service prediction failed: {exc}") from exc

    if use_cache:
        ttl = cache_ttl if cache_ttl is not None else getattr(
            settings, "ML_SERVICE_CACHE_TTL", 3600
        )
        try:
            cache.set(key, score, ttl)
        except Exception:
            logger.exception("Failed to write ML cache for key %s", key)

    return score


__all__ = ["predict_similarity", "MLServiceError"]
