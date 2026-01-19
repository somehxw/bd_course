from django.db import models


class UserStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.code}"


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.code}"


class CourseLevel(models.Model):
    level_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.code}"


class AssignmentType(models.Model):
    type_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.code}"


class EnrollmentStatus(models.Model):
    status_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.code}"


class Language(models.Model):
    language_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)

    def __str__(self) -> str:
        return f"{self.code}"


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"
