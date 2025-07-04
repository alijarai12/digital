# Generated by Django 4.1 on 2023-07-19 08:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_road_bbox"),
    ]

    operations = [
        migrations.AddField(
            model_name="building",
            name="association_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Main", "main"),
                    ("Associate", "associate"),
                    ("Dissociate", "dissociate"),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="building",
            name="roof_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("RCC", "rcc"),
                    ("Tile", "tile"),
                    ("GI Sheet", "gi_sheet"),
                    ("Others", "others"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
