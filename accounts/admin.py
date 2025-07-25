from django.contrib import admin
from .models import SearchHistory, ProductSearchHistory
from django.contrib.auth import get_user_model

User = get_user_model()

class SearchHistoryInline(admin.TabularInline):
    model = SearchHistory
    extra = 0
    readonly_fields = ['query', 'searched_at']
    can_delete = False

class ProductSearchHistoryInline(admin.TabularInline):
    model = ProductSearchHistory
    extra = 0

from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    inlines = [SearchHistoryInline, ProductSearchHistoryInline]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


admin.site.register(SearchHistory)
admin.site.register(ProductSearchHistory)
