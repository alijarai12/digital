# Generated by Django 4.1 on 2023-09-14 11:11

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0060_alter_building_house_no"),
    ]

    operations = [
        migrations.AlterField(
            model_name="building",
            name="building_sp_use",
            field=multiselectfield.db.fields.MultiSelectField(
                blank=True, choices=[], max_length=500, null=True
            ),
        ),
    ]
