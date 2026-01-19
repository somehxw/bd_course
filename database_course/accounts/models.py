from django.db import models

from dictionaries.models import Role, UserStatus


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    status = models.ForeignKey(UserStatus, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return self.email


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="student_id",
        related_name="student_profile",
    )
    birth_date = models.DateField(null=True, blank=True)
    education_level = models.CharField(max_length=150, blank=True)
    university = models.CharField(max_length=150, blank=True)
    faculty = models.CharField(max_length=150, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    scholarship = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"Student {self.user_id}"


class Teacher(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="teacher_id",
        related_name="teacher_profile",
    )
    academic_degree = models.CharField(max_length=150, blank=True)
    experience_years = models.IntegerField(null=True, blank=True)
    specialization = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self) -> str:
        return f"Teacher {self.user_id}"
