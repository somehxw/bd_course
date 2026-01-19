from django.db import models

from accounts.models import Student
from courses.models import Assignment


class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="submissions")
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["assignment", "student"],
                name="unique_submission_per_assignment_student",
            )
        ]

    def __str__(self) -> str:
        return f"{self.assignment_id}:{self.student_id}"


class SubmissionFile(models.Model):
    file_id = models.AutoField(primary_key=True)
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="files"
    )
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.submission_id}:{self.file_id}"
