# Generated by Django 4.1 on 2023-08-11 09:01

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0045_alter_roadcategorychoice_alias_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="road",
            name="ward_no",
        ),
    ]
