from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_create_profiles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('admin', 'Admin'), ('buyer', 'Buyer'), ('employee', 'Employee')], default='buyer', max_length=20),
        ),
    ]
