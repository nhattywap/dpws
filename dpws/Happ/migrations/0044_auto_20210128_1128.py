# Generated by Django 3.1 on 2021-01-28 11:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0043_auto_20210128_0200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctor',
            name='profession',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Happ.profession'),
        ),
    ]