# Generated by Django 3.1.8 on 2021-04-15 23:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0004_auto_20210414_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='most_recent_file',
            field=models.ForeignKey(blank=True, help_text='Most recent file downloaded.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='locations', to='repo.file'),
        ),
    ]
