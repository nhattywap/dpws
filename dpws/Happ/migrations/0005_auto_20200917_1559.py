# Generated by Django 3.1 on 2020-09-17 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0004_auto_20200917_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepicture',
            name='pic',
            field=models.ImageField(height_field=100, max_length=10000, upload_to='file', width_field=100),
        ),
    ]