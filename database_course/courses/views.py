from django.db.models import F, Count, Avg, Sum
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Student
from courses.models import Assignment, Course, Lesson
from courses.serializers import (
    AssignmentCreateSerializer,
    AssignmentDetailSerializer,
    AssignmentListSerializer,
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseStructureRowSerializer,
    CourseTeacherListSerializer,
    LessonCreateSerializer,
    LessonDetailSerializer,
    LessonListSerializer,
)


class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer


class CourseUpdateView(generics.UpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseCreateSerializer
    lookup_field = "course_id"


class CourseDeleteView(generics.DestroyAPIView):
    queryset = Course.objects.all()
    lookup_field = "course_id"


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.select_related(
        "level", "language", "category", "teacher__user"
    )
    serializer_class = CourseDetailSerializer
    lookup_field = "course_id"


class CourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer

    def get_queryset(self):
        queryset = Course.objects.select_related(
            "level", "language", "category", "teacher__user"
        ).order_by("-created_at")
        category_id = self.request.query_params.get("category_id")
        level_id = self.request.query_params.get("level_id")
        language_id = self.request.query_params.get("language_id")
        teacher_id = self.request.query_params.get("teacher_id")
        teacher_full_name = self.request.query_params.get("teacher_full_name")

        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if level_id:
            queryset = queryset.filter(level_id=level_id)
        if language_id:
            queryset = queryset.filter(language_id=language_id)
        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)
        if teacher_full_name:
            queryset = queryset.filter(
                teacher__user__first_name__icontains=teacher_full_name
            ) | queryset.filter(
                teacher__user__last_name__icontains=teacher_full_name
            )
        return queryset


class CourseTeacherListView(generics.ListAPIView):
    serializer_class = CourseTeacherListSerializer

    def get_queryset(self):
        teacher_id = self.kwargs["teacher_id"]
        return Course.objects.filter(teacher_id=teacher_id).order_by("-created_at")


class LessonCreateView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonCreateSerializer


class LessonUpdateView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonCreateSerializer
    lookup_field = "lesson_id"


class LessonDeleteView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    lookup_field = "lesson_id"


class LessonListView(generics.ListAPIView):
    serializer_class = LessonListSerializer

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        return Lesson.objects.filter(course_id=course_id).order_by("lesson_order")


class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonDetailSerializer
    lookup_field = "lesson_id"


class AssignmentCreateView(generics.CreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentCreateSerializer


class AssignmentUpdateView(generics.UpdateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentCreateSerializer
    lookup_field = "assignment_id"


class AssignmentDeleteView(generics.DestroyAPIView):
    queryset = Assignment.objects.all()
    lookup_field = "assignment_id"


class AssignmentListView(generics.ListAPIView):
    serializer_class = AssignmentListSerializer

    def get_queryset(self):
        lesson_id = self.kwargs["lesson_id"]
        return Assignment.objects.select_related("type").filter(lesson_id=lesson_id).order_by(
            "assignment_id"
        )


class AssignmentDetailView(generics.RetrieveAPIView):
    queryset = Assignment.objects.select_related("type")
    serializer_class = AssignmentDetailSerializer
    lookup_field = "assignment_id"


class CourseStructureView(generics.ListAPIView):
    serializer_class = CourseStructureRowSerializer

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        return (
            Lesson.objects.filter(course_id=course_id)
            .annotate(
                course_id=F("course__course_id"),
                course_title=F("course__title"),
                lesson_title=F("title"),
                assignment_id=F("assignments__assignment_id"),
                assignment_title=F("assignments__title"),
                deadline=F("assignments__deadline"),
                max_score=F("assignments__max_score"),
                assignment_type=F("assignments__type__code"),
            )
            .values(
                "course_id",
                "course_title",
                "lesson_id",
                "lesson_order",
                "lesson_title",
                "assignment_id",
                "assignment_title",
                "deadline",
                "max_score",
                "assignment_type",
            )
            .order_by("lesson_order", "assignment_id")
        )


class CourseAnalyticsView(APIView):
    """
    View to provide analytics and aggregations for the course platform.
    """

    def get(self, request, *args, **kwargs):
        # 1. Total number of courses
        total_courses = Course.objects.count()

        # 2. Total number of students
        total_students = Student.objects.count()

        # 3. Average course price
        avg_price = Course.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0

        # 4. Count of active assignments (assignments that belong to lessons in courses)
        total_assignments = Assignment.objects.count()

        data = {
            'total_courses': total_courses,
            'total_students': total_students,
            'average_course_price': round(float(avg_price), 2),
            'total_assignments': total_assignments,
        }

        return Response(data)
