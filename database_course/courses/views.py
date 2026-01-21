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
    CourseAnalyticsSerializer,
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
        from django.db.models import F, Count, Avg, Sum, Case, When, IntegerField
        from learning.models import Enrollment
        from submissions.models import Submission
        from reviews.models import Review

        # Basic analytics
        total_courses = Course.objects.count()
        total_students = Student.objects.count()
        avg_price = Course.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0
        total_assignments = Assignment.objects.count()

        # Enhanced analytics
        # 1. Top performing teachers by average course ratings
        top_teachers = []
        try:
            top_teachers = Course.objects.select_related('teacher__user').values(
                'teacher_id'
            ).annotate(
                teacher_user_first_name=F('teacher__user__first_name'),
                teacher_user_last_name=F('teacher__user__last_name'),
                avg_rating=Avg('enrollments__review__rating'),
                course_count=Count('course_id')
            ).filter(
                avg_rating__isnull=False
            ).order_by('-avg_rating')[:5]
        except Exception as e:
            print(f"Error in top_teachers query: {e}")

        # 2. Most popular courses by enrollment count
        popular_courses = []
        try:
            popular_courses = Course.objects.select_related('teacher__user', 'category').values(
                'course_id',
                'title'
            ).annotate(
                teacher_user_first_name=F('teacher__user__first_name'),
                teacher_user_last_name=F('teacher__user__last_name'),
                category_name=F('category__name'),
                enrollment_count=Count('enrollments')
            ).order_by('-enrollment_count')[:5]
        except Exception as e:
            print(f"Error in popular_courses query: {e}")

        # 3. Student success rates by course completion
        course_completion_stats = []
        try:
            course_completion_stats = Enrollment.objects.values(
                'course_id'
            ).annotate(
                course_title=F('course__title'),
                total_enrollments=Count('enrollment_id'),
                completed_count=Count(Case(
                    When(final_grade__isnull=False, then=1),
                    output_field=IntegerField()
                )),
                completion_rate=Avg(Case(
                    When(final_grade__isnull=False, then=100),
                    default=0,
                    output_field=IntegerField()
                ))
            ).order_by('-completion_rate')[:5]
        except Exception as e:
            print(f"Error in course_completion_stats query: {e}")

        # 4. Assignment completion statistics
        assignment_stats = []
        try:
            assignment_stats = Assignment.objects.values(
                'lesson__course_id'
            ).annotate(
                course_title=F('lesson__course__title'),
                total_assignments=Count('assignment_id'),
                submitted_count=Count('submissions'),
                submission_rate=Avg(Case(
                    When(submissions__isnull=False, then=100),
                    default=0,
                    output_field=IntegerField()
                ))
            ).order_by('-submission_rate')
        except Exception as e:
            print(f"Error in assignment_stats query: {e}")

        # 5. Revenue analytics by course category
        revenue_by_category = []
        try:
            revenue_by_category = Course.objects.values().annotate(
                category_name=F('category__name'),
                total_revenue=Sum('price'),
                course_count=Count('course_id')
            ).order_by('-total_revenue')
        except Exception as e:
            print(f"Error in revenue_by_category query: {e}")

        # 6. Course completion rates
        overall_completion_rate = Enrollment.objects.aggregate(
            completion_percentage=Avg(Case(
                When(final_grade__isnull=False, then=100),
                default=0,
                output_field=IntegerField()
            ))
        )['completion_percentage'] or 0

        # 7. Teacher activity metrics
        teacher_activity = []
        try:
            teacher_activity = Course.objects.select_related('teacher__user').values(
                'teacher_id'
            ).annotate(
                teacher_user_first_name=F('teacher__user__first_name'),
                teacher_user_last_name=F('teacher__user__last_name'),
                course_count=Count('course_id'),
                total_students=Count('enrollments__student_id', distinct=True),
                avg_course_rating=Avg('enrollments__review__rating')
            ).order_by('-course_count')
        except Exception as e:
            print(f"Error in teacher_activity query: {e}")

        data = {
            'total_courses': total_courses,
            'total_students': total_students,
            'average_course_price': round(float(avg_price), 2),
            'total_assignments': total_assignments,

            # Enhanced analytics
            'top_teachers': list(top_teachers),
            'popular_courses': list(popular_courses),
            'course_completion_stats': list(course_completion_stats),
            'assignment_stats': list(assignment_stats),
            'revenue_by_category': list(revenue_by_category),
            'overall_completion_rate': round(float(overall_completion_rate), 2),
            'teacher_activity': list(teacher_activity),
        }

        serializer = CourseAnalyticsSerializer(data)
        return Response(serializer.data)
