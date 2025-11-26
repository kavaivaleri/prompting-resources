from django.contrib import admin
from .models import Todo


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'due_date', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'due_date', 'created_at']
    search_fields = ['title', 'description']
    date_hierarchy = 'due_date'
