from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_alter_order_cost_price_alter_order_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='stone_type',
            field=models.CharField(
                choices=[('glass', 'Shisha tosh'), ('plastic', 'Plastik tosh')],
                default='glass',
                help_text='Tosh turi (xaridor tanlaydi)',
                max_length=10,
            ),
        ),
    ]
