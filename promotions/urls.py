from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, AssignmentViewSet, PlayEventViewSet

router = DefaultRouter()
router.register(r"campaigns", CampaignViewSet, basename="campaign")
router.register(r"assignments", AssignmentViewSet, basename="assignment")
router.register(r"plays", PlayEventViewSet, basename="play")

urlpatterns = router.urls