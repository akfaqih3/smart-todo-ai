# context/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import ContextEntry
from .serializers import ContextEntrySerializer
from apps.ai_integration.services import AIService # Import the AI Service

class ContextEntryViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing ContextEntry instances.
    Provides CRUD operations for context entries.
    Automatically processes content with AI upon creation/update.
    """
    queryset = ContextEntry.objects.all().order_by('-timestamp')
    serializer_class = ContextEntrySerializer
    # permission_classes = [permissions.IsAuthenticated] # Add permissions later if needed

    def get_queryset(self):
        """
        Optionally restricts the returned context entries to a given source type
        or within a date range.
        Example: /context/?source_type=email&start_date=2025-07-01&end_date=2025-07-07
        """
        queryset = super().get_queryset()
        source_type = self.request.query_params.get('source_type', None)
        if source_type is not None:
            queryset = queryset.filter(source_type=source_type)

        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            # Add one day to end_date to include the entire end_date
            # Or ensure the date format includes time if you want to be precise
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        """
        Override create method to analyze content with AI before saving.
        """
        instance = serializer.save() # Save the instance first to get an ID
        ai_service = AIService()
        insights = ai_service.analyze_context(instance.content)
        if insights:
            instance.processed_insights = insights
            instance.save(update_fields=['processed_insights']) # Save only the insights field
        return instance

    def perform_update(self, serializer):
        """
        Override update method to re-analyze content with AI if content changes.
        """
        instance = serializer.save() # Save the instance with updated data
        # Check if content has actually changed
        if 'content' in serializer.validated_data:
            ai_service = AIService()
            insights = ai_service.analyze_context(instance.content)
            if insights:
                instance.processed_insights = insights
                instance.save(update_fields=['processed_insights'])
        return instance

