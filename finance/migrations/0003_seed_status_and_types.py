from django.db import migrations


def seed_finance_data(apps, schema_editor):
    PaymentStatus = apps.get_model('finance', 'PaymentStatus')
    ExpenseType = apps.get_model('finance', 'ExpenseType')

    payment_statuses = [
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    expense_types = [
        ('salary', 'Salary'),
        ('food', 'Food'),
        ('raw_material', 'Raw material'),
        ('utilities', 'Utilities'),
        ('rent', 'Rent'),
    ]

    for code, name in payment_statuses:
        PaymentStatus.objects.get_or_create(code=code, defaults={'name': name})

    for code, name in expense_types:
        ExpenseType.objects.get_or_create(code=code, defaults={'name': name})


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(seed_finance_data, migrations.RunPython.noop),
    ]
