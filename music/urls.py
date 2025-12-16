from rest_framework.routers import DefaultRouter
from .views import TrackViewSet, JobViewSet

router = DefaultRouter()
router.register(r"tracks", TrackViewSet, basename="track")
router.register(r"jobs", JobViewSet, basename="job") 

urlpatterns = router.urls