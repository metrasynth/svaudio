# Generated by Django 3.1.8 on 2021-04-19 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repo', '0006_auto_20210419_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='num_vote_down',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='module',
            name='num_vote_up',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='module',
            name='vote_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='num_vote_down',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='num_vote_up',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        migrations.AddField(
            model_name='project',
            name='vote_score',
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
