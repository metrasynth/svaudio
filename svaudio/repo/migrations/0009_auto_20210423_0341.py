# Generated by Django 3.1.8 on 2021-04-23 03:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0008_auto_20210423_0025'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ['-file__cached_at']},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ['-file__cached_at']},
        ),
    ]
