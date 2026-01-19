from django.urls import path

from dictionaries import views


urlpatterns = [
    path("user-statuses/", views.UserStatusListView.as_view(), name="user-statuses-list"),
    path("course-levels/", views.CourseLevelListView.as_view(), name="course-levels-list"),
    path("assignment-types/", views.AssignmentTypeListView.as_view(), name="assignment-types-list"),
    path(
        "enrollment-statuses/",
        views.EnrollmentStatusListView.as_view(),
        name="enrollment-statuses-list",
    ),
    path("languages/", views.LanguageListView.as_view(), name="languages-list"),
    path("categories/", views.CategoryListView.as_view(), name="categories-list"),
]
