
from rest_framework import serializers
from .models import ContextEntry

class ContextEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for the ContextEntry model.
    """
    class Meta:
        model = ContextEntry
        fields = ['id', 'content', 'source_type', 'timestamp', 'processed_insights', 'created_at', 'updated_at']
        read_only_fields = ['processed_insights', 'created_at', 'updated_at'] # Insights are AI-generated
