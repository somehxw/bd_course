from rest_framework import serializers

from accounts.models import Student, Teacher, User
from dictionaries.models import Role, UserStatus


class UserCreateSerializer(serializers.ModelSerializer):
    role_id = serializers.IntegerField(read_only=True)
    status_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "email",
            "password_hash",
            "first_name",
            "last_name",
            "phone",
            "role_id",
            "status_id",
            "date_registered",
            "last_login",
        ]
        read_only_fields = ["user_id", "date_registered", "last_login"]

    def create(self, validated_data):
        role, _ = Role.objects.get_or_create(
            code="student", defaults={"name": "Student"}
        )
        status, _ = UserStatus.objects.get_or_create(
            code="active", defaults={"name": "Active"}
        )
        validated_data["role"] = role
        validated_data["status"] = status
        return super().create(validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    status_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ["user_id", "email", "password_hash", "status_id"]


class UserProfileSerializer(serializers.ModelSerializer):
    status_code = serializers.CharField(source="status.code", read_only=True)
    status_name = serializers.CharField(source="status.name", read_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "status_code",
            "status_name",
            "date_registered",
            "last_login",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_id", "email", "first_name", "last_name", "phone"]
        read_only_fields = ["user_id", "email"]


class UserListSerializer(serializers.ModelSerializer):
    status_code = serializers.CharField(source="status.code", read_only=True)

    class Meta:
        model = User
        fields = [
            "user_id",
            "email",
            "first_name",
            "last_name",
            "status_code",
            "date_registered",
            "last_login",
        ]


class UserStatusUpdateSerializer(serializers.ModelSerializer):
    status_id = serializers.PrimaryKeyRelatedField(
        source="status", queryset=UserStatus.objects.all()
    )

    class Meta:
        model = User
        fields = ["user_id", "status_id"]
        read_only_fields = ["user_id"]



class StudentCreateSerializer(serializers.ModelSerializer):
    student_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all()
    )

    class Meta:
        model = Student
        fields = [
            "student_id",
            "birth_date",
            "education_level",
            "university",
            "faculty",
            "year_of_study",
            "scholarship",
        ]


class StudentProfileSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source="user_id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Student
        fields = [
            "student_id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "birth_date",
            "education_level",
            "university",
            "faculty",
            "year_of_study",
            "scholarship",
        ]


class StudentUpdateSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source="user_id", read_only=True)

    class Meta:
        model = Student
        fields = [
            "student_id",
            "birth_date",
            "education_level",
            "university",
            "faculty",
            "year_of_study",
            "scholarship",
        ]


class TeacherCreateSerializer(serializers.ModelSerializer):
    teacher_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all()
    )

    class Meta:
        model = Teacher
        fields = [
            "teacher_id",
            "academic_degree",
            "experience_years",
            "specialization",
            "bio",
        ]


class TeacherProfileSerializer(serializers.ModelSerializer):
    teacher_id = serializers.IntegerField(source="user_id", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "teacher_id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "academic_degree",
            "experience_years",
            "specialization",
            "bio",
        ]


class TeacherUpdateSerializer(serializers.ModelSerializer):
    teacher_id = serializers.IntegerField(source="user_id", read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "teacher_id",
            "academic_degree",
            "experience_years",
            "specialization",
            "bio",
        ]
