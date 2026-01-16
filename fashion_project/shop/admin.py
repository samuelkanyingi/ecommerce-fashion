from django.contrib import admin
from .models import Product, Order
from django.urls import reverse
from django.utils.html import format_html

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "subcategory", "price", "stock")
    list_filter = ("category", "subcategory")
    search_fields = ("name", "subcategory")
    list_editable = ("stock",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("tracking_number", "buyer", "amount", "status", "mpesa_receipt", "phone", "city")
    list_filter = ("status",)
    search_fields = ("tracking_number", "buyer__username", "mpesa_receipt", "phone")
    readonly_fields = ("tracking_number",)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['inventory_url'] = reverse('inventory')
        return super().changelist_view(request, extra_context)

# Customize admin site header
admin.site.site_header = "FashionHub Administration"
admin.site.site_title = "FashionHub Admin"
admin.site.index_title = "Welcome to FashionHub Admin Panel"