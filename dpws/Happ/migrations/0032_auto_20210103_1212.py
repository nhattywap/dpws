# Generated by Django 3.1 on 2021-01-03 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0031_auto_20210103_1114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='time',
            field=models.DateTimeField(),
        ),
    ]