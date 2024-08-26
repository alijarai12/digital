from user.models import Ward
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Populate the Ward model with ward numbers and names"

    def handle(self, *args, **kwargs):
        # Check if there are already wards in the database
        existing_wards = Ward.objects.count()

        if existing_wards == 0:
            # If there are no existing wards, create new ones
            for ward_number in range(1, 26):
                ward_name = f"Ward No {ward_number}"
                Ward.objects.create(
                    ward_no=ward_number, name=ward_name, name_ne=ward_name
                )

            self.stdout.write(self.style.SUCCESS("Successfully created wards."))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Wards already exist in the database. No new wards were created."
                )
            )
