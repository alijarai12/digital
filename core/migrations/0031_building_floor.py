# Generated by Django 4.1 on 2023-08-03 15:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0030_alter_building_association_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="building",
            name="floor",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
