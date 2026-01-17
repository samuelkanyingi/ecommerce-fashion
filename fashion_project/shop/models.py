from django.db import models
from django.contrib.auth.models import User
import uuid


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=50, choices=[
        ('women', 'Women'),
        ('men', 'Men'),
    ], default='men')
    subcategory = models.CharField(max_length=50)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    mpesa_receipt = models.CharField(max_length=50, blank=True, null=True)
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    
    tracking_number = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args, **kwargs)

    def get_total_amount(self):
        """Calculate total from OrderItems (3NF compliant)"""
        return sum(item.get_total() for item in self.items.all())

    def __str__(self):
        return f"Order {self.tracking_number} - {self.buyer.username}"


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    price = models.IntegerField()  # Price at time of purchase
    size = models.CharField(max_length=20, blank=True)  # Shoe size (40, 41) or clothing (S, M, L, XL)
    
    def __str__(self):
        size_info = f" - Size {self.size}" if self.size else ""
        return f"{self.quantity}x {self.product.name}{size_info} - Order {self.order.tracking_number}"
    
    def get_total(self):
        return self.quantity * self.price