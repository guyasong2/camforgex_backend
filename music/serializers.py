from rest_framework import serializers
from .models import Track

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = "__all__"

class ProcessTrackRequestSerializer(serializers.Serializer):
    denoise = serializers.BooleanField(required=False, default=True)
    add_beats = serializers.BooleanField(required=False, default=True)
    style = serializers.ChoiceField(
        choices=["afrobeats", "hiphop", "house", "pop", "none"],
        required=False, allow_blank=True, allow_null=True, default="none"
    )
    tempo = serializers.IntegerField(required=False, min_value=60, max_value=200)
    intensity = serializers.ChoiceField(choices=["soft", "medium", "hard"], required=False, default="medium")

class TrackProcessingStatusSerializer(serializers.Serializer):
    job_id = serializers.CharField()
    status = serializers.ChoiceField(choices=["queued", "running", "succeeded", "failed"])
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    processed_file = serializers.CharField(required=False, allow_blank=True, allow_null=True)

# NEW
class JobSerializer(serializers.Serializer):
    id = serializers.CharField()
    status = serializers.ChoiceField(choices=["queued", "running", "succeeded", "failed"])
    progress = serializers.IntegerField(required=False, min_value=0, max_value=100)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    result_url = serializers.URLField(required=False, allow_blank=True, allow_null=True)