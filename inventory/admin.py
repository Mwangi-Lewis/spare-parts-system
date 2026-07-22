from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, Product, SerialNumber, Sale


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff", "is_superuser")
    # add our custom 'role' field to the default Django user edit form
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role", {"fields": ("role",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Role", {"fields": ("role",)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "product_count")
    search_fields = ("name",)

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "brand", "category", "price",
        "stock_quantity", "stock_status",
    )
    list_filter = ("category", "brand")
    search_fields = ("name", "brand")
    ordering = ("category__name", "brand", "name")

    @admin.display(description="Status")
    def stock_status(self, obj):
        return "Low stock" if obj.is_low_stock() else "In stock"


@admin.register(SerialNumber)
class SerialNumberAdmin(admin.ModelAdmin):
    list_display = ("serial_code", "product", "product_category", "status")
    list_filter = ("status", "product__category")
    search_fields = ("serial_code", "product__name", "product__brand")
    ordering = ("product__name", "serial_code")

    @admin.display(description="Category", ordering="product__category__name")
    def product_category(self, obj):
        return obj.product.category.name


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "id", "product_name", "serial_code",
        "user", "sale_price", "sale_date",
    )
    list_filter = ("sale_date", "user", "serial_number__product__category")
    search_fields = (
        "serial_number__serial_code",
        "serial_number__product__name",
    )
    ordering = ("-sale_date",)
    readonly_fields = ("sale_date",)

    @admin.display(description="Product", ordering="serial_number__product__name")
    def product_name(self, obj):
        product = obj.serial_number.product
        return f"{product.brand} {product.name}"

    @admin.display(description="Serial number")
    def serial_code(self, obj):
        return obj.serial_number.serial_code
