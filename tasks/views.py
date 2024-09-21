from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .models import Task
from .forms import TaskForm

class TaskCreateView(LoginRequiredMixin, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Task'
        return context
    
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


from django.views.generic.list import ListView
from django.utils import timezone
from datetime import timedelta

class TaskListView(LoginRequiredMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Task'
        return context
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        week = self.request.GET.get('week')
        if week:
            week = int(week)
        else:
            week = timezone.now().isocalendar()[1]

        tasks = Task.objects.filter(
            user=user,
            created_at__week=week
        )
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['week'] = self.request.GET.get('week', timezone.now().isocalendar()[1])
        return context



from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone
from django.views.generic.edit import UpdateView

class TaskUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task_list')

    def test_func(self):
        task = self.get_object()
        one_week_ago = timezone.now() - timedelta(weeks=1)
        return task.user == self.request.user and task.created_at >= one_week_ago



class SubordinateTaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/subordinate_task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        user = self.request.user
        subordinates = user.get_all_subordinates()
        week = self.request.GET.get('week')
        if week:
            week = int(week)
        else:
            week = timezone.now().isocalendar()[1]

        tasks = Task.objects.filter(
            user__in=subordinates,
            created_at__week=week
        )
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['week'] = self.request.GET.get('week', timezone.now().isocalendar()[1])
        return context



from django.http import HttpResponse

def export_tasks_text(request):
    tasks = Task.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=tasks.txt'

    for task in tasks:
        response.write(f"{task.created_at.date()} - {task.description} ({task.time_spent} mins)\n")

    return response



import openpyxl
from openpyxl.utils import get_column_letter

def export_tasks_excel(request):
    tasks = Task.objects.filter(user=request.user)
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Tasks'

    # Define the titles for columns
    columns = ['Date', 'Description', 'Time Spent (mins)']
    row_num = 1

    # Assign the titles for each cell of the header
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=row_num, column=col_num)
        cell.value = column_title

    # Iterate through all tasks
    for task in tasks:
        row_num += 1
        row = [
            task.created_at.date(),
            task.description,
            task.time_spent,
        ]
        for col_num, cell_value in enumerate(row, 1):
            cell = worksheet.cell(row=row_num, column=col_num)
            cell.value = cell_value

    # Adjust column widths
    for col_num in range(1, len(columns) + 1):
        column_letter = get_column_letter(col_num)
        worksheet.column_dimensions[column_letter].width = 25

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename=tasks.xlsx'
    workbook.save(response)
    return response
