import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0006_rename_price_update_stone'),
    ]

    operations = [
        # Create MoldPrice model
        migrations.CreateModel(
            name='MoldPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, help_text='Qolip tortish narxi (bir rang uchun)', max_digits=10)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Mold Price',
                'verbose_name_plural': 'Mold Price',
                'ordering': ['-created_at'],
            },
        ),
        # Remove mold_price field from Design (added in migration 0006)
        migrations.RemoveField(
            model_name='design',
            name='mold_price',
        ),
    ]
