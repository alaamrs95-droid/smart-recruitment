# jobs/views/api.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q  
from django.shortcuts import get_object_or_404
from ..models import Job
from ..serializers import JobSerializer
from accounts.permissions import IsEmployer
from django.db import models

class JobListAPIView(generics.ListAPIView):
    """API لعرض جميع الوظائف النشطة (عام)"""
    permission_classes = [permissions.AllowAny]
    serializer_class = JobSerializer
    queryset = Job.objects.filter(is_active=True).select_related('employer')
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فلترة حسب البحث
        search_query = self.request.query_params.get('q', '')
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query) |
                models.Q(description__icontains=search_query)
            )
        
        # فلترة حسب المهارات
        skill_filter = self.request.query_params.get('skill', '')
        if skill_filter:
            queryset = queryset.filter(required_skills__contains=[skill_filter])
        
        return queryset

class JobDetailAPIView(generics.RetrieveAPIView):
    """API لعرض تفاصيل وظيفة محددة"""
    permission_classes = [permissions.AllowAny]
    serializer_class = JobSerializer
    queryset = Job.objects.filter(is_active=True)
    lookup_field = 'pk'

class CreateJobAPIView(generics.CreateAPIView):
    """API لإنشاء وظيفة جديدة (للموظفين فقط)"""
    permission_classes = [permissions.IsAuthenticated, IsEmployer]
    serializer_class = JobSerializer
    
    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

class UpdateJobAPIView(generics.UpdateAPIView):
    """API لتحديث وظيفة (للمالك فقط)"""
    permission_classes = [permissions.IsAuthenticated, IsEmployer]
    serializer_class = JobSerializer
    queryset = Job.objects.all()
    lookup_field = 'pk'
    
    def get_queryset(self):
        # فقط المالك يمكنه التعديل
        return Job.objects.filter(employer=self.request.user)

class DeleteJobAPIView(generics.DestroyAPIView):
    """API لحذف وظيفة (للمالك فقط)"""
    permission_classes = [permissions.IsAuthenticated, IsEmployer]
    serializer_class = JobSerializer
    queryset = Job.objects.all()
    lookup_field = 'pk'
    
    def get_queryset(self):
        # فقط المالك يمكنه الحذف
        return Job.objects.filter(employer=self.request.user)

class EmployerJobsAPIView(generics.ListAPIView):
    """API لعرض وظائف الموظف نفسه"""
    permission_classes = [permissions.IsAuthenticated, IsEmployer]
    serializer_class = JobSerializer
    
    def get_queryset(self):
        return Job.objects.filter(employer=self.request.user).order_by('-created_at')

