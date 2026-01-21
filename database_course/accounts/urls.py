from django.urls import path

from accounts import views


urlpatterns = [
    path("users/", views.UserCreateView.as_view(), name="user-create"),
    path("users/list/", views.UserListView.as_view(), name="user-list"),
    path("users/by-email/<str:email>/", views.UserByEmailView.as_view(), name="user-by-email"),
    path(
        "users/<int:user_id>/last-login/",
        views.UserLastLoginUpdateView.as_view(),
        name="user-last-login",
    ),
    path("users/<int:user_id>/", views.UserProfileView.as_view(), name="user-profile"),
    path(
        "users/<int:user_id>/update/",
        views.UserUpdateView.as_view(),
        name="user-update",
    ),
    path(
        "users/<int:user_id>/status/",
        views.UserStatusUpdateView.as_view(),
        name="user-status-update",
    ),
    path(
        "users/<int:user_id>/delete/",
        views.UserDeleteView.as_view(),
        name="user-delete",
    ),
    path("students/", views.StudentCreateView.as_view(), name="student-create"),
    path(
        "students/<int:user_id>/",
        views.StudentDetailView.as_view(),
        name="student-detail",
    ),
    path("teachers/", views.TeacherCreateView.as_view(), name="teacher-create"),
    path(
        "teachers/<int:user_id>/",
        views.TeacherDetailView.as_view(),
        name="teacher-detail",
    ),
    path(
        "students/<int:user_id>/report/",
        views.StudentReportView.as_view(),
        name="student-report",
    ),
]
