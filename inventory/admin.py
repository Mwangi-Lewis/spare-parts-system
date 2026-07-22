from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, SerialNumber, Sale

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(SerialNumber)
admin.site.register(Sale)