# Generated by Django 3.1 on 2021-01-19 23:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0034_auto_20210107_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]