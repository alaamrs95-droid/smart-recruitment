# resumes/serializers.py
from rest_framework import serializers
from .models import Resume

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ("id", "file", "raw_text", "parsed_data", "created_at")
        read_only_fields = ("raw_text", "parsed_data")
