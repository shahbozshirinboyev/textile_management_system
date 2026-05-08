from django.db import migrations


def seed_order_status(apps, schema_editor):
    OrderStatus = apps.get_model('orders', 'OrderStatus')
    statuses = [
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In progress'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    for code, name in statuses:
        OrderStatus.objects.get_or_create(code=code, defaults={'name': name})


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_order_status, migrations.RunPython.noop),
    ]
