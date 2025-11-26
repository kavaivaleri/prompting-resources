from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import Todo


class TodoForm(forms.ModelForm):
    quick_date = forms.ChoiceField(
        choices=[
            ('', 'Select quick date...'),
            ('today', 'Today'),
            ('tomorrow', 'Tomorrow'),
            ('custom', 'Custom date'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'quick-date-select'})
    )
    
    quick_time = forms.ChoiceField(
        choices=[
            ('09:00', '9:00 AM'),
            ('12:00', '12:00 PM (Noon)'),
            ('17:00', '5:00 PM'),
            ('20:00', '8:00 PM'),
            ('23:59', '11:59 PM (End of day)'),
            ('custom', 'Custom time'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'quick-time-select'})
    )
    
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'is_resolved']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter TODO title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter description (optional)'}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'id': 'due-date-input'}),
            'is_resolved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial quick_date based on existing due_date
        if self.instance and self.instance.pk and self.instance.due_date:
            today = timezone.now().date()
            tomorrow = today + timedelta(days=1)
            todo_date = self.instance.due_date.date()
            if todo_date == today:
                self.fields['quick_date'].initial = 'today'
            elif todo_date == tomorrow:
                self.fields['quick_date'].initial = 'tomorrow'
            else:
                self.fields['quick_date'].initial = 'custom'

