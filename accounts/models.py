# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    EMPLOYER = "employer"
    CANDIDATE = "candidate"

    ROLE_CHOICES = (
        (EMPLOYER, "Employer"),
        (CANDIDATE, "Candidate"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
