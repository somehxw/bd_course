from django.db import models

from learning.models import Enrollment


class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment"],
                name="unique_review_per_enrollment",
            )
        ]

    def __str__(self) -> str:
        return f"{self.enrollment_id}"
