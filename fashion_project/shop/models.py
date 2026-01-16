from django.db import models
from django.contrib.auth.models import User
import uuid


class Product(models.Model):
    name = models.CharField(max_length=100)
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
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    amount = models.IntegerField()
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