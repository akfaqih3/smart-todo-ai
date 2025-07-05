# tasks/admin.py

from django.contrib import admin
from .models import Category, Task

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'usage_frequency', 'created_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    readonly_fields = ('usage_frequency', 'created_at') # These fields are managed by the system

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'priority', 'priority_score', 'deadline', 'status', 'is_ai_suggested', 'created_at')
    list_filter = ('status', 'priority', 'is_ai_suggested', 'category')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at' # Adds a date-based drilldown navigation
    raw_id_fields = ('category',) # For large number of categories, shows ID input instead of dropdown
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'category')
        }),
        ('AI & Priority Information', {
            'fields': ('priority_score', 'priority', 'is_ai_suggested'),
            'classes': ('collapse',) # Makes this section collapsible
        }),
        ('Status & Dates', {
            'fields': ('status', 'deadline', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at') # These fields are managed by the system

