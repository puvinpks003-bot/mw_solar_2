from django.urls import path
from . import views

app_name = 'admin_portal'

urlpatterns = [
    path('login/', views.admin_auth_view, name='admin_auth'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('delete-user/<int:user_id>/', views.admin_delete_user_view, name='admin_delete_user'),
    path('user/<int:user_id>/dashboard/', views.admin_user_dashboard_view, name='admin_user_dashboard'),
]
