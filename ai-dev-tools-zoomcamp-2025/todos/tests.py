from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Todo
from .forms import TodoForm


class TodoModelTest(TestCase):
    """Test cases for the Todo model"""
    
    def test_create_todo_with_required_fields(self):
        """Test creating a TODO with only required fields"""
        todo = Todo.objects.create(title="Test TODO")
        self.assertEqual(todo.title, "Test TODO")
        self.assertFalse(todo.is_resolved)
        self.assertIsNone(todo.due_date)
        self.assertEqual(todo.description, "")
    
    def test_create_todo_with_all_fields(self):
        """Test creating a TODO with all fields"""
        due_date = timezone.now() + timedelta(days=1)
        todo = Todo.objects.create(
            title="Complete project",
            description="Finish the Django project",
            due_date=due_date,
            is_resolved=True
        )
        self.assertEqual(todo.title, "Complete project")
        self.assertEqual(todo.description, "Finish the Django project")
        self.assertEqual(todo.due_date, due_date)
        self.assertTrue(todo.is_resolved)
    
    def test_todo_str_representation(self):
        """Test the string representation of Todo"""
        todo = Todo.objects.create(title="My TODO")
        self.assertEqual(str(todo), "My TODO")
    
    def test_todo_default_values(self):
        """Test default values for Todo fields"""
        todo = Todo.objects.create(title="Test")
        self.assertFalse(todo.is_resolved)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)
    
    def test_todo_ordering(self):
        """Test that TODOs are ordered by newest first"""
        todo1 = Todo.objects.create(title="First TODO")
        todo2 = Todo.objects.create(title="Second TODO")
        todos = list(Todo.objects.all())
        self.assertEqual(todos[0], todo2)  # Newest first
        self.assertEqual(todos[1], todo1)


class TodoListViewTest(TestCase):
    """Test cases for the todo list view"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('todo_list')
    
    def test_list_view_returns_200(self):
        """Test that list view returns 200 status code"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_list_view_with_empty_list(self):
        """Test list view with no TODOs"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['todos'], [])
    
    def test_list_view_displays_todos(self):
        """Test that list view displays all TODOs"""
        todo1 = Todo.objects.create(title="TODO 1")
        todo2 = Todo.objects.create(title="TODO 2")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(todo1, response.context['todos'])
        self.assertIn(todo2, response.context['todos'])


class TodoCreateViewTest(TestCase):
    """Test cases for the todo create view"""
    
    def setUp(self):
        self.client = Client()
        self.url = reverse('todo_create')
    
    def test_create_view_get(self):
        """Test GET request to create view"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], TodoForm)
        self.assertEqual(response.context['action'], 'Create')
    
    def test_create_todo_with_valid_data(self):
        """Test creating a TODO with valid data"""
        data = {
            'title': 'New TODO',
            'description': 'Test description',
            'is_resolved': False
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(Todo.objects.filter(title='New TODO').exists())
    
    def test_create_todo_with_quick_date_today(self):
        """Test creating a TODO with quick_date='today'"""
        data = {
            'title': 'Today TODO',
            'quick_date': 'today',
            'quick_time': '12:00'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        todo = Todo.objects.get(title='Today TODO')
        self.assertIsNotNone(todo.due_date)
        self.assertEqual(todo.due_date.date(), timezone.now().date())
    
    def test_create_todo_with_quick_date_tomorrow(self):
        """Test creating a TODO with quick_date='tomorrow'"""
        data = {
            'title': 'Tomorrow TODO',
            'quick_date': 'tomorrow',
            'quick_time': '17:00'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        todo = Todo.objects.get(title='Tomorrow TODO')
        self.assertIsNotNone(todo.due_date)
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        self.assertEqual(todo.due_date.date(), tomorrow)
    
    def test_create_todo_with_custom_datetime(self):
        """Test creating a TODO with custom datetime"""
        due_date = timezone.now() + timedelta(days=2)
        data = {
            'title': 'Custom TODO',
            'due_date': due_date.strftime('%Y-%m-%dT%H:%M')
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        todo = Todo.objects.get(title='Custom TODO')
        self.assertIsNotNone(todo.due_date)


class TodoEditViewTest(TestCase):
    """Test cases for the todo edit view"""
    
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(title="Original TODO")
        self.url = reverse('todo_edit', kwargs={'pk': self.todo.pk})
    
    def test_edit_view_get(self):
        """Test GET request to edit view"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], TodoForm)
        self.assertEqual(response.context['action'], 'Edit')
        self.assertEqual(response.context['todo'], self.todo)
    
    def test_edit_view_with_invalid_pk(self):
        """Test edit view with non-existent TODO"""
        url = reverse('todo_edit', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_edit_todo_with_valid_data(self):
        """Test updating a TODO with valid data"""
        data = {
            'title': 'Updated TODO',
            'description': 'Updated description',
            'is_resolved': True
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated TODO')
        self.assertEqual(self.todo.description, 'Updated description')
        self.assertTrue(self.todo.is_resolved)
    
    def test_edit_todo_quick_date_detection(self):
        """Test that edit form detects today/tomorrow correctly"""
        # Create TODO with today's date
        today = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        self.todo.due_date = today
        self.todo.save()
        
        response = self.client.get(self.url)
        form = response.context['form']
        self.assertEqual(form.fields['quick_date'].initial, 'today')


class TodoDeleteViewTest(TestCase):
    """Test cases for the todo delete view"""
    
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(title="TODO to delete")
        self.url = reverse('todo_delete', kwargs={'pk': self.todo.pk})
    
    def test_delete_view_get(self):
        """Test GET request to delete view shows confirmation"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['todo'], self.todo)
    
    def test_delete_view_with_invalid_pk(self):
        """Test delete view with non-existent TODO"""
        url = reverse('todo_delete', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_delete_todo_post(self):
        """Test deleting a TODO via POST"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=self.todo.pk).exists())


class TodoToggleResolvedViewTest(TestCase):
    """Test cases for the toggle resolved view"""
    
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(title="Test TODO", is_resolved=False)
        self.url = reverse('todo_toggle_resolved', kwargs={'pk': self.todo.pk})
    
    def test_toggle_resolved_from_false_to_true(self):
        """Test toggling resolved status from False to True"""
        self.assertFalse(self.todo.is_resolved)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_resolved)
    
    def test_toggle_resolved_from_true_to_false(self):
        """Test toggling resolved status from True to False"""
        self.todo.is_resolved = True
        self.todo.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.is_resolved)
    
    def test_toggle_resolved_with_invalid_pk(self):
        """Test toggle resolved with non-existent TODO"""
        url = reverse('todo_toggle_resolved', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoFormTest(TestCase):
    """Test cases for the TodoForm"""
    
    def test_form_with_valid_data(self):
        """Test form with valid data"""
        data = {
            'title': 'Form Test TODO',
            'description': 'Test description',
            'is_resolved': False
        }
        form = TodoForm(data)
        self.assertTrue(form.is_valid())
    
    def test_form_without_title(self):
        """Test form validation without required title"""
        data = {
            'description': 'No title'
        }
        form = TodoForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_form_quick_date_choices(self):
        """Test that quick_date field has correct choices"""
        form = TodoForm()
        choices = [choice[0] for choice in form.fields['quick_date'].choices]
        self.assertIn('today', choices)
        self.assertIn('tomorrow', choices)
        self.assertIn('custom', choices)
    
    def test_form_quick_time_choices(self):
        """Test that quick_time field has correct choices"""
        form = TodoForm()
        choices = [choice[0] for choice in form.fields['quick_time'].choices]
        self.assertIn('09:00', choices)
        self.assertIn('12:00', choices)
        self.assertIn('17:00', choices)
        self.assertIn('20:00', choices)
        self.assertIn('23:59', choices)


class TodoURLTest(TestCase):
    """Test cases for URL routing"""
    
    def setUp(self):
        self.client = Client()
    
    def test_todo_list_url(self):
        """Test that todo_list URL resolves correctly"""
        url = reverse('todo_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_todo_create_url(self):
        """Test that todo_create URL resolves correctly"""
        url = reverse('todo_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_todo_edit_url(self):
        """Test that todo_edit URL resolves correctly"""
        todo = Todo.objects.create(title="Test")
        url = reverse('todo_edit', kwargs={'pk': todo.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_todo_delete_url(self):
        """Test that todo_delete URL resolves correctly"""
        todo = Todo.objects.create(title="Test")
        url = reverse('todo_delete', kwargs={'pk': todo.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_todo_toggle_resolved_url(self):
        """Test that todo_toggle_resolved URL resolves correctly"""
        todo = Todo.objects.create(title="Test")
        url = reverse('todo_toggle_resolved', kwargs={'pk': todo.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirects


class TodoIntegrationTest(TestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.client = Client()
    
    def test_full_crud_workflow(self):
        """Test complete Create-Read-Update-Delete workflow"""
        # Create
        create_url = reverse('todo_create')
        data = {
            'title': 'Integration Test TODO',
            'description': 'Testing full workflow',
            'quick_date': 'today',
            'quick_time': '12:00'
        }
        response = self.client.post(create_url, data)
        self.assertEqual(response.status_code, 302)
        
        # Read
        todo = Todo.objects.get(title='Integration Test TODO')
        self.assertIsNotNone(todo)
        
        # Update
        edit_url = reverse('todo_edit', kwargs={'pk': todo.pk})
        update_data = {
            'title': 'Updated Integration TODO',
            'description': 'Updated description'
        }
        response = self.client.post(edit_url, update_data)
        self.assertEqual(response.status_code, 302)
        todo.refresh_from_db()
        self.assertEqual(todo.title, 'Updated Integration TODO')
        
        # Toggle resolved
        toggle_url = reverse('todo_toggle_resolved', kwargs={'pk': todo.pk})
        response = self.client.get(toggle_url)
        self.assertEqual(response.status_code, 302)
        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)
        
        # Delete
        delete_url = reverse('todo_delete', kwargs={'pk': todo.pk})
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Todo.objects.filter(pk=todo.pk).exists())
