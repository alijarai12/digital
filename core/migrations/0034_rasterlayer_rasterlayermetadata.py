# Generated by Django 4.1 on 2023-08-04 11:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0033_rename_title_vectorlayer_description_en_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="RasterLayer",
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
                ("updated_date", models.DateTimeField(auto_now=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                ("name_en", models.CharField(blank=True, max_length=50, null=True)),
                ("name_ne", models.CharField(blank=True, max_length=50, null=True)),
                ("raster_file", models.FileField(upload_to="raster/")),
                (
                    "sld_file",
                    models.FileField(
                        blank=True, null=True, upload_to="layer/sld_uploads"
                    ),
                ),
                ("attr_data", models.JSONField(blank=True, default=dict, null=True)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("in_process", "In Process"),
                            ("completed", "Completed"),
                            ("error", "Error"),
                        ],
                        max_length=15,
                        null=True,
                    ),
                ),
                ("display_on_map", models.BooleanField(default=True)),
                ("is_public", models.BooleanField(default=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="RasterLayerMetadata",
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
                ("width", models.IntegerField(blank=True, null=True)),
                ("height", models.IntegerField(blank=True, null=True)),
                ("numbands", models.IntegerField(blank=True, null=True)),
                ("srid", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("extent", models.JSONField(blank=True, null=True)),
                ("legend", models.JSONField(blank=True, null=True)),
                ("stats", models.JSONField(blank=True, null=True)),
                ("pixel_size", models.FloatField(default=0)),
                ("minx", models.FloatField(default=0)),
                ("maxx", models.FloatField(default=0)),
                ("file_name", models.CharField(blank=True, max_length=100, null=True)),
                (
                    "rasterlayer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="raster_layer_metadata",
                        to="core.rasterlayer",
                    ),
                ),
            ],
        ),
    ]
