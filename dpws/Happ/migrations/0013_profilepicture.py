# Generated by Django 3.1 on 2020-09-23 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0012_delete_profilepicture'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilePicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('photo', models.ImageField(upload_to='Happ/static/Happ/file/')),
            ],
        ),
    ]