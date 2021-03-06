# Generated by Django 3.1 on 2020-11-09 09:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Happ', '0026_highsurtitle_surveyvote_surveywithvote'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=100)),
                ('comment', models.TextField()),
                ('news', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Happ.news')),
            ],
        ),
    ]
