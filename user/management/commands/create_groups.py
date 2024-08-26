from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    This createS the default Django groups
    """

    GROUPS = [
        "public",
        "ward viewer",
        "ward editor",
        "municipal viewer",
        "municipal editor",
        "municipal admin",
        "super admin",
    ]

    def handle(self, **options):
        for group_name in self.GROUPS:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(
                    self.style.WARNING(
                        "The group has been created with name:  {}".format(group.name)
                    )
                )
