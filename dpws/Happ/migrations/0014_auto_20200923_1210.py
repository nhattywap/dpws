# Generated by Django 3.1 on 2020-09-23 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0013_profilepicture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profilepicture',
            name='photo',
            field=models.ImageField(upload_to='Happ/static/Happ/file'),
        ),
    ]
