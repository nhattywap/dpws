# Generated by Django 3.1 on 2020-09-17 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0008_auto_20200917_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepicture',
            name='pic',
            field=models.ImageField(upload_to='Happ/static/Happ/file'),
        ),
    ]
