# Generated by Django 4.1.8 on 2023-04-29 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visit', '0003_alter_appointment_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='tracking_number',
            field=models.PositiveIntegerField(editable=False, unique=True, verbose_name='کد رهگیری'),
        ),
    ]