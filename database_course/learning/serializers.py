from rest_framework import serializers

from accounts.models import Student
from courses.models import Course
from dictionaries.models import EnrollmentStatus
from learning.models import Enrollment


class EnrollmentCreateSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        source="student", queryset=Student.objects.all()
    )
    course_id = serializers.PrimaryKeyRelatedField(
        source="course", queryset=Course.objects.all()
    )
    status_id = serializers.PrimaryKeyRelatedField(
        source="status", queryset=EnrollmentStatus.objects.all()
    )

    class Meta:
        model = Enrollment
        fields = [
            "enrollment_id",
            "student_id",
            "course_id",
            "enroll_date",
            "completion_date",
            "final_grade",
            "status_id",
        ]
        read_only_fields = ["enrollment_id", "enroll_date", "completion_date", "final_grade"]


class EnrollmentStatusUpdateSerializer(serializers.ModelSerializer):
    status_id = serializers.PrimaryKeyRelatedField(
        source="status", queryset=EnrollmentStatus.objects.all()
    )
    student_id = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["enrollment_id", "student_id", "course_id", "status_id"]
        read_only_fields = ["enrollment_id", "student_id", "course_id"]


class EnrollmentCompleteSerializer(serializers.ModelSerializer):
    status_id = serializers.PrimaryKeyRelatedField(
        source="status", queryset=EnrollmentStatus.objects.all()
    )
    student_id = serializers.IntegerField(read_only=True)
    course_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "enrollment_id",
            "student_id",
            "course_id",
            "completion_date",
            "final_grade",
            "status_id",
        ]
        read_only_fields = ["enrollment_id", "student_id", "course_id", "completion_date"]


class StudentCourseListSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(source="course.course_id", read_only=True)
    title = serializers.CharField(source="course.title", read_only=True)
    enrollment_status = serializers.CharField(source="status.code", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "enrollment_id",
            "course_id",
            "title",
            "enrollment_status",
            "enroll_date",
            "completion_date",
            "final_grade",
        ]


class CourseStudentListSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source="student.user_id", read_only=True)
    first_name = serializers.CharField(source="student.user.first_name", read_only=True)
    last_name = serializers.CharField(source="student.user.last_name", read_only=True)
    email = serializers.EmailField(source="student.user.email", read_only=True)
    enrollment_status = serializers.CharField(source="status.code", read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            "enrollment_id",
            "student_id",
            "first_name",
            "last_name",
            "email",
            "enrollment_status",
            "enroll_date",
            "completion_date",
            "final_grade",
        ]
