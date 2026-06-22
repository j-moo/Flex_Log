from django.contrib import admin

from .models import Category, Comment, ExpenseLog, Like


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(ExpenseLog)
class ExpenseLogAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'amount', 'is_visible', 'created_at')
    list_filter = ('category', 'is_visible')
    search_fields = ('title', 'user__username', 'content')


admin.site.register(Like)
admin.site.register(Comment)
