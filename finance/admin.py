from django.contrib import admin

from .models import Expense, ExpenseType, Payment, PaymentStatus, Statistics


@admin.register(PaymentStatus)
class PaymentStatusAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'updated_at', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'date', 'amount', 'status', 'receipt_image']
    list_filter = ['status', 'date']
    search_fields = ['id', 'order__id', 'order__design__name']
    autocomplete_fields = ['order', 'status']
    date_hierarchy = 'date'


@admin.register(ExpenseType)
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'updated_at', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'type', 'amount', 'total_amount']
    list_filter = ['type', 'date']
    search_fields = ['id', 'type__name']
    autocomplete_fields = ['type']
    date_hierarchy = 'date'


@admin.register(Statistics)
class StatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'month',
        'monthly_orders_total',
        'monthly_payments_total',
        'monthly_expenses_total',
    ]
    date_hierarchy = 'month'
