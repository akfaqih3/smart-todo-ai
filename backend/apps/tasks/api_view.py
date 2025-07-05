
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Category instances.
    Provides CRUD operations for categories.
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

    @action(detail=True, methods=['post'], url_path='increment-usage')
    def increment_usage(self, request, pk=None):
        """
        Custom action to manually increment category usage.
        (For testing or specific admin use, AI should handle this automatically)
        """
        category = self.get_object()
        category.increment_usage()
        return Response({'status': 'usage incremented'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='decrement-usage')
    def decrement_usage(self, request, pk=None):
        """
        Custom action to manually decrement category usage.
        """
        category = self.get_object()
        category.decrement_usage()
        return Response({'status': 'usage decremented'}, status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Task instances.
    Provides CRUD operations for tasks and custom actions for AI integration.
    """
    queryset = Task.objects.all().order_by('-created_at') # Default ordering
    serializer_class = TaskSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned tasks to a given category,
        by filtering against a `category_id` query parameter in the URL.
        Example: /tasks/?category_id=1
        """
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id', None)
        if category_id is not None:
            queryset = queryset.filter(category__id=category_id)

        # Add filtering by status, priority, etc. as needed
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        priority_param = self.request.query_params.get('priority', None)
        if priority_param:
            queryset = queryset.filter(priority=priority_param)

        return queryset

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        Marks a task as completed.
        """
        task = self.get_object()
        if task.update_status('completed'):
            return Response({'status': 'task completed'}, status=status.HTTP_200_OK)
        return Response({'error': 'Could not complete task'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='set-priority')
    def set_priority(self, request, pk=None):
        """
        Sets the AI-generated priority score for a task.
        Expects 'score' in request data.
        """
        task = self.get_object()
        score = request.data.get('score')
        if score is not None:
            try:
                score = float(score)
                task.set_ai_priority(score)
                return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)
            except ValueError:
                return Response({'error': 'Score must be a number'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Score is required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='assign-category-by-name')
    def assign_category_by_name(self, request, pk=None):
        """
        Assigns a category to a task by category name.
        Creates the category if it doesn't exist.
        Expects 'category_name' in request data.
        """
        task = self.get_object()
        category_name = request.data.get('category_name')
        if category_name:
            task.assign_category(category_name)
            return Response(self.get_serializer(task).data, status=status.HTTP_200_OK)
        return Response({'error': 'Category name is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Placeholder for AI integration actions (will be implemented in AI module)
    @action(detail=True, methods=['post'], url_path='get-ai-suggestions')
    def get_ai_suggestions(self, request, pk=None):
        """
        Endpoint to trigger AI suggestions for a specific task.
        This will be handled by the AI Integration Module.
        """
        task = self.get_object()
        # Here you would call your AI integration module
        # For now, just a placeholder response
        return Response({'message': f'AI suggestions requested for task: {task.title}'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='batch-ai-prioritization')
    def batch_ai_prioritization(self, request):
        """
        Endpoint to trigger AI prioritization for multiple tasks.
        This will be handled by the AI Integration Module.
        Expects a list of task IDs in request data.
        """
        task_ids = request.data.get('task_ids', [])
        if not isinstance(task_ids, list):
            return Response({'error': 'task_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        # Here you would call your AI integration module to process these tasks
        # For now, just a placeholder response
        return Response({'message': f'AI batch prioritization requested for tasks: {task_ids}'}, status=status.HTTP_200_OK)

