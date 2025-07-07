from django.db import models
from django.utils import timezone
from datetime import timedelta

def default_deadline():
    return timezone.now() + timedelta(days=7)

class Category(models.Model):
    """
    Represents a category or tag for tasks.
    """
    name = models.CharField(max_length=100, unique=True, help_text="The name of the category.")
    usage_frequency = models.IntegerField(default=0, help_text="How often this category is used.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time when the category was created.")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name'] # Order categories alphabetically by default

    def __str__(self):
        """
        String representation of the Category object.
        """
        return self.name

    def increment_usage(self):
        """
        Increments the usage frequency of the category.
        """
        self.usage_frequency += 1
        self.save()

    def decrement_usage(self):
        """
        Decrements the usage frequency of the category, ensuring it doesn't go below zero.
        """
        if self.usage_frequency > 0:
            self.usage_frequency -= 1
            self.save()



class Task(models.Model):
    """
    Represents a single task in the Smart Todo List application.
    """
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255, help_text="The title of the task.")
    description = models.TextField(blank=True, null=True, help_text="A detailed description of the task.")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL, # If a category is deleted, set task's category to NULL
        related_name='tasks',      # Allows accessing tasks from a category object (e.g., category.tasks.all())
        blank=True,
        null=True,
        help_text="The category or tag associated with the task."
    )
    priority_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        help_text="AI-generated priority score for the task (e.g., 0.00 to 100.00)."
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Human-readable priority level (Low, Medium, High, Urgent)."
    )
    deadline = models.DateTimeField(
        blank=True,
        null=True,
        help_text="The suggested or set deadline for the task.",
        default=default_deadline
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The current status of the task."
    )
    is_ai_suggested = models.BooleanField(
        default=False,
        help_text="Indicates if this task was suggested by the AI."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time when the task was created.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time when the task was last updated.")

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-priority_score', 'deadline', 'created_at'] # Order by priority (desc), then deadline, then creation date

    def __str__(self):
        """
        String representation of the Task object.
        """
        return self.title

    def save(self, *args, **kwargs):
        """
        Override save method to update category usage frequency.
        """
        # Handle category usage frequency when a task's category changes
        if self.pk: # If task already exists
            old_task = Task.objects.get(pk=self.pk)
            if old_task.category and old_task.category != self.category:
                old_task.category.decrement_usage()
            if self.category and old_task.category != self.category:
                self.category.increment_usage()
        elif self.category: # If new task and has a category
            self.category.increment_usage()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete method to decrement category usage frequency.
        """
        if self.category:
            self.category.decrement_usage()
        super().delete(*args, **kwargs)

    def update_status(self, new_status):
        """
        Updates the status of the task.
        """
        if new_status in [choice[0] for choice in self.STATUS_CHOICES]:
            self.status = new_status
            self.save()
            return True
        return False

    def assign_category(self, category_name):
        """
        Assigns a category to the task. Creates the category if it doesn't exist.
        """
        category, created = Category.objects.get_or_create(name=category_name)
        self.category = category
        self.save()
        return category

    def set_ai_priority(self, score):
        """
        Sets the AI-generated priority score and updates the human-readable priority.
        """
        self.priority_score = score
        if score >= 80:
            self.priority = 'urgent'
        elif score >= 60:
            self.priority = 'high'
        elif score >= 30:
            self.priority = 'medium'
        else:
            self.priority = 'low'
        self.save()