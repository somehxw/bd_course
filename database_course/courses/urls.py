from django.urls import path

from courses import views


urlpatterns = [
    path("", views.CourseCreateView.as_view(), name="course-create"),
    path("<int:course_id>/", views.CourseDetailView.as_view(), name="course-detail"),
    path(
        "<int:course_id>/update/",
        views.CourseUpdateView.as_view(),
        name="course-update",
    ),
    path(
        "<int:course_id>/delete/",
        views.CourseDeleteView.as_view(),
        name="course-delete",
    ),
    path("list/", views.CourseListView.as_view(), name="course-list"),
    path(
        "<int:course_id>/structure/",
        views.CourseStructureView.as_view(),
        name="course-structure",
    ),
    path(
        "teachers/<int:teacher_id>/courses/",
        views.CourseTeacherListView.as_view(),
        name="teacher-courses",
    ),
    path("<int:course_id>/lessons/", views.LessonListView.as_view(), name="lesson-list"),
    path("lessons/", views.LessonCreateView.as_view(), name="lesson-create"),
    path("lessons/<int:lesson_id>/", views.LessonDetailView.as_view(), name="lesson-detail"),
    path(
        "lessons/<int:lesson_id>/update/",
        views.LessonUpdateView.as_view(),
        name="lesson-update",
    ),
    path(
        "lessons/<int:lesson_id>/delete/",
        views.LessonDeleteView.as_view(),
        name="lesson-delete",
    ),
    path(
        "lessons/<int:lesson_id>/assignments/",
        views.AssignmentListView.as_view(),
        name="assignment-list",
    ),
    path("assignments/", views.AssignmentCreateView.as_view(), name="assignment-create"),
    path("assignments/<int:assignment_id>/", views.AssignmentDetailView.as_view(), name="assignment-detail"),
    path(
        "assignments/<int:assignment_id>/update/",
        views.AssignmentUpdateView.as_view(),
        name="assignment-update",
    ),
    path(
        "assignments/<int:assignment_id>/delete/",
        views.AssignmentDeleteView.as_view(),
        name="assignment-delete",
    ),
    path("analytics/", views.CourseAnalyticsView.as_view(), name="course-analytics"),
]
