# Generated by Django 4.1 on 2023-10-17 08:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dmaps", "0007_remove_card_collaboration_remove_card_contact_us_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="card",
            name="type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("major_feature", "Major Feature"),
                    ("major_component", "Major Component Case"),
                    ("client", "We Work With: client"),
                    (
                        "partner_and_collabrators",
                        "We Work With: Partner and Collabrators",
                    ),
                    ("municipal_management", "Use Case:Municipal Management"),
                    ("navigational_operations", "Use Case:Navigational Operations"),
                    (
                        "data_management_and_centralization",
                        "Use Case:Data Management and Centralization",
                    ),
                    (
                        "geospatial_planning_and_visualization",
                        "Use Case:Geospatial Planning and Visualization",
                    ),
                    ("contact_us", "Contact Us"),
                    ("use_case", "Use Case"),
                    ("use_case_major_feature", "Use Case Major Feature"),
                    ("collaboration", "Collaboration"),
                ],
                max_length=50,
                null=True,
            ),
        ),
    ]
