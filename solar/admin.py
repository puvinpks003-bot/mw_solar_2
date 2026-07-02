from django.contrib import admin
from .models import CustomUser, SolarCalculation

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('mobile_number', 'full_name', 'email', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('mobile_number', 'full_name', 'email')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    ordering = ('-date_joined',)

@admin.register(SolarCalculation)
class SolarCalculationAdmin(admin.ModelAdmin):
    list_display = ('user', 'monthly_bill', 'investment', 'roi', 'carbon_saved', 'created_at')
    search_fields = ('user__mobile_number', 'user__full_name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
