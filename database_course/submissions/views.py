from rest_framework import generics

from submissions.models import Submission, SubmissionFile
from submissions.serializers import (
    SubmissionCourseListSerializer,
    SubmissionCreateSerializer,
    SubmissionDetailSerializer,
    SubmissionFileCreateSerializer,
    SubmissionFileListSerializer,
    SubmissionGradeSerializer,
    SubmissionListByAssignmentSerializer,
)


class SubmissionCreateView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionCreateSerializer


class SubmissionGradeUpdateView(generics.UpdateAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionGradeSerializer
    lookup_field = "submission_id"


class SubmissionDetailView(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionDetailSerializer
    lookup_field = "submission_id"


class SubmissionListByAssignmentView(generics.ListAPIView):
    serializer_class = SubmissionListByAssignmentSerializer

    def get_queryset(self):
        assignment_id = self.kwargs["assignment_id"]
        return Submission.objects.select_related("student__user").filter(
            assignment_id=assignment_id
        ).order_by("-submitted_at")


class SubmissionCourseListView(generics.ListAPIView):
    serializer_class = SubmissionCourseListSerializer

    def get_queryset(self):
        student_id = self.kwargs["student_id"]
        course_id = self.kwargs["course_id"]
        return (
            Submission.objects.select_related(
                "assignment__lesson__course",
                "assignment__lesson",
                "assignment",
            )
            .filter(student_id=student_id, assignment__lesson__course_id=course_id)
            .order_by("assignment__lesson__lesson_order", "-submitted_at")
        )


class SubmissionFileCreateView(generics.CreateAPIView):
    queryset = SubmissionFile.objects.all()
    serializer_class = SubmissionFileCreateSerializer


class SubmissionFileListView(generics.ListAPIView):
    serializer_class = SubmissionFileListSerializer

    def get_queryset(self):
        submission_id = self.kwargs["submission_id"]
        return SubmissionFile.objects.filter(submission_id=submission_id).order_by(
            "uploaded_at"
        )


class SubmissionFileDeleteView(generics.DestroyAPIView):
    queryset = SubmissionFile.objects.all()
    lookup_field = "file_id"
