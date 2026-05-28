from django.conf import settings
from django.db import models

from designs.models import Design


class OrderStatus(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Order Status'
        verbose_name_plural = 'Order Statuses'
        ordering = ['id']


class Order(models.Model):
    design = models.ForeignKey(Design, on_delete=models.PROTECT, related_name='orders')
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='buyer_orders',
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_orders',
    )
    date = models.DateField()
    quantity = models.PositiveIntegerField(default=1, help_text='Buyurtma qilingan dona soni')
    note = models.TextField(blank=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.PROTECT, related_name='orders')
    cost_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    sale_price = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} - {self.design}'

    @property
    def total_sale_price(self):
        return self.sale_price * self.quantity

    @property
    def total_cost_price(self):
        return self.cost_price * self.quantity

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-date', '-created_at']
