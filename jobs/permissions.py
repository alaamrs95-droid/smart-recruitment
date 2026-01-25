# jobs/permissions.py
from rest_framework.permissions import BasePermission

class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "employer"
    

class IsJobOwner(BasePermission):
    """يسمح فقط لمالك الوظيفة"""
    def has_object_permission(self, request, view, obj):
        return obj.employer == request.user
