from django.urls import path

from submissions import views


urlpatterns = [
    path("", views.SubmissionCreateView.as_view(), name="submission-create"),
    path(
        "<int:submission_id>/",
        views.SubmissionDetailView.as_view(),
        name="submission-detail",
    ),
    path(
        "<int:submission_id>/grade/",
        views.SubmissionGradeUpdateView.as_view(),
        name="submission-grade",
    ),
    path(
        "assignments/<int:assignment_id>/submissions/",
        views.SubmissionListByAssignmentView.as_view(),
        name="assignment-submissions",
    ),
    path(
        "students/<int:student_id>/courses/<int:course_id>/submissions/",
        views.SubmissionCourseListView.as_view(),
        name="student-course-submissions",
    ),
    path(
        "files/",
        views.SubmissionFileCreateView.as_view(),
        name="submission-file-create",
    ),
    path(
        "<int:submission_id>/files/",
        views.SubmissionFileListView.as_view(),
        name="submission-files",
    ),
    path(
        "files/<int:file_id>/delete/",
        views.SubmissionFileDeleteView.as_view(),
        name="submission-file-delete",
    ),
]
