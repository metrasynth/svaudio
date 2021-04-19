# Generated by Django 3.1.8 on 2021-04-14 21:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0003_auto_20210414_2148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='url',
            field=models.URLField(help_text='URL where resource can be publicly accessed.', max_length=2048, unique=True),
        ),
    ]