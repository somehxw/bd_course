from django.urls import path

from learning import views


urlpatterns = [
    path("enrollments/", views.EnrollmentCreateView.as_view(), name="enrollment-create"),
    path(
        "enrollments/student/<int:student_id>/course/<int:course_id>/status/",
        views.EnrollmentStatusUpdateView.as_view(),
        name="enrollment-status-update",
    ),
    path(
        "enrollments/student/<int:student_id>/course/<int:course_id>/complete/",
        views.EnrollmentCompleteView.as_view(),
        name="enrollment-complete",
    ),
    path(
        "students/<int:student_id>/courses/",
        views.StudentCourseListView.as_view(),
        name="student-courses",
    ),
    path(
        "courses/<int:course_id>/students/",
        views.CourseStudentListView.as_view(),
        name="course-students",
    ),
]
