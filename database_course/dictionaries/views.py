from rest_framework import generics

from dictionaries.models import (
    AssignmentType,
    Category,
    CourseLevel,
    EnrollmentStatus,
    Language,
    UserStatus,
)
from dictionaries.serializers import (
    AssignmentTypeSerializer,
    CategorySerializer,
    CourseLevelSerializer,
    EnrollmentStatusSerializer,
    LanguageSerializer,
    UserStatusSerializer,
)


class UserStatusListView(generics.ListAPIView):
    queryset = UserStatus.objects.all().order_by("status_id")
    serializer_class = UserStatusSerializer


class CourseLevelListView(generics.ListAPIView):
    queryset = CourseLevel.objects.all().order_by("level_id")
    serializer_class = CourseLevelSerializer


class AssignmentTypeListView(generics.ListAPIView):
    queryset = AssignmentType.objects.all().order_by("type_id")
    serializer_class = AssignmentTypeSerializer


class EnrollmentStatusListView(generics.ListAPIView):
    queryset = EnrollmentStatus.objects.all().order_by("status_id")
    serializer_class = EnrollmentStatusSerializer


class LanguageListView(generics.ListAPIView):
    queryset = Language.objects.all().order_by("language_id")
    serializer_class = LanguageSerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
