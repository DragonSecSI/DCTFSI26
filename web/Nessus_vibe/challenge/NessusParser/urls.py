from django.urls import path
from . import views

urlpatterns = [
    path('', views.root, name='root'),
    path('list-scans/', views.list_scans, name='list_scans'),
    path('delete-scan/<int:scan_id>/', views.delete_scan, name='delete_scan'),
    path('list-projects/', views.list_projects, name='list_projects'),
    path('create-project/', views.create_project, name='create_project'),
    path('delete-project/<int:project_id>/', views.delete_project, name='delete_project'),
    path('project-scans/<int:project_id>/', views.get_project_scans, name='get_project_scans'),
    path('assign-scan-to-project/', views.assign_scan_to_project, name='assign_scan_to_project'),
    path('unassigned-scans/', views.get_unassigned_scans, name='get_unassigned_scans'),
]