# Generated by Django 3.1 on 2020-09-17 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0006_auto_20200917_1614'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepicture',
            name='pic',
            field=models.ImageField(height_field='100', upload_to='file', width_field='100'),
        ),
    ]
