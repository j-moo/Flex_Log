from django.contrib import admin
from .models import Category, Comment, ExpenseLog, Like
admin.site.register(Category); admin.site.register(ExpenseLog); admin.site.register(Like); admin.site.register(Comment)
