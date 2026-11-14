from django.db import models
from accounts.models import Student


class ResultBatch(models.Model):

    EXAM_TYPE_CHOICES = [
        ("REGULAR", "Regular"),
        ("BACKLOG", "Backlog"),
    ]

    semester = models.PositiveIntegerField()

    exam_type = models.CharField(
        max_length=20,
        choices=EXAM_TYPE_CHOICES
    )

    exam_session = models.CharField(
        max_length=50
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Semester {self.semester} - "
            f"{self.exam_type} - "
            f"{self.exam_session}"
        )


class Subject(models.Model):

    course_code = models.CharField(
        max_length=50
    )

    subject_code = models.CharField(
        max_length=50,
        blank=True
    )

    subject_name = models.CharField(
        max_length=200
    )

    semester = models.PositiveIntegerField()

    credits = models.FloatField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.course_code} - {self.subject_name}"


class Result(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    batch = models.ForeignKey(
        ResultBatch,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    obtained_marks = models.FloatField(
        null=True,
        blank=True
    )

    grade = models.CharField(
        max_length=20,
        blank=True
    )

    grade_point = models.FloatField(
        null=True,
        blank=True
    )

    credits = models.FloatField(
        null=True,
        blank=True
    )

    result_status = models.CharField(
        max_length=50,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.student.student_id} - "
            f"{self.subject.subject_name}"
        )


class ResultFile(models.Model):

    FILE_TYPE_CHOICES = [
        ("PDF", "PDF"),
        ("CSV", "CSV"),
        ("XLSX", "XLSX"),
    ]

    PROCESSING_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    batch = models.ForeignKey(
        ResultBatch,
        on_delete=models.CASCADE,
        related_name="files"
    )

    file = models.FileField(
        upload_to="result_files/"
    )

    file_type = models.CharField(
        max_length=10,
        choices=FILE_TYPE_CHOICES
    )

    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default="PENDING"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.file.name