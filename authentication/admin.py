# admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from rest_framework.authtoken.admin import TokenAdmin

CustomUser = get_user_model()

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    search_fields = [ 'email', 'full_name'] 
    list_display = [ 'email', 'full_name', 'is_active', 'is_staff', 'is_superuser']
    list_filter = ['is_active', 'is_staff', 'is_superuser']

TokenAdmin.raw_id_fields = ('user',)
