# Generated by Django 4.1 on 2023-07-19 07:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_building_ward_no_alter_road_file_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="road",
            name="bbox",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
