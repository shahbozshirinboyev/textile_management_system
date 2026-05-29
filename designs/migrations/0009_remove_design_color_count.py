from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('designs', '0008_alter_stonesize_glass_stone_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='design',
            name='color_count',
        ),
    ]
