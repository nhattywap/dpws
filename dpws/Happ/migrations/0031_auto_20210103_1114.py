# Generated by Django 3.1 on 2021-01-03 08:14

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0030_auto_20210103_0107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]