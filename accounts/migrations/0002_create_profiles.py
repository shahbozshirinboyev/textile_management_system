from django.conf import settings
from django.db import migrations


def create_profiles(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], settings.AUTH_USER_MODEL.split('.')[1])
    UserProfile = apps.get_model('accounts', 'UserProfile')

    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_profiles, migrations.RunPython.noop),
    ]
