# Generated by Django 3.1 on 2020-09-17 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0003_profilepicture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepicture',
            name='pic',
            field=models.ImageField(height_field=100, upload_to='file', width_field=100),
        ),
    ]