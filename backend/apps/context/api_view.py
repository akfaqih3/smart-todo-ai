
from rest_framework import viewsets
from .models import ContextEntry
from .serializers import ContextEntrySerializer

class ContextEntryViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing ContextEntry instances.
    Provides CRUD operations for context entries.
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
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)


        if source_type is not None:
            queryset = queryset.filter(source_type=source_type)

        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
            
        if end_date:
            # Add one day to end_date to include the entire end_date
            # Or ensure the date format includes time if you want to be precise
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset

