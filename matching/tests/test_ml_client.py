# matching/tests/test_ml_client.py
from django.test import TestCase, override_settings
from django.core.cache import cache
from unittest.mock import patch, Mock
import requests

from matching.services import ml_client
from matching.services.ml_client import MLServiceError


class MLClientTests(TestCase):
    def setUp(self):
        cache.clear()

    @override_settings(ML_SERVICE_URL="https://example.hf.space")
    def test_predict_success_and_cache(self):
        mock_resp = Mock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = {"data": [0.66]}

        with patch.object(ml_client._session, "post", return_value=mock_resp) as mock_post:
            score = ml_client.predict_similarity("cv text", "job text")
            self.assertAlmostEqual(score, 0.66)

            # second call should hit cache (so post not called again)
            score2 = ml_client.predict_similarity("cv text", "job text")
            self.assertAlmostEqual(score2, 0.66)
            self.assertEqual(mock_post.call_count, 1)

    @override_settings(ML_SERVICE_URL="https://example.hf.space")
    def test_network_error_raises_MLServiceError(self):
        with patch.object(ml_client._session, "post", side_effect=requests.RequestException("fail")):
            with self.assertRaises(MLServiceError):
                ml_client.predict_similarity("a", "b")

    @override_settings(ML_SERVICE_URL=None)
    def test_missing_url_raises(self):
        with self.assertRaises(MLServiceError):
            ml_client.predict_similarity("a", "b")
