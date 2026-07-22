from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Django's built-in user, extended with a role for access control."""
    ADMIN = 'Admin'
    CASHIER = 'Cashier'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (CASHIER, 'Cashier'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=CASHIER)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Category(models.Model):
    """Hardware category: CPU, GPU, RAM, Motherboard, Storage, PSU."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    """A part in the catalogue. Technical specs live in `attributes`."""
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products'
    )
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=3)
    attributes = models.JSONField(default=dict, blank=True)

    def is_low_stock(self):
        """Used by the dashboard and the low-stock flag."""
        return self.stock_quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.brand} {self.name}"


class SerialNumber(models.Model):
    """One physical unit of a product, tracked individually."""
    IN_STOCK = 'In Stock'
    SOLD = 'Sold'
    STATUS_CHOICES = [
        (IN_STOCK, 'In Stock'),
        (SOLD, 'Sold'),
    ]

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='serial_numbers'
    )
    serial_code = models.CharField(max_length=100, unique=True)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=IN_STOCK
    )

    def __str__(self):
        return f"{self.serial_code} ({self.status})"


class Sale(models.Model):
    """A completed sale of one serial-numbered unit."""
    serial_number = models.OneToOneField(
        SerialNumber, on_delete=models.PROTECT, related_name='sale'
    )
    user = models.ForeignKey(
        User, on_delete=models.PROTECT, related_name='sales'
    )
    sale_date = models.DateTimeField(auto_now_add=True)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Sale #{self.id} — {self.serial_number.serial_code}"
