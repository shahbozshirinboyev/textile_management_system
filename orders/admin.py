from django.contrib import admin

from .models import Order, OrderStatus


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'updated_at', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'design',
        'buyer',
        'employee',
        'date',
        'status',
        'cost_price',
        'sale_price',
    ]
    list_filter = ['status', 'date', 'employee']
    search_fields = ['id', 'design__name', 'buyer__username', 'employee__username', 'note']
    autocomplete_fields = ['design', 'buyer', 'employee', 'status']
    date_hierarchy = 'date'
