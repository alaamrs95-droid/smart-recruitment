#matching/tests/test_ml_api.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import patch

from resumes.models.uploaded import Resume
from jobs.models import Job
from matching.services.ml_client import MLServiceError

User = get_user_model()


class MLPredictAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="alice", password="pw", role=User.CANDIDATE)
        self.other = User.objects.create_user(username="bob", password="pw", role=User.CANDIDATE)

    def test_direct_text_success(self):
        self.client.force_authenticate(self.user)
        url = reverse('ml-predict')
        with patch('matching.services.ml_client.predict_similarity', return_value=0.66) as mock_predict:
            resp = self.client.post(url, {"cv_text": "my cv", "job_text": "job desc"}, format='json')
            self.assertEqual(resp.status_code, 200)
            self.assertAlmostEqual(resp.json().get('score'), 0.66)
            mock_predict.assert_called_once()

    def test_resume_job_ids_success(self):
        resume = Resume.objects.create(candidate=self.user, raw_text="cv text", original_filename="r.pdf")
        job = Job.objects.create(employer=self.other, title="J", description="job desc")
        self.client.force_authenticate(self.user)
        url = reverse('ml-predict')
        with patch('matching.services.ml_client.predict_similarity', return_value=0.55) as mock_predict:
            resp = self.client.post(url, {"resume_id": resume.id, "job_id": job.id}, format='json')
            self.assertEqual(resp.status_code, 200)
            self.assertAlmostEqual(resp.json().get('score'), 0.55)
            mock_predict.assert_called_once()

    def test_resume_not_owned_forbidden(self):
        resume = Resume.objects.create(candidate=self.other, raw_text="cv text", original_filename="r.pdf")
        job = Job.objects.create(employer=self.other, title="J", description="job desc")
        self.client.force_authenticate(self.user)
        url = reverse('ml-predict')
        resp = self.client.post(url, {"resume_id": resume.id, "job_id": job.id}, format='json')
        self.assertEqual(resp.status_code, 403)

    def test_ml_service_error_returns_503(self):
        self.client.force_authenticate(self.user)
        url = reverse('ml-predict')
        with patch('matching.services.ml_client.predict_similarity', side_effect=MLServiceError("service down")):
            resp = self.client.post(url, {"cv_text": "a", "job_text": "b"}, format='json')
            self.assertEqual(resp.status_code, 503)
            self.assertIn('service down', resp.json().get('error', ''))
