# Generated by Django 3.2 on 2021-04-15 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("symptoms", "0004_alter_symptom_term"),
    ]

    operations = [
        migrations.AddField(
            model_name="symptomdisorder",
            name="frequency_id",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]