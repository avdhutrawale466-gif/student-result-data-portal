from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile"
    )

    student_id = models.CharField(
        max_length=50,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True
    )

    email_verified = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.student_id