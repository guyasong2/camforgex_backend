from rest_framework import serializers

class MyStatsSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['ARTIST', 'PROMOTER'])
    tracks = serializers.IntegerField(required=False)
    campaigns = serializers.IntegerField(required=False)
    total_plays = serializers.IntegerField(required=False)
    spent = serializers.CharField(required=False)  
    my_plays = serializers.IntegerField(required=False)