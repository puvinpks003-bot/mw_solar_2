from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Password Reset URLs
    path('password_reset/', views.password_reset_request_view, name='password_reset'),
    path('password_reset/done/', views.password_reset_done_view, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete_view, name='password_reset_complete'),

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/charts/', views.dashboard_charts_api_view, name='api_charts'),
    path('calculator/', views.calculator_view, name='calculator'),
    path('history/', views.history_view, name='history'),
    path('history/delete/<int:calc_id>/', views.delete_calculation_view, name='delete_calculation'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/delete/', views.delete_account_view, name='delete_account'),
]
