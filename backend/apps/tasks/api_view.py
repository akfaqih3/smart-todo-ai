# tasks/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer
from ai_integration.services import AIService # Import the AI Service
from django.utils import timezone # For current date in deadline suggestion

class CategoryViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing Category instances.
    Provides CRUD operations for categories.
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    # permission_classes = [permissions.IsAuthenticated] # Add permissions later if needed

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
    # permission_classes = [permissions.IsAuthenticated] # Add permissions later if needed

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

        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)

        priority_param = self.request.query_params.get('priority', None)
        if priority_param:
            queryset = queryset.filter(priority=priority_param)

        return queryset

    def perform_create(self, serializer):
        """
        Override create method to optionally apply AI suggestions upon task creation.
        AI suggestions are applied only if 'apply_ai' is True in the request data.
        """
        # Check if AI should be applied
        apply_ai = self.request.data.get('apply_ai', False)
        
        task = serializer.save() # Save the task initially

        if apply_ai:
            ai_service = AIService()

            # 1. AI Priority Suggestion
            priority_score = ai_service.get_task_priority_score(task.title, task.description)
            if priority_score is not None:
                task.set_ai_priority(priority_score) # This method also sets human-readable priority

            # 2. AI Deadline Suggestion
            suggested_deadline = ai_service.suggest_deadline(task.title, task.description, timezone.now().date())
            if suggested_deadline:
                task.deadline = suggested_deadline

            # 3. AI Category Suggestion
            suggested_categories = ai_service.suggest_categories_and_tags(task.title, task.description)
            if suggested_categories:
                # Try to assign the first suggested category if it exists or create it
                if suggested_categories:
                    first_suggested_category_name = suggested_categories[0]
                    category, created = Category.objects.get_or_create(name=first_suggested_category_name)
                    task.category = category
                    if created:
                        print(f"Created new category: {category.name}")
                    # Increment usage for the newly assigned category
                    category.increment_usage() # This is handled in Task.save() now, but good to be explicit

            # 4. AI Task Enhancement (optional, might be better as a separate action)
            # enhanced_description = ai_service.enhance_task_description(task.title, task.description)
            # if enhanced_description:
            #     task.description = enhanced_description

            task.is_ai_suggested = True # Mark as AI-processed
            task.save() # Save all AI-generated updates
        else:
            # If no AI is applied, just ensure is_ai_suggested is False
            task.is_ai_suggested = False
            task.save()

    def perform_update(self, serializer):
        """
        Override update method to potentially re-apply AI suggestions if title/description changes.
        AI suggestions are re-applied only if 'apply_ai' is True in the request data.
        """
        # Check if AI should be applied
        apply_ai = self.request.data.get('apply_ai', False)
        
        task = serializer.save() # Save the task with updated data

        if apply_ai:
            ai_service = AIService()
            re_process_ai = False

            # Check if title or description has changed, which might trigger re-processing
            if 'title' in serializer.validated_data or 'description' in serializer.validated_data:
                re_process_ai = True

            if re_process_ai:
                # Re-suggest priority
                priority_score = ai_service.get_task_priority_score(task.title, task.description)
                if priority_score is not None:
                    task.set_ai_priority(priority_score)

                # Re-suggest deadline
                suggested_deadline = ai_service.suggest_deadline(task.title, task.description, timezone.now().date())
                if suggested_deadline:
                    task.deadline = suggested_deadline

                # Re-suggest category (optional, might be disruptive if user set it manually)
                # suggested_categories = ai_service.suggest_categories_and_tags(task.title, task.description)
                # if suggested_categories:
                #     first_suggested_category_name = suggested_categories[0]
                #     category, created = Category.objects.get_or_create(name=first_suggested_category_name)
                #     task.category = category
                #     if created:
                #         print(f"Created new category on update: {category.name}")

                task.is_ai_suggested = True # Mark as AI-processed
                task.save() # Save all AI-generated updates

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

    @action(detail=True, methods=['post'], url_path='get-ai-suggestions')
    def get_ai_suggestions(self, request, pk=None):
        """
        Endpoint to trigger AI suggestions (priority, deadline, category, enhancement) for a specific task.
        """
        task = self.get_object()
        ai_service = AIService()
        response_data = {}

        # Get context insights if available (assuming we can fetch related context entries)
        context_insights = None # Placeholder for now

        # Priority
        priority_score = ai_service.get_task_priority_score(task.title, task.description, context_insights)
        if priority_score is not None:
            response_data['suggested_priority_score'] = priority_score
            # Need to get human-readable priority from score
            # This logic should ideally be in a helper or Task model method
            if priority_score >= 70:
                response_data['suggested_priority'] = 'high'
            elif priority_score >= 40:
                response_data['suggested_priority'] = 'medium'
            else:
                response_data['suggested_priority'] = 'low'

        # Deadline
        suggested_deadline = ai_service.suggest_deadline(task.title, task.description, timezone.now().date(), context_insights)
        if suggested_deadline:
            response_data['suggested_deadline'] = suggested_deadline.isoformat()

        # Categories
        suggested_categories = ai_service.suggest_categories_and_tags(task.title, task.description)
        if suggested_categories:
            response_data['suggested_categories'] = suggested_categories

        # Task Enhancement
        enhanced_description = ai_service.enhance_task_description(task.title, task.description, context_insights)
        if enhanced_description:
            response_data['enhanced_description'] = enhanced_description

        response_data['message'] = 'AI suggestions generated.'
        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='get-ai-suggestions-for-new-task')
    def get_ai_suggestions_for_new_task(self, request):
        """
        Endpoint to get AI suggestions for a new task based on provided title and description.
        Does NOT save the task.
        Expects 'title' and 'description' in request data.
        """
        title = request.data.get('title')
        description = request.data.get('description')

        if not title:
            return Response({'error': 'Title is required for AI suggestions.'}, status=status.HTTP_400_BAD_REQUEST)

        ai_service = AIService()
        response_data = {}

        # Priority
        priority_score = ai_service.get_task_priority_score(title, description)
        if priority_score is not None:
            response_data['suggested_priority_score'] = priority_score
            # Need to get human-readable priority from score
            # This logic should ideally be in a helper or Task model method
            if priority_score >= 70:
                response_data['suggested_priority'] = 'high'
            elif priority_score >= 40:
                response_data['suggested_priority'] = 'medium'
            else:
                response_data['suggested_priority'] = 'low'

        # Deadline
        suggested_deadline = ai_service.suggest_deadline(title, description, timezone.now().date())
        if suggested_deadline:
            response_data['suggested_deadline'] = suggested_deadline.isoformat()

        # Categories
        suggested_categories = ai_service.suggest_categories_and_tags(title, description)
        if suggested_categories:
            response_data['suggested_categories'] = suggested_categories

        # Task Enhancement
        enhanced_description = ai_service.enhance_task_description(title, description)
        if enhanced_description:
            response_data['enhanced_description'] = enhanced_description

        response_data['message'] = 'AI suggestions generated for new task.'
        return Response(response_data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='batch-ai-prioritization')
    def batch_ai_prioritization(self, request):
        """
        Endpoint to trigger AI prioritization for multiple tasks.
        Expects a list of task IDs in request data.
        """
        task_ids = request.data.get('task_ids', [])
        if not isinstance(task_ids, list):
            return Response({'error': 'task_ids must be a list'}, status=status.HTTP_400_BAD_REQUEST)

        ai_service = AIService()
        processed_tasks = []
        for task_id in task_ids:
            try:
                task = Task.objects.get(id=task_id)
                priority_score = ai_service.get_task_priority_score(task.title, task.description)
                if priority_score is not None:
                    task.set_ai_priority(priority_score)
                    task.is_ai_suggested = True
                    task.save()
                    processed_tasks.append(self.get_serializer(task).data)
            except Task.DoesNotExist:
                continue # Skip if task not found

        return Response({'message': f'Processed {len(processed_tasks)} tasks for AI prioritization.', 'tasks': processed_tasks}, status=status.HTTP_200_OK)

