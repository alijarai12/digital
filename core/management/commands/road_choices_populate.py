import os
import django

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project_name.settings")
django.setup()
from django.core.management.base import BaseCommand
from core.models import RoadCategoryChoice
from core.utils.constants import (
    ROAD_CATEGORY_CHOICES,
    ROAD_CLASS_CHOICES,
    PAVEMENT_TYPE_CHOICES,
    ROAD_LANE_CHOICES,
)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        choices_to_populate = [
            (ROAD_CATEGORY_CHOICES, "road_category"),
            (ROAD_CLASS_CHOICES, "road_class"),
            (PAVEMENT_TYPE_CHOICES, "road_type"),
            (ROAD_LANE_CHOICES, "road_lane"),
        ]
        for choices, attribute_type in choices_to_populate:
            populate_choices(choices, attribute_type)


def populate_choices(choice_list, attribute_type):
    try:
        for choice_value, choice_label, choice_label_ne in choice_list:
            instance, created = RoadCategoryChoice.objects.get_or_create(
                attribute_name=choice_value,
                alias_name=choice_label,
                type=attribute_type,
            )
            instance.alias_name_ne = choice_label_ne
            instance.save()
    except Exception as e:
        print(f"Error while populating choices: {str(e)}")
