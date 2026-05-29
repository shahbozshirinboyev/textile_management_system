from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0005_rename_scotch_fields'),
    ]

    operations = [
        # Rename existing 'price' field to 'glass_stone_price'
        migrations.RenameField(
            model_name='stonesize',
            old_name='price',
            new_name='glass_stone_price',
        ),
        # Add new 'plastic_stone_price' field
        migrations.AddField(
            model_name='stonesize',
            name='plastic_stone_price',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Plastik tosh narxi', max_digits=10),
        ),
        # Add 'color_count' to Design
        migrations.AddField(
            model_name='design',
            name='color_count',
            field=models.PositiveIntegerField(default=0, help_text='Ranglar soni'),
        ),
        # Add 'mold_price' to Design
        migrations.AddField(
            model_name='design',
            name='mold_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Qolip tortish narxi (bir rang uchun)', max_digits=10, null=True),
        ),
        # Add 'is_printable' to Design
        migrations.AddField(
            model_name='design',
            name='is_printable',
            field=models.BooleanField(default=False, help_text='Chop etish'),
        ),
        # Add 'use_plastic_stone' to DesignColor
        migrations.AddField(
            model_name='designcolor',
            name='use_plastic_stone',
            field=models.BooleanField(default=False, help_text='Plastik tosh ishlatilsinmi (aks holda shisha)'),
        ),
    ]
