# Generated by Django 3.2 on 2021-05-08 22:32

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('Tags', '0004_auto_20210423_0025'),
    ]

    operations = [
        migrations.AddField(
            model_name='taggeditem',
            name='added_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
