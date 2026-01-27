# matching/views/api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from resumes.models import Resume
from jobs.models import Job
from matching.services.matcher import match_resume_to_job, batch_match_resumes_to_job, batch_match_jobs_to_resume
from accounts.permissions import IsEmployer, IsCandidate

# ML client
from matching.services.ml_client import predict_similarity, MLServiceError



class MatchResumeJobsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, resume_id):
        # 1. التحقق من ملكية السيرة الذاتية
        try:
            resume = Resume.objects.get(
                id=resume_id,
                candidate=request.user
            )
        except Resume.DoesNotExist:
            return Response(
                {"error": "Resume not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. جلب الوظائف النشطة فقط
        jobs = Job.objects.filter(is_active=True).select_related("employer")
        
        # ⚠️ استخدام الدالة المحسنة للمطابقة الدفعية
        matches = batch_match_jobs_to_resume(resume, jobs)
        results = []

        # 3. حلقة المطابقة
        for job in jobs:
            match_result = match_resume_to_job(resume, job)

            if match_result["score"] > 10:
                results.append({
                    "job_id": job.id,
                    "job_title": job.title,
                    "employer": job.employer.username,
                    "match": match_result,
                })

        # 4. الترتيب
        results.sort(
            key=lambda x: x["match"]["score"],
            reverse=True
        )

        return Response({
            "resume_id": resume.id,
            "matches_count": len(results),
            "matches": results
        })
    


class MatchJobsResumeAPIView(APIView):

    def get(self, request, job_id):
        # 1. التأكد أن الوظيفة موجودة وتخص صاحب العمل
        try:
            job = Job.objects.get(
                id=job_id,
                employer=request.user
            )
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found or not owned by you"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. جلب السير الذاتية المعالجة فقط
        resumes = Resume.objects.filter(is_processed=True).select_related('candidate')
        
        # ⚠️ استخدام الدالة المحسنة للمطابقة الدفعية
        matches = batch_match_resumes_to_job(job, resumes)
        results = []

        # 3. المطابقة
        for resume in resumes:
            match = match_resume_to_job(resume, job)

            # فلترة ذكية (نتجنب الضجيج)
            if match["score"] >= 20:
                results.append({
                    "resume_id": resume.id,
                    "candidate": resume.candidate.username,
                    "score": match["score"],
                    "color": match["color"],
                    "reasons": match["reasons"],
                    "details": match["details"],
                })

        # 4. ترتيب تنازلي
        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "candidates_count": len(results),
            "candidates": results
        })


class MLPredictAPIView(APIView):
    """POST endpoint to get similarity score.

    Accepts either:
    - {'cv_text': ..., 'job_text': ...}
    or
    - {'resume_id': <id>, 'job_id': <id>} (resume must be owned by user)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        cv_text = data.get("cv_text")
        job_text = data.get("job_text")
        resume_id = data.get("resume_id")
        job_id = data.get("job_id")

        if resume_id and not cv_text:
            try:
                resume = Resume.objects.get(id=resume_id)
            except Resume.DoesNotExist:
                return Response({"error": "Resume not found"}, status=status.HTTP_404_NOT_FOUND)
            if resume.candidate != request.user:
                return Response({"error": "Permission denied for resume"}, status=status.HTTP_403_FORBIDDEN)
            cv_text = resume.raw_text

        if job_id and not job_text:
            try:
                job = Job.objects.get(id=job_id)
            except Job.DoesNotExist:
                return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
            job_text = job.description

        if not cv_text or not job_text:
            return Response({"error": "Provide cv_text and job_text or resume_id and job_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            score = predict_similarity(cv_text, job_text)
        except MLServiceError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({"score": score})
