# Generated by Django 4.1 on 2023-08-08 08:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0036_alter_building_roof_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="building",
            name="building_use",
            field=models.CharField(
                blank=True,
                choices=[
                    ("residential", "Residential"),
                    ("commercial", "Commercial"),
                    ("multi_use", "Multi use"),
                    ("institutional", "Institutional"),
                    ("unused", "Unused"),
                    ("other", "Other"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
