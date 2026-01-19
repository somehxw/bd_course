from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.response import Response

from reviews.models import Review
from reviews.serializers import (
    ReviewAggregateSerializer,
    ReviewCreateSerializer,
    ReviewDetailSerializer,
    ReviewListSerializer,
    ReviewUpdateSerializer,
)


class ReviewCreateView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer


class ReviewUpdateView(generics.UpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    lookup_field = "review_id"


class ReviewDetailView(generics.RetrieveAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer
    lookup_field = "review_id"


class ReviewByEnrollmentView(generics.RetrieveUpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewDetailSerializer

    def get_object(self):
        return get_object_or_404(
            Review,
            enrollment_id=self.kwargs["enrollment_id"],
        )

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return ReviewUpdateSerializer
        return super().get_serializer_class()

    def perform_update(self, serializer):
        serializer.save(created_at=timezone.now())


class ReviewListView(generics.ListAPIView):
    serializer_class = ReviewListSerializer

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        return Review.objects.select_related(
            "enrollment__student__user"
        ).filter(
            enrollment__course_id=course_id
        ).order_by("-created_at")


class ReviewAggregateView(generics.GenericAPIView):
    serializer_class = ReviewAggregateSerializer

    def get(self, request, *args, **kwargs):
        course_id = self.kwargs["course_id"]
        data = Review.objects.filter(enrollment__course_id=course_id).aggregate(
            reviews_count=Count("review_id"), avg_rating=Avg("rating")
        )
        data["reviews_count"] = int(data["reviews_count"] or 0)
        data["avg_rating"] = data["avg_rating"] or 0
        serializer = self.get_serializer(data)
        return Response(serializer.data)
