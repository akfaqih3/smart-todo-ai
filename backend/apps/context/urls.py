from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_view import ContextEntryViewSet

router = DefaultRouter()
router.register(r'context', ContextEntryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
