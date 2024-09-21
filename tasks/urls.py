from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/new/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('subordinates/tasks/', views.SubordinateTaskListView.as_view(), name='subordinate_task_list'),
    path('export/text/', views.export_tasks_text, name='export_tasks_text'),
    path('export/excel/', views.export_tasks_excel, name='export_tasks_excel'),
]
