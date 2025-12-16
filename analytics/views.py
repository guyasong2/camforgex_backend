from decimal import Decimal
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from promotions.models import Campaign, PlayEvent
from music.models import Track
from .serializers import MyStatsSerializer

from decimal import Decimal
from django.db.models import F, Sum, DecimalField

class MyStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Analytics'],
        summary='Get statistics for the authenticated user',
        responses=MyStatsSerializer,
        examples=[
            OpenApiExample(
                'Artist stats',
                value={'role': 'ARTIST', 'tracks': 5, 'campaigns': 2, 'total_plays': 1234, 'spent': '47.50'},
                response_only=True
            ),
            OpenApiExample(
                'Promoter stats',
                value={'role': 'PROMOTER', 'my_plays': 987},
                response_only=True
            ),
        ],
    )
    def get(self, request):
        if request.user.role == 'ARTIST':
            track_count = Track.objects.filter(owner=request.user).count()
            campaigns = Campaign.objects.filter(owner=request.user)
            total_plays = PlayEvent.objects.filter(assignment__campaign__in=campaigns).count()
            agg = campaigns.aggregate(
            spent=Sum(F('budget') - F('remaining_budget'), output_field=DecimalField(max_digits=12, decimal_places=2))
            )
            spent = agg['spent'] or Decimal('0')

            data = {
                'role': 'ARTIST',
                'tracks': track_count,
                'campaigns': campaigns.count(),
                'total_plays': total_plays,
                'spent': str(spent),
            }
        else:
            total_plays = PlayEvent.objects.filter(assignment__promoter=request.user).count()
            data = {'role': 'PROMOTER', 'my_plays': total_plays}
        return Response(data)