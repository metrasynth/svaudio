# Generated by Django 3.2 on 2021-05-03 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0014_auto_20210425_0444'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='metadata',
            field=models.JSONField(blank=True, help_text='Metadata provided by API client', null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='metadata',
            field=models.JSONField(blank=True, help_text='Metadata provided by API client', null=True),
        ),
    ]
