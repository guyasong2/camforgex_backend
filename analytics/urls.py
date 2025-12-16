from django.urls import path
from .views import MyStatsView

urlpatterns = [
    path('me/', MyStatsView.as_view(), name='my-stats'),
]