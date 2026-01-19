from django.db import models

from accounts.models import Teacher
from dictionaries.models import AssignmentType, Category, CourseLevel, Language


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    level = models.ForeignKey(CourseLevel, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_hours = models.IntegerField(null=True, blank=True)
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, related_name="courses")

    def __str__(self) -> str:
        return self.title


class Lesson(models.Model):
    lesson_id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    lesson_order = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "lesson_order"],
                name="unique_lesson_order_per_course",
            )
        ]
        ordering = ["lesson_order"]

    def __str__(self) -> str:
        return f"{self.course_id}:{self.lesson_order}"


class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="assignments")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    max_score = models.IntegerField()
    type = models.ForeignKey(AssignmentType, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.title
