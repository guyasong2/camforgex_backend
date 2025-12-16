from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Campaign, Assignment, PlayEvent
from .serializers import CampaignSerializer, AssignmentSerializer, PlayEventSerializer

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.select_related("owner", "track").all()
    serializer_class = CampaignSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        owner = self.request.user if self.request.user.is_authenticated else None
        serializer.save(owner=owner)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def activate(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = Campaign.Status.ACTIVE
        campaign.save(update_fields=["status"])
        return Response(self.get_serializer(campaign).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def pause(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = Campaign.Status.PAUSED
        campaign.save(update_fields=["status"])
        return Response(self.get_serializer(campaign).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def end(self, request, pk=None):
        campaign = self.get_object()
        campaign.status = Campaign.Status.ENDED
        campaign.save(update_fields=["status"])
        return Response(self.get_serializer(campaign).data)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticatedOrReadOnly])
    def stats(self, request, pk=None):
        campaign = self.get_object()
        plays = PlayEvent.objects.filter(assignment__campaign=campaign).count()
        spent = float(campaign.budget - campaign.remaining_budget)
        return Response({
            "plays": plays,
            "spent": spent,
            "remaining_budget": float(campaign.remaining_budget)
        })

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related("campaign", "promoter").all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        assignment = self.get_object()
        assignment.status = Assignment.Status.ACCEPTED
        assignment.accepted_at = timezone.now()
        assignment.promoter = request.user
        assignment.save(update_fields=["status", "accepted_at", "promoter"])
        return Response(self.get_serializer(assignment).data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        assignment = self.get_object()
        assignment.status = Assignment.Status.REJECTED
        assignment.save(update_fields=["status"])
        return Response(self.get_serializer(assignment).data)

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def join(self, request):
        code = request.data.get("join_code")
        if not code:
            return Response({"detail": "join_code required"}, status=400)
        try:
            assignment = Assignment.objects.get(join_code=code)
        except Assignment.DoesNotExist:
            return Response({"detail": "Invalid join_code"}, status=404)
        assignment.status = Assignment.Status.ACCEPTED
        assignment.accepted_at = timezone.now()
        assignment.promoter = request.user
        assignment.save(update_fields=["status", "accepted_at", "promoter"])
        return Response(self.get_serializer(assignment).data)

class PlayEventViewSet(viewsets.ModelViewSet):
    queryset = PlayEvent.objects.select_related("assignment", "assignment__campaign").all()
    serializer_class = PlayEventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]