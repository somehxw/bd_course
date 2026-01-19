from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics

from learning.models import Enrollment
from learning.serializers import (
    CourseStudentListSerializer,
    EnrollmentCompleteSerializer,
    EnrollmentCreateSerializer,
    EnrollmentStatusUpdateSerializer,
    StudentCourseListSerializer,
)


class EnrollmentCreateView(generics.CreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentCreateSerializer


class EnrollmentStatusUpdateView(generics.UpdateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentStatusUpdateSerializer

    def get_object(self):
        return get_object_or_404(
            Enrollment,
            student_id=self.kwargs["student_id"],
            course_id=self.kwargs["course_id"],
        )


class EnrollmentCompleteView(generics.UpdateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentCompleteSerializer

    def get_object(self):
        return get_object_or_404(
            Enrollment,
            student_id=self.kwargs["student_id"],
            course_id=self.kwargs["course_id"],
        )

    def perform_update(self, serializer):
        serializer.save(completion_date=timezone.now())


class StudentCourseListView(generics.ListAPIView):
    serializer_class = StudentCourseListSerializer

    def get_queryset(self):
        student_id = self.kwargs["student_id"]
        return Enrollment.objects.select_related("course", "status").filter(
            student_id=student_id
        ).order_by("-enroll_date")


class CourseStudentListView(generics.ListAPIView):
    serializer_class = CourseStudentListSerializer

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        return Enrollment.objects.select_related("student__user", "status").filter(
            course_id=course_id
        ).order_by("-enroll_date")
