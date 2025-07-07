
from django.db import models
from django.utils import timezone

class ContextEntry(models.Model):
    """
    Represents a single daily context entry (e.g., message, email, note).
    """
    SOURCE_TYPE_CHOICES = [
        ('whatsapp', 'WhatsApp Message'),
        ('email', 'Email'),
        ('note', 'Note'),
        ('other', 'Other'),
    ]

    content = models.TextField(help_text="The raw content of the context entry.")
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='note',
        help_text="The type of the context source (e.g., WhatsApp, Email, Note)."
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="The original timestamp of the context entry."
    )
    processed_insights = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON field to store AI-processed insights (e.g., keywords, sentiment, entities)."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time when the entry was created in the system.")
    updated_at = models.DateTimeField(auto_now=True, help_text="The date and time when the entry was last updated.")

    class Meta:
        verbose_name = "Context Entry"
        verbose_name_plural = "Context Entries"
        ordering = ['-timestamp'] # Order by most recent context first

    def __str__(self):
        """
        String representation of the ContextEntry object.
        """
        return f"{self.source_type.capitalize()} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}: {self.content[:50]}..."

    def save(self, *args, **kwargs):
        """
        Override save method to ensure timestamp is set if not provided.
        """
        if not self.timestamp:
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)

    def add_insight(self, key, value):
        """
        Adds or updates a specific insight in the processed_insights JSON field.
        """
        if not self.processed_insights:
            self.processed_insights = {}
        self.processed_insights[key] = value
        self.save()

    def get_insight(self, key):
        """
        Retrieves a specific insight from the processed_insights JSON field.
        """
        if self.processed_insights:
            return self.processed_insights.get(key)
        return None

