# Generated by Django 3.1 on 2020-10-20 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0020_auto_20201020_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='discussionvote',
            name='author',
            field=models.CharField(default='username', max_length=100),
        ),
    ]