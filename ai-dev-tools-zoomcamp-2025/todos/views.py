from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Todo
from .forms import TodoForm


def todo_list(request):
    todos = Todo.objects.all()
    return render(request, 'todos/todo_list.html', {'todos': todos})


def todo_create(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            # Handle quick date selection if due_date is not set
            if not todo.due_date:
                quick_date = form.cleaned_data.get('quick_date')
                quick_time = form.cleaned_data.get('quick_time')
                
                if quick_date == 'today':
                    date = timezone.now().date()
                elif quick_date == 'tomorrow':
                    date = (timezone.now() + timedelta(days=1)).date()
                else:
                    date = None
                
                if date:
                    # Parse time
                    if quick_time and quick_time != 'custom':
                        time_str = quick_time
                    else:
                        time_str = '12:00'  # Default to noon
                    
                    # Combine date and time
                    datetime_str = f"{date} {time_str}:00"
                    todo.due_date = timezone.make_aware(
                        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                    )
            
            todo.save()
            messages.success(request, 'TODO created successfully!')
            return redirect('todo_list')
    else:
        form = TodoForm()
    return render(request, 'todos/todo_form.html', {'form': form, 'action': 'Create'})


def todo_edit(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            todo = form.save(commit=False)
            # Handle quick date selection if due_date is not set or was cleared
            if not todo.due_date:
                quick_date = form.cleaned_data.get('quick_date')
                quick_time = form.cleaned_data.get('quick_time')
                
                if quick_date == 'today':
                    date = timezone.now().date()
                elif quick_date == 'tomorrow':
                    date = (timezone.now() + timedelta(days=1)).date()
                else:
                    date = None
                
                if date:
                    # Parse time
                    if quick_time and quick_time != 'custom':
                        time_str = quick_time
                    else:
                        time_str = '12:00'  # Default to noon
                    
                    # Combine date and time
                    datetime_str = f"{date} {time_str}:00"
                    todo.due_date = timezone.make_aware(
                        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
                    )
            
            todo.save()
            messages.success(request, 'TODO updated successfully!')
            return redirect('todo_list')
    else:
        form = TodoForm(instance=todo)
    return render(request, 'todos/todo_form.html', {'form': form, 'todo': todo, 'action': 'Edit'})


def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == 'POST':
        todo.delete()
        messages.success(request, 'TODO deleted successfully!')
        return redirect('todo_list')
    return render(request, 'todos/todo_confirm_delete.html', {'todo': todo})


def todo_toggle_resolved(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.is_resolved = not todo.is_resolved
    todo.save()
    status = 'resolved' if todo.is_resolved else 'unresolved'
    messages.success(request, f'TODO marked as {status}!')
    return redirect('todo_list')
