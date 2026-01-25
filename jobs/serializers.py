# jobs/serializers.py
from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    employer = serializers.ReadOnlyField(source='employer.username')
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description',
            'required_skills', 'preferred_skills',
            'languages', 'education_level',
            'experience_years', 'is_active',
            'employer', 'created_at', 'updated_at'
        ]
        read_only_fields = ('employer', 'created_at', 'updated_at')





