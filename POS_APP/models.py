from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone

# --- Category Model ---
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


# --- Product Model ---
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


# --- Customer Model ---
class Customer(models.Model):
    first_name = models.CharField(max_length=500)
    phone = models.CharField(max_length=15)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.first_name


# --- Employee Model ---
class Employee(models.Model):
    emp_name = models.CharField(max_length=50)
    emp_number = models.CharField(max_length=15, unique=True)
    emp_email = models.EmailField(unique=True)
    emp_address = models.TextField()
    # image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    password = models.CharField(max_length=50)  # Consider hashing or using Django auth

    def __str__(self):
        return f"{self.emp_name} ({self.emp_number})"


# --- Sale Model ---
class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    sale_date = models.DateTimeField(default=timezone.now)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    created_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Sale #{self.id} - ₹{self.total_amount} by {self.created_by}"


# --- Sales Detail Model ---
class SalesDetail(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at the time of sale

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ ₹{self.price}"

    def total_price(self):
        return self.quantity * self.price