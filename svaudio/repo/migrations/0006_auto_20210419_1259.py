# Generated by Django 3.1.8 on 2021-04-19 12:59

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('Tags', '0001_initial'),
        ('repo', '0005_auto_20210415_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='Tags.TaggedItem', to='Tags.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='project',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='Tags.TaggedItem', to='Tags.Tag', verbose_name='Tags'),
        ),
    ]
