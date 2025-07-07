
from django.contrib import admin
from .models import ContextEntry

@admin.register(ContextEntry)
class ContextEntryAdmin(admin.ModelAdmin):
    list_display = ('content_preview', 'source_type', 'timestamp', 'created_at', 'updated_at')
    list_filter = ('source_type', 'created_at', 'timestamp')
    search_fields = ('content', 'processed_insights')
    date_hierarchy = 'timestamp'
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('content', 'source_type', 'timestamp')
        }),
        ('AI Processed Insights', {
            'fields': ('processed_insights',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def content_preview(self, obj):
        return obj.content[:75] + '...' if len(obj.content) > 75 else obj.content
    content_preview.short_description = 'Content'

