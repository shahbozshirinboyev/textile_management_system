from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_rename_orders_to_english'),
        ('finance', '0003_seed_status_and_types'),
    ]

    operations = []
