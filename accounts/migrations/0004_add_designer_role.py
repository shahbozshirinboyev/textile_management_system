from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_userprofile_role'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('admin', 'Admin'),
                    ('buyer', 'Buyer'),
                    ('employee', 'Employee'),
                    ('designer', 'Designer'),
                ],
                default='buyer',
                max_length=20,
            ),
        ),
    ]
