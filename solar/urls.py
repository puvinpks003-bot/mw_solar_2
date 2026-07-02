from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/charts/', views.dashboard_charts_api_view, name='api_charts'),
    path('calculator/', views.calculator_view, name='calculator'),
    path('history/', views.history_view, name='history'),
    path('history/delete/<int:calc_id>/', views.delete_calculation_view, name='delete_calculation'),
    path('profile/', views.profile_view, name='profile'),
]
