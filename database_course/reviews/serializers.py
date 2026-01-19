from rest_framework import serializers

from learning.models import Enrollment
from reviews.models import Review


class ReviewCreateSerializer(serializers.ModelSerializer):
    enrollment_id = serializers.PrimaryKeyRelatedField(
        source="enrollment", queryset=Enrollment.objects.all()
    )

    class Meta:
        model = Review
        fields = [
            "review_id",
            "enrollment_id",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["review_id", "created_at"]


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["review_id", "enrollment_id", "rating", "comment", "created_at"]
        read_only_fields = ["review_id", "enrollment_id", "created_at"]


class ReviewDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["review_id", "enrollment_id", "rating", "comment", "created_at"]


class ReviewListSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source="enrollment.student.user.first_name", read_only=True
    )
    last_name = serializers.CharField(
        source="enrollment.student.user.last_name", read_only=True
    )

    class Meta:
        model = Review
        fields = [
            "review_id",
            "enrollment_id",
            "rating",
            "comment",
            "created_at",
            "first_name",
            "last_name",
        ]


class ReviewAggregateSerializer(serializers.Serializer):
    reviews_count = serializers.IntegerField()
    avg_rating = serializers.DecimalField(max_digits=10, decimal_places=2)
