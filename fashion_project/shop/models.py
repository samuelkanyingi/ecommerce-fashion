from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='products/')
    category = models.CharField(max_length=50, choices=[
        ('women', 'Women'),
        ('men', 'Men'),
        ('accessories', 'Accessories')
    ], default='men')
    subcategory = models.CharField(max_length=50)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name



class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class CustomUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.username




class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sales")
    amount = models.IntegerField()
    phone = models.CharField(max_length=15)
    mpesa_receipt = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("ESCROW_PENDING", "Escrow Pending"),
            ("ESCROWED", "Escrowed"),
            ("DELIVERED", "Delivered"),
            ("RELEASED", "Released"),
            ("DISPUTE", "Dispute"),
        ],
        default="ESCROW_PENDING"
    )

    