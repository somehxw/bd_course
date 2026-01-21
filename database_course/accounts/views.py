from django.db import transaction
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime
from django.http import HttpResponse

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


from rest_framework.views import APIView
from django.http import Http404


class StudentReportView(APIView):
    """
    Generates PDF report for a student.
    Only the student himself or an administrator can access this report.
    """
    def get(self, request, user_id):
        # Get the student
        try:
            student = Student.objects.select_related('user').get(user_id=user_id)
        except Student.DoesNotExist:
            raise Http404("Student not found")

        # Check access rights
        current_user_id = request.query_params.get('current_user_id')
        current_user_email = getattr(request.user, 'email', None)

        if not current_user_id or (int(current_user_id) != student.user_id and current_user_email != 'admin@example.com'):
            return Response({'error': 'Access denied'}, status=status.HTTP_403_FORBIDDEN)

        # Create buffer for PDF
        buffer = io.BytesIO()

        # Prepare text in English
        report_title = "Student Report"
        name_label = "Name:"
        email_label = "Email:"
        birth_date_label = "Birth Date:"
        education_level_label = "Education Level:"
        university_label = "University:"
        faculty_label = "Faculty:"
        year_of_study_label = "Year of Study:"
        scholarship_label = "Scholarship:"
        yes_text = "Yes"
        no_text = "No"
        enrolled_courses_label = "Enrolled Courses:"
        generated_label = "Report Generated:"
        generated_by_label = "Generated By:"
        anonymous_user_text = "Anonymous User"

        # Register Cyrillic font
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        import os

        # Try to use Liberation Sans font, which usually supports Cyrillic
        # or specify a path to a system font
        try:
            # Try to register a font with Cyrillic support
            # Use a font that is typically available in systems
            font_name = "DejaVuSans"
            pdfmetrics.registerFont(TTFont(font_name, "DejaVuSans.ttf"))
            pdfmetrics.registerFont(TTFont(font_name + "-Bold", "DejaVuSans-Bold.ttf"))
            pdfmetrics.registerFont(TTFont(font_name + "-Oblique", "DejaVuSans-Oblique.ttf"))
        except:
            # If font is not found, we will use standard fonts
            # and replace Cyrillic characters with transliteration
            font_name = "Helvetica"

            # Transliteration of Cyrillic strings (for Ukrainian alphabet)
            def transliterate(text):
                if isinstance(text, str):
                    # Ukrainian alphabet considering peculiarities
                    cyrillic_to_latin = {
                        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'h', 'ґ': 'g', 'д': 'd', 'е': 'e',
                        'є': 'ie', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'yi', 'й': 'i',
                        'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
                        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
                        'ш': 'sh', 'щ': 'shch', 'ь': "'", 'ю': 'iu', 'я': 'ia',
                        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'H', 'Ґ': 'G', 'Д': 'D', 'Е': 'E',
                        'Є': 'Ye', 'Ж': 'Zh', 'З': 'Z', 'И': 'Y', 'І': 'I', 'Ї': 'Yi', 'Й': 'Y',
                        'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R',
                        'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch',
                        'Ш': 'Sh', 'Щ': 'Shch', 'Ь': "'", 'Ю': 'Iu', 'Я': 'Ia',
                        ' ': ' ', '.': '.', ',': ',', '!': '!', '?': '?', '-': '-',
                        '«': '"', '»': '"', '(': '(', ')': ')', ':': ':', ';': ';', '…': '...'
                    }
                    result = ""
                    for char in text:
                        result += cyrillic_to_latin.get(char, char)
                    return result

            # Apply transliteration to our strings
            report_title = transliterate(report_title)
            name_label = transliterate(name_label)
            email_label = transliterate(email_label)
            birth_date_label = transliterate(birth_date_label)
            education_level_label = transliterate(education_level_label)
            university_label = transliterate(university_label)
            faculty_label = transliterate(faculty_label)
            year_of_study_label = transliterate(year_of_study_label)
            scholarship_label = transliterate(scholarship_label)
            yes_text = transliterate(yes_text)
            no_text = transliterate(no_text)
            enrolled_courses_label = transliterate(enrolled_courses_label)
            generated_label = transliterate(generated_label)
            generated_by_label = transliterate(generated_by_label)
            anonymous_user_text = transliterate(anonymous_user_text)

            # Also transliterate student data
            student.user.first_name = transliterate(student.user.first_name)
            student.user.last_name = transliterate(student.user.last_name)
            student.education_level = transliterate(student.education_level)
            student.university = transliterate(student.university)
            student.faculty = transliterate(student.faculty)

        # Создаем PDF
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Заголовок
        p.setFont(font_name + "-Bold" if font_name != "Helvetica" else "Helvetica-Bold", 16)
        p.drawString(50, height - 50, report_title)

        # Information about the student
        p.setFont(font_name, 12)
        y_position = height - 100

        p.drawString(50, y_position, f"{name_label} {student.user.first_name} {student.user.last_name}")
        y_position -= 20
        p.drawString(50, y_position, f"{email_label} {student.user.email}")
        y_position -= 20
        p.drawString(50, y_position, f"{birth_date_label} {student.birth_date}")
        y_position -= 20
        p.drawString(50, y_position, f"{education_level_label} {student.education_level}")
        y_position -= 20
        p.drawString(50, y_position, f"{university_label} {student.university}")
        y_position -= 20
        p.drawString(50, y_position, f"{faculty_label} {student.faculty}")
        y_position -= 20
        p.drawString(50, y_position, f"{year_of_study_label} {student.year_of_study}")
        y_position -= 20
        p.drawString(50, y_position, f"{scholarship_label} {yes_text if student.scholarship else no_text}")
        y_position -= 30

        # Add information about courses the student is enrolled in
        p.drawString(50, y_position, enrolled_courses_label)
        y_position -= 20

        from learning.models import Enrollment
        from courses.models import Course
        enrollments = Enrollment.objects.filter(student=student).select_related('course', 'status')

        for enrollment in enrollments:
            course_title = str(enrollment.course.title)
            status_name = str(enrollment.status.name)
            # Применяем транслитерацию к названиям курсов и статусов, если используется транслит
            if font_name == "Helvetica":
                course_title = transliterate(course_title)
                status_name = transliterate(status_name)

            p.drawString(70, y_position, f"- {course_title} ({status_name})")
            y_position -= 15
            if y_position < 100:  # If there's not enough space, create a new page
                p.showPage()
                y_position = height - 50

        y_position -= 20

        # Add the requested metadata below the main content
        # Move to a new page if there's not enough space
        if y_position < 100:
            p.showPage()
            y_position = height - 50

        # Add the report generation metadata in the requested format (italic, smaller font)
        p.setFont(font_name + "-Oblique" if font_name != "Helvetica" else "Helvetica-Oblique", 10)
        p.drawString(50, y_position, f"{generated_label} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        y_position -= 15
        current_user_email = transliterate(request.user.email) if font_name == "Helvetica" and hasattr(request.user, 'email') and request.user.email else getattr(request.user, 'email', '')
        p.drawString(50, y_position, f"{generated_by_label} {current_user_email if hasattr(request.user, 'email') and request.user.email else anonymous_user_text}")

        # Save PDF
        p.save()

        # Get value from buffer
        pdf = buffer.getvalue()
        buffer.close()

        # Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="student_report_{user_id}.pdf"'
        return response
