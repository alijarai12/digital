# Generated by Django 4.1 on 2024-01-02 10:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0076_building_ref_centroid"),
    ]

    operations = [
        migrations.AddField(
            model_name="historylog",
            name="association_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
