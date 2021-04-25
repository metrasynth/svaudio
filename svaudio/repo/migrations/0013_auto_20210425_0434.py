# Generated by Django 3.2 on 2021-04-25 04:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0012_auto_20210425_0042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='alt_name',
            field=models.CharField(blank=True, help_text='Name to show instead of the one embedded in the file', max_length=500, null=True, verbose_name='Alternate name'),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(blank=True, help_text='Limited Markdown supported.', null=True),
        ),
        migrations.AlterField(
            model_name='module',
            name='listed',
            field=models.BooleanField(default=True, help_text='Uncheck this to remove from search results'),
        ),
        migrations.AlterField(
            model_name='project',
            name='alt_name',
            field=models.CharField(blank=True, help_text='Name to show instead of the one embedded in the file', max_length=500, null=True, verbose_name='Alternate name'),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, help_text='Limited Markdown supported.', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='listed',
            field=models.BooleanField(default=True, help_text='Uncheck this to remove from search results'),
        ),
    ]