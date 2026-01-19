from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response

from accounts.models import Student, Teacher, User
from accounts.serializers import (
    StudentCreateSerializer,
    StudentProfileSerializer,
    StudentUpdateSerializer,
    TeacherCreateSerializer,
    TeacherProfileSerializer,
    TeacherUpdateSerializer,
    UserCreateSerializer,
    UserListSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserStatusUpdateSerializer,
    UserUpdateSerializer,
)


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer


class UserByEmailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserLoginSerializer
    lookup_field = "email"


class UserLastLoginUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "user_id"

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.last_login = timezone.now()
        instance.save(update_fields=["last_login"])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.select_related("status")
    serializer_class = UserProfileSerializer
    lookup_field = "user_id"


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = "user_id"


class UserListView(generics.ListAPIView):
    queryset = User.objects.select_related("status").order_by("-date_registered")
    serializer_class = UserListSerializer


class UserStatusUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserStatusUpdateSerializer
    lookup_field = "user_id"


class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentCreateSerializer


class StudentDetailView(generics.RetrieveUpdateAPIView):
    queryset = Student.objects.select_related("user")
    serializer_class = StudentProfileSerializer
    lookup_field = "user_id"

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return StudentUpdateSerializer
        return super().get_serializer_class()


class TeacherCreateView(generics.CreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherCreateSerializer


class TeacherDetailView(generics.RetrieveUpdateAPIView):
    queryset = Teacher.objects.select_related("user")
    serializer_class = TeacherProfileSerializer
    lookup_field = "user_id"

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return TeacherUpdateSerializer
        return super().get_serializer_class()


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    lookup_field = "user_id"

    def perform_destroy(self, instance):
        # Удаляем связанные профили до удаления пользователя
        # Так как они используют OneToOneField, они будут удалены автоматически при удалении пользователя
        # Но сначала удалим данные, которые ссылаются на студенческий или преподавательский профиль

        # Проверяем, является ли пользователь студентом
        try:
            student_profile = instance.student_profile
            # Удаляем все записи, связанные со студентом

            # Удаляем сабмиты
            from submissions.models import Submission
            Submission.objects.filter(student=student_profile).delete()

            # Профиль студента будет удален автоматически при удалении пользователя
        except AttributeError:
            # У пользователя нет студенческого профиля
            pass

        # Проверяем, является ли пользователь преподавателем
        try:
            teacher_profile = instance.teacher_profile
            # Удаляем курсы, созданные преподавателем
            from courses.models import Course
            Course.objects.filter(teacher=teacher_profile).delete()

            # Профиль преподавателя будет удален автоматически при удалении пользователя
        except AttributeError:
            # У пользователя нет преподавательского профиля
            pass

        # Удаляем самого пользователя (и связанные OneToOne профили)
        # Оборачиваем в отдельную транзакцию для изоляции ошибки
        try:
            with transaction.atomic():
                instance.delete()
        except Exception as e:
            # Если возникает ошибка из-за таблицы отзывов или других связей, логируем и продолжаем
            # Это позволяет удалить пользователя, даже если есть проблемы с каскадным удалением
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting user {instance.user_id}: {str(e)}")
            # Попробуем удалить вручную, учитывая правильный порядок зависимостей
            from django.db import connection
            with transaction.atomic():  # Новая транзакция для ручного удаления
                with connection.cursor() as cursor:
                    # Проверяем, является ли пользователь студентом
                    try:
                        student_profile = instance.student_profile
                        # Удаляем сабмиты студента
                        cursor.execute("DELETE FROM submissions_submission WHERE student_id = %s", [instance.user_id])

                        # Удаляем энролменты студента (это может вызвать проблемы с отзывами, но мы продолжаем)
                        cursor.execute("DELETE FROM learning_enrollment WHERE student_id = %s", [instance.user_id])

                        # Удаляем студенческий профиль
                        cursor.execute("DELETE FROM accounts_student WHERE student_id = %s", [instance.user_id])
                    except AttributeError:
                        # У пользователя нет студенческого профиля
                        pass

                    # Проверяем, является ли пользователь преподавателем
                    try:
                        teacher_profile = instance.teacher_profile
                        # Удаляем курсы преподавателя
                        cursor.execute("DELETE FROM courses_course WHERE teacher_id = %s", [instance.user_id])

                        # Удаляем преподавательский профиль
                        cursor.execute("DELETE FROM accounts_teacher WHERE teacher_id = %s", [instance.user_id])
                    except AttributeError:
                        # У пользователя нет преподавательского профиля
                        pass

                    # Удаляем пользователя
                    cursor.execute("DELETE FROM accounts_user WHERE user_id = %s", [instance.user_id])
