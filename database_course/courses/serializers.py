from rest_framework import serializers

from accounts.models import Teacher
from courses.models import Assignment, Course, Lesson
from dictionaries.models import AssignmentType, Category, CourseLevel, Language


class CourseCreateSerializer(serializers.ModelSerializer):
    level_id = serializers.PrimaryKeyRelatedField(
        source="level", queryset=CourseLevel.objects.all()
    )
    language_id = serializers.PrimaryKeyRelatedField(
        source="language", queryset=Language.objects.all()
    )
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all()
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        source="teacher", queryset=Teacher.objects.all()
    )

    class Meta:
        model = Course
        fields = [
            "course_id",
            "title",
            "description",
            "level_id",
            "price",
            "duration_hours",
            "language_id",
            "category_id",
            "created_at",
            "teacher_id",
        ]
        read_only_fields = ["course_id", "created_at"]


class CourseDetailSerializer(serializers.ModelSerializer):
    level_code = serializers.CharField(source="level.code", read_only=True)
    level_name = serializers.CharField(source="level.name", read_only=True)
    language_code = serializers.CharField(source="language.code", read_only=True)
    language_name = serializers.CharField(source="language.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    teacher_id = serializers.IntegerField(read_only=True)
    teacher_first_name = serializers.CharField(
        source="teacher.user.first_name", read_only=True
    )
    teacher_last_name = serializers.CharField(
        source="teacher.user.last_name", read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "course_id",
            "title",
            "description",
            "price",
            "duration_hours",
            "created_at",
            "level_code",
            "level_name",
            "language_code",
            "language_name",
            "category_name",
            "teacher_id",
            "teacher_first_name",
            "teacher_last_name",
        ]


class CourseListSerializer(serializers.ModelSerializer):
    level_code = serializers.CharField(source="level.code", read_only=True)
    language_code = serializers.CharField(source="language.code", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    teacher_first_name = serializers.CharField(
        source="teacher.user.first_name", read_only=True
    )
    teacher_last_name = serializers.CharField(
        source="teacher.user.last_name", read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "course_id",
            "title",
            "price",
            "duration_hours",
            "created_at",
            "level_code",
            "language_code",
            "category_name",
            "teacher_first_name",
            "teacher_last_name",
        ]


class CourseTeacherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["course_id", "title", "created_at", "price"]


class LessonCreateSerializer(serializers.ModelSerializer):
    course_id = serializers.PrimaryKeyRelatedField(
        source="course", queryset=Course.objects.all()
    )

    class Meta:
        model = Lesson
        fields = [
            "lesson_id",
            "course_id",
            "title",
            "content",
            "video_url",
            "duration_minutes",
            "lesson_order",
        ]
        read_only_fields = ["lesson_id"]


class LessonListSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "lesson_id",
            "course_id",
            "title",
            "video_url",
            "duration_minutes",
            "lesson_order",
        ]


class LessonDetailSerializer(serializers.ModelSerializer):
    course_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "lesson_id",
            "course_id",
            "title",
            "content",
            "video_url",
            "duration_minutes",
            "lesson_order",
        ]


class AssignmentCreateSerializer(serializers.ModelSerializer):
    lesson_id = serializers.PrimaryKeyRelatedField(
        source="lesson", queryset=Lesson.objects.all()
    )
    type_id = serializers.PrimaryKeyRelatedField(
        source="type", queryset=AssignmentType.objects.all()
    )

    class Meta:
        model = Assignment
        fields = [
            "assignment_id",
            "lesson_id",
            "title",
            "description",
            "deadline",
            "max_score",
            "type_id",
        ]
        read_only_fields = ["assignment_id"]


class AssignmentListSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField(read_only=True)
    type_code = serializers.CharField(source="type.code", read_only=True)
    type_name = serializers.CharField(source="type.name", read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "assignment_id",
            "lesson_id",
            "title",
            "deadline",
            "max_score",
            "type_code",
            "type_name",
        ]


class AssignmentDetailSerializer(serializers.ModelSerializer):
    lesson_id = serializers.IntegerField(read_only=True)
    type_code = serializers.CharField(source="type.code", read_only=True)
    type_name = serializers.CharField(source="type.name", read_only=True)

    class Meta:
        model = Assignment
        fields = [
            "assignment_id",
            "lesson_id",
            "title",
            "description",
            "deadline",
            "max_score",
            "type_code",
            "type_name",
        ]


class CourseStructureRowSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    course_title = serializers.CharField()
    lesson_id = serializers.IntegerField()
    lesson_order = serializers.IntegerField()
    lesson_title = serializers.CharField()
    assignment_id = serializers.IntegerField(allow_null=True)
    assignment_title = serializers.CharField(allow_null=True)
    deadline = serializers.DateTimeField(allow_null=True)
    max_score = serializers.IntegerField(allow_null=True)
    assignment_type = serializers.CharField(allow_null=True)
