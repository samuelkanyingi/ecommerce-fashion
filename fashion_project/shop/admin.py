from django.contrib import admin
from .models import Product

# Register your models here.

# admin.site.register(Product)
# admin.site.register(Seller)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "subcategory", "price", "stock")
    list_filter = ("category", "subcategory")