# Generated by Django 4.1 on 2023-07-27 12:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_alter_road_road_class_alter_road_road_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="building",
            name="file_type",
        ),
        migrations.RemoveField(
            model_name="building",
            name="file_upload",
        ),
        migrations.RemoveField(
            model_name="road",
            name="file_type",
        ),
        migrations.RemoveField(
            model_name="road",
            name="file_upload",
        ),
        migrations.AlterField(
            model_name="building",
            name="building_structure",
            field=models.CharField(
                blank=True,
                choices=[
                    ("R.C.C", "rcc"),
                    ("framed", "framed"),
                    ("Load Bearing", "load_bearing"),
                    ("Wood/Bamboo", "wood/bamboo"),
                    ("compressed_mud", "compressed_mud"),
                    ("Mud Block", "mud block"),
                    ("Others", "others"),
                ],
                max_length=50,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="direction",
            field=models.CharField(
                blank=True,
                choices=[("Left", "left"), ("Right", "right")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="building",
            name="reg_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("Registered and completed", "registered_and_completed"),
                    (
                        "Registered but building under construction",
                        "registered but building under construction",
                    ),
                    ("Not registered", "not_registered"),
                    ("Archived", "archived"),
                    ("Others", "others"),
                ],
                max_length=50,
                null=True,
                verbose_name="registration type",
            ),
        ),
        migrations.AlterField(
            model_name="road",
            name="road_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("black_topped", "black_topped"),
                    ("gravel", "gravel"),
                    ("concrete", "concrete"),
                    ("Earthen", "earthen"),
                    ("Unpaved", "unpaved"),
                    ("Others", "others"),
                ],
                max_length=20,
                null=True,
            ),
        ),
    ]
