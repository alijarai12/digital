# Generated by Django 4.1 on 2023-10-31 05:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0003_alter_user_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkshopMode",
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
                ("workshop_mode", models.BooleanField(blank=True, null=True)),
            ],
        ),
    ]
