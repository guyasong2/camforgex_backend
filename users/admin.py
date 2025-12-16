from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'role', 'promoter_type', 'is_promoter_approved')
    list_filter = ('role', 'promoter_type', 'is_promoter_approved')
    search_fields = ('username', 'email')