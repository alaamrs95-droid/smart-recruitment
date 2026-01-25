# accounts/views/api.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password

from accounts.serializers import RegisterSerializer, UserMeSerializer
from accounts.permissions import IsCandidate, IsEmployer

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # حفظ اليوزر وتخزينه في متغير
            refresh = RefreshToken.for_user(user)  # توليد الـ tokens
            return Response(
                {
                    "message": "User registered successfully",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginAPIView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

class MeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)

class EmployerOnlyView(APIView):
    permission_classes = [IsEmployer]

    def get(self, request):
        return Response({"message": "Hello Employer!"})
    

class CandidateOnlyView(APIView):
    permission_classes = [IsCandidate]
    
    def get(self, request):
        return Response({"message": "Hello Candidate!"})