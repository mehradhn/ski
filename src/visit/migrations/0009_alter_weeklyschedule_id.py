# Generated by Django 4.1.8 on 2023-05-01 08:41

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('visit', '0008_remove_weeklyschedule_flag'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklyschedule',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
