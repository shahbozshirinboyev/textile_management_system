from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    quantity = models.PositiveIntegerField(default=1, help_text='Miqdor (dona, kg, metr va h.k.)')
    amount = models.DecimalField(max_digits=14, decimal_places=2, help_text='Birlik narxi')
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False)
    note = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_amount = self.quantity * self.amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.type} - {self.total_amount}'

    class Meta:
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-date', '-created_at']


class Statistics(models.Model):
    month = models.DateField(unique=True)
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


def _refresh_statistics_for_month(month_date):
    """Recalculate and upsert statistics for the given month (uses first day of month)."""
    from django.db.models import Sum, Value
    from django.db.models.functions import Coalesce
    from django.db.models import DecimalField
    import datetime

    first_day = month_date.replace(day=1)

    if isinstance(first_day, datetime.datetime):
        first_day = first_day.date()

    MONEY = DecimalField(max_digits=14, decimal_places=2)

    orders_total = Order.objects.filter(
        date__year=first_day.year,
        date__month=first_day.month,
    ).aggregate(
        total=Coalesce(Sum('sale_price'), Value(0), output_field=MONEY)
    )['total']

    payments_total = Payment.objects.filter(
        date__year=first_day.year,
        date__month=first_day.month,
        status__code='accepted',
    ).aggregate(
        total=Coalesce(Sum('amount'), Value(0), output_field=MONEY)
    )['total']

    expenses_total = Expense.objects.filter(
        date__year=first_day.year,
        date__month=first_day.month,
    ).aggregate(
        total=Coalesce(Sum('total_amount'), Value(0), output_field=MONEY)
    )['total']

    Statistics.objects.update_or_create(
        month=first_day,
        defaults={
            'monthly_orders_total': orders_total,
            'monthly_payments_total': payments_total,
            'monthly_expenses_total': expenses_total,
        },
    )


@receiver(post_save, sender=Order)
def update_stats_on_order_save(sender, instance, **kwargs):
    _refresh_statistics_for_month(instance.date)


@receiver(post_save, sender=Payment)
def update_stats_on_payment_save(sender, instance, **kwargs):
    _refresh_statistics_for_month(instance.date)


@receiver(post_save, sender=Expense)
def update_stats_on_expense_save(sender, instance, **kwargs):
    _refresh_statistics_for_month(instance.date)


# Also refresh on delete
from django.db.models.signals import post_delete


@receiver(post_delete, sender=Order)
def update_stats_on_order_delete(sender, instance, **kwargs):
    _refresh_statistics_for_month(instance.date)


@receiver(post_delete, sender=Payment)
def update_stats_on_payment_delete(sender, instance, **kwargs):
    _refresh_statistics_for_month(instance.date)


@receiver(post_delete, sender=Expense)
def update_stats_on_expense_delete(sender, instance, **kwargs):
    _refresh_statistics_for_month(instance.date)
