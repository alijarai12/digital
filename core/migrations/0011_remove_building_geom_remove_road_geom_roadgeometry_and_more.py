# Generated by Django 4.1 on 2023-07-26 05:23

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0010_alter_building_file_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="building",
            name="geom",
        ),
        migrations.RemoveField(
            model_name="road",
            name="geom",
        ),
        migrations.CreateModel(
            name="RoadGeometry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.GeometryField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="road",
                        to="core.road",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BuildingGeometry",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "geom",
                    django.contrib.gis.db.models.fields.GeometryField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                (
                    "feature",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="building",
                        to="core.building",
                    ),
                ),
            ],
        ),
    ]
