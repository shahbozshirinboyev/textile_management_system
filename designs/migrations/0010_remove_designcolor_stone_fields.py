from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0009_remove_design_color_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='designcolor',
            name='use_plastic_stone',
        ),
        migrations.RemoveField(
            model_name='designcolor',
            name='stone_size',
        ),
    ]
