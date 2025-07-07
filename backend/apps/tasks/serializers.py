
from rest_framework import serializers
from .models import Category, Task

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    Converts Category model instances to JSON and vice-versa.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'usage_frequency', 'created_at']
        read_only_fields = ['usage_frequency', 'created_at'] # These fields are managed by the system

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.
    Handles serialization and deserialization of Task instances.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    # This field will display the category name when reading, but won't be used for writing.

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'priority_score', 'priority', 'deadline', 'status',
            'is_ai_suggested', 'created_at', 'updated_at'
        ]
        read_only_fields = ['priority_score', 'priority', 'is_ai_suggested', 'created_at', 'updated_at']
        # AI-related fields and timestamps are read-only as they are managed by the system or AI.

    def create(self, validated_data):
        """
        Custom create method to handle category assignment.
        """
        category_data = validated_data.pop('category', None)
        task = Task.objects.create(**validated_data)
        if category_data:
            # Assuming category_data is a Category instance from the validated data
            # If you want to create/get category by name, you'd need to adjust this.
            task.category = category_data
            task.save()
        return task

    def update(self, instance, validated_data):
        """
        Custom update method to handle category assignment and other logic.
        """
        # Handle category update if provided
        new_category = validated_data.get('category', None)
        if new_category and instance.category != new_category:
            if instance.category:
                instance.category.decrement_usage() # Decrement old category usage
            new_category.increment_usage() # Increment new category usage
            instance.category = new_category

        # Update other fields
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.deadline = validated_data.get('deadline', instance.deadline)
        instance.status = validated_data.get('status', instance.status)

        # AI-related fields are read-only, so they won't be in validated_data for direct update
        # If AI updates are needed, they should be handled by specific AI integration logic,
        # not directly through this serializer's update method.

        instance.save()
        return instance

