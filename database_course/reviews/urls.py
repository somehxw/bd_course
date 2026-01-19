from django.urls import path

from reviews import views


urlpatterns = [
    path("", views.ReviewCreateView.as_view(), name="review-create"),
    path("<int:review_id>/", views.ReviewDetailView.as_view(), name="review-detail"),
    path(
        "<int:review_id>/update/",
        views.ReviewUpdateView.as_view(),
        name="review-update",
    ),
    path(
        "enrollments/<int:enrollment_id>/review/",
        views.ReviewByEnrollmentView.as_view(),
        name="review-by-enrollment",
    ),
    path(
        "courses/<int:course_id>/reviews/",
        views.ReviewListView.as_view(),
        name="course-reviews",
    ),
    path(
        "courses/<int:course_id>/rating/",
        views.ReviewAggregateView.as_view(),
        name="course-rating",
    ),
]
