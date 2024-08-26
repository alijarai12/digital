from django.core.management.base import BaseCommand
from core.models import Building, PalikaWardGeometry


class Command(BaseCommand):
    help = "Assign ward numbers to buildings based on their spatial relationship"

    def handle(self, *args, **options):
        for building in Building.objects.all():
            try:
                ward_geometry = PalikaWardGeometry.objects.get(
                    geom__contains=building.feature.geom.centroid
                )
                building.ward_no = ward_geometry.ward_no
                building.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully assigned ward number to Building {building.id}"
                    )
                )
            except PalikaWardGeometry.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"Building {building.id} is not within any ward")
                )
