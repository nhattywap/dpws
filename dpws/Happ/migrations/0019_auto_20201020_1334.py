# Generated by Django 3.1 on 2020-10-20 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0018_auto_20201020_1237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discussionwithvote',
            name='voters',
        ),
        migrations.AddField(
            model_name='discussionwithvote',
            name='voter',
            field=models.CharField(default='doctor', max_length=100),
        ),
    ]