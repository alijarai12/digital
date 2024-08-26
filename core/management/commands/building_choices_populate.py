import os
import django
from django.core.management.base import BaseCommand

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
django.setup()

from core.models import BuildingCategoryChoice
from core.utils.constants import (
    REGISTRATION_TYPE_CHOICES,
    STRUCTURE_CHOICES,
    USE_CHOICES,
    ASSOCIATION_TYPE_CHOICES,
    PAVEMENT_TYPE_CHOICES,
    ROOF_TYPE_CHOICES,
    OWNER_STATUS_CHOICES,
    TEMPRORARY_STATUS_CHOICES,
    ROAD_LANE_CHOICES,
    SPECIFIC_USE_CHOICES,
)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        choices_to_populate = [
            (ASSOCIATION_TYPE_CHOICES, "association_type"),
            (OWNER_STATUS_CHOICES, "owner_status"),
            (TEMPRORARY_STATUS_CHOICES, "temporary_type"),
            (ROOF_TYPE_CHOICES, "roof_type"),
            (STRUCTURE_CHOICES, "building_structure"),
            (REGISTRATION_TYPE_CHOICES, "reg_type"),
            (USE_CHOICES, "building_use"),
            (SPECIFIC_USE_CHOICES, "building_sp_use"),
            (ROAD_LANE_CHOICES, "road_lane"),
            (PAVEMENT_TYPE_CHOICES, "road_type"),
        ]
        for choices, attribute_type in choices_to_populate:
            populate_choices(choices, attribute_type)


def populate_choices(choice_list, attribute_type):
    try:
        for choice_value, choice_label, choice_label_ne in choice_list:
            instance, created = BuildingCategoryChoice.objects.get_or_create(
                attribute_name=choice_value,
                alias_name=choice_label,
                type=attribute_type,
            )
            instance.alias_name_ne = choice_label_ne
            instance.save()
    except Exception as e:
        print(f"Error while populating choices: {str(e)}")
