from rest_framework import serializers

from accounts.models import Student
from courses.models import Assignment
from submissions.models import Submission, SubmissionFile


class SubmissionCreateSerializer(serializers.ModelSerializer):
    assignment_id = serializers.PrimaryKeyRelatedField(
        source="assignment", queryset=Assignment.objects.all()
    )
    student_id = serializers.PrimaryKeyRelatedField(
        source="student", queryset=Student.objects.all()
    )

    class Meta:
        model = Submission
        fields = [
            "submission_id",
            "assignment_id",
            "student_id",
            "submitted_at",
            "score",
            "feedback",
        ]
        read_only_fields = ["submission_id", "submitted_at", "score", "feedback"]


class SubmissionGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ["submission_id", "score", "feedback"]
        read_only_fields = ["submission_id"]


class SubmissionDetailSerializer(serializers.ModelSerializer):
    assignment_id = serializers.IntegerField(read_only=True)
    student_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Submission
        fields = [
            "submission_id",
            "assignment_id",
            "student_id",
            "submitted_at",
            "score",
            "feedback",
        ]


class SubmissionListByAssignmentSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source="student.user_id", read_only=True)
    first_name = serializers.CharField(source="student.user.first_name", read_only=True)
    last_name = serializers.CharField(source="student.user.last_name", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "submission_id",
            "student_id",
            "first_name",
            "last_name",
            "submitted_at",
            "score",
        ]


class SubmissionCourseListSerializer(serializers.ModelSerializer):
    assignment_id = serializers.IntegerField(source="assignment.assignment_id", read_only=True)
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    lesson_id = serializers.IntegerField(source="assignment.lesson.lesson_id", read_only=True)
    lesson_order = serializers.IntegerField(
        source="assignment.lesson.lesson_order", read_only=True
    )
    course_id = serializers.IntegerField(
        source="assignment.lesson.course.course_id", read_only=True
    )
    course_title = serializers.CharField(
        source="assignment.lesson.course.title", read_only=True
    )

    class Meta:
        model = Submission
        fields = [
            "submission_id",
            "submitted_at",
            "score",
            "assignment_id",
            "assignment_title",
            "lesson_id",
            "lesson_order",
            "course_id",
            "course_title",
        ]


class SubmissionFileCreateSerializer(serializers.ModelSerializer):
    submission_id = serializers.PrimaryKeyRelatedField(
        source="submission", queryset=Submission.objects.all()
    )

    class Meta:
        model = SubmissionFile
        fields = ["file_id", "submission_id", "file_url", "uploaded_at"]
        read_only_fields = ["file_id", "uploaded_at"]


class SubmissionFileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionFile
        fields = ["file_id", "file_url", "uploaded_at"]
