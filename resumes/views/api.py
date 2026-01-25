# resumes/views/api.py 
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from ..models.uploaded import Resume
from ..serializers import ResumeSerializer
from ..permissions import IsCandidate
from ..services.file_extractor import extract_text
from ..services.parsing import parse_resume
from datetime import datetime

class UploadResumeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCandidate]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # إنشاء السجل أولاً
        resume = Resume.objects.create(
            candidate=request.user,
            file=file,
            original_filename=file.name
        )

        try:
            # استخراج النص
            raw_text = extract_text(resume.file.path)
            resume.raw_text = raw_text
            
            # التحليل
            resume.parsed_data = parse_resume(raw_text)
            
            resume.is_processed = True
            resume.processed_at = datetime.now()
            resume.save()
            
            return Response(ResumeSerializer(resume).data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            resume.is_processed = False
            resume.save()
            return Response(
                {"error": "Failed to process resume"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MyResumesListAPIView(generics.ListAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsCandidate]

    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user).order_by('-created_at')

class ResumeDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'candidate':
            return Resume.objects.filter(candidate=user)
        elif user.role == 'employer':
            return Resume.objects.all()
        return Resume.objects.none()

class UpdateResumeAPIView(generics.UpdateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsCandidate]
    
    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user)
    
    def perform_update(self, serializer):
        resume = serializer.save()
        if 'file' in self.request.FILES:
            # إعادة معالجة الملف
            try:
                raw_text = extract_text(resume.file.path)
                resume.raw_text = raw_text
                resume.parsed_data = parse_resume(raw_text)
                resume.is_processed = True
                resume.processed_at = datetime.now()
                resume.save()
            except Exception:
                resume.is_processed = False
                resume.save()

class DeleteResumeAPIView(generics.DestroyAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [IsCandidate]
    
    def get_queryset(self):
        return Resume.objects.filter(candidate=self.request.user)