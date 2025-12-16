from rest_framework import serializers
from .models import Campaign, Assignment, PlayEvent

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = "__all__"
        read_only_fields = ("owner", "remaining_budget", "created_at")

    def create(self, validated_data):
        if "remaining_budget" not in validated_data:
            validated_data["remaining_budget"] = validated_data.get("budget", 0)
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault("owner", request.user)
        return super().create(validated_data)

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"
        read_only_fields = ("join_code", "accepted_at", "created_at")

class PlayEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayEvent
        fields = "__all__"
        read_only_fields = ("timestamp",)

    def create(self, validated_data):
        play = super().create(validated_data)
        try:
            assignment = play.assignment
            amount = assignment.payout_per_play
            assignment.campaign.spend(amount)
        except Exception:
            pass
        return play