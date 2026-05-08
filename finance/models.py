from django.db import models

from orders.models import Order


class PaymentStatus(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Payment Status'
        verbose_name_plural = 'Payment Statuses'
        ordering = ['id']


class Payment(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    receipt_image = models.ImageField(upload_to='checks/', blank=True, null=True)
    status = models.ForeignKey(PaymentStatus, on_delete=models.PROTECT, related_name='payments')
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment #{self.id} - {self.amount}'

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-date', '-created_at']


class ExpenseType(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Expense Type'
        verbose_name_plural = 'Expense Types'
        ordering = ['id']


class Expense(models.Model):
    date = models.DateField()
    type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT, related_name='expenses')
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.type} - {self.amount}'

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date', '-created_at']


class Statistics(models.Model):
    month = models.DateField()
    monthly_orders_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    monthly_payments_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    monthly_expenses_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Statistics - {self.month:%Y-%m}'

    class Meta:
        verbose_name = 'Statistics'
        verbose_name_plural = 'Statistics'
        ordering = ['-month']
