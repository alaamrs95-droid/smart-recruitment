#matching/services/README.md
Usage
-----

This module provides a simple HTTP client to call a Gradio/Hugging Face Space that exposes `/api/predict/` and returns similarity scores.

1. Add to your `.env`:

ML_SERVICE_URL=https://<username>-<space>.hf.space
HF_TOKEN=<token-if-private>
ML_SERVICE_TIMEOUT=10
ML_SERVICE_CACHE_TTL=3600

2. Example:

from matching.services.ml_client import predict_similarity
score = predict_similarity(cv_text, job_text)

3. Production recommendations:
- Use Redis for Django cache for sharing cached results across workers.
- Run the ML calls in background tasks (Celery/RQ) when comparing many resumes.
- Add rate-limiting / monitoring for the ML service.

4. Running tests:
- The project uses Django's test runner. You can run the matching tests with:

    python manage.py test matching

- If test runner fails due to missing dependencies when running locally, run the small unit tests by setting up a lightweight dev environment or use pytest with proper PYTHONPATH and installed requirements.
