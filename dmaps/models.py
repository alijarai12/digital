from django.db import models
from core.models import User
from ckeditor.fields import RichTextField
from core.tile import MVTManager
from django.contrib.gis.db import models


# Create your models here.

# ==================
# Auditable Model
# ==================


class AuditableModel(models.Model):
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    updated_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


# ==================
# Nav Bar
# ==================
class NavBar(AuditableModel):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)
    icon = models.ImageField(blank=True, null=True, upload_to="icons/")


# ==================
# Header
# ==================


class Header(AuditableModel):
    PAGE_CHOICES = (
        ("home", "Home"),
        ("use_case", "Use Case"),
        ("about", "About"),
        ("contact", "Contact"),
    )
    page = models.CharField(max_length=50, choices=PAGE_CHOICES, blank=True, null=True)
    title_en = RichTextField(blank=True, null=True)
    title_ne = RichTextField(blank=True, null=True)
    description_en = RichTextField(blank=True, null=True)
    description_ne = RichTextField(blank=True, null=True)
    file = models.FileField(upload_to=f"header/", blank=True, null=True)

    def __str__(self):
        return str(self.title_en) if self.title_en else str(self.id)


# ==================
# Footer
# ==================


class Footer(AuditableModel):
    phone_no = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    footer_note = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(self.id)


# ==================
# HOME PAGE
# ==================


class About(AuditableModel):
    title_en = RichTextField(blank=True, null=True)
    title_ne = RichTextField(blank=True, null=True)
    description_en = RichTextField(blank=True, null=True)
    description_ne = RichTextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return str(self.title_en) if self.title_en else str(self.id)


class MajorFeature(AuditableModel):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.title_en)


# MAP


class GeometryFile(models.Model):
    FILE_CHOICES = [
        ("municipality", "Municipality"),
        ("province", "Province"),
    ]
    file_type = models.CharField(max_length=20, choices=FILE_CHOICES, null=True)
    file_upload = models.FileField(upload_to="maps")

    def __str__(self):
        return str(self.id)


class MunicipalityGeometry(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    area = models.FloatField(null=True, blank=True)
    bbox = models.JSONField(null=True, blank=True)
    geom = models.GeometryField(srid=4326, blank=True, null=True)
    attr_data = models.JSONField(default=dict, blank=True, null=True)

    objects = models.Manager()
    vector_tiles = MVTManager()

    def __str__(self):
        return str(self.id)


class ProvinceGeometry(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    area = models.FloatField(null=True, blank=True)
    bbox = models.JSONField(null=True, blank=True)
    geom = models.GeometryField(srid=4326, blank=True, null=True)
    attr_data = models.JSONField(default=dict, blank=True, null=True)

    objects = models.Manager()
    vector_tiles = MVTManager()

    def __str__(self):
        return str(self.id)


# END MAP


class MajorComponent(AuditableModel):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)
    description_en = RichTextField(blank=True, null=True)
    description_ne = RichTextField(blank=True, null=True)

    def __str__(self):
        return str(self.title_en)


class WeWorkWith(AuditableModel):
    PARTNER_CHOICES = (
        ("partner_and_collabrators", "Partner and Collabrators"),
        ("client", "Client"),
    )
    partner = models.CharField(
        max_length=50, choices=PARTNER_CHOICES, blank=True, null=True
    )
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)


class ContactUs(AuditableModel):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)


# ==================
# Use Case PAGE
# ==================


class UseCase(AuditableModel):
    USE_CASE_CHOICES = (
        ("municipal_management", "Municipal Management"),
        ("navigational_operations", "Navigational Operations"),
        ("data_management_and_centralization", "Data Management and Centralization"),
        (
            "geospatial_planning_and_visualization",
            "Geospatial Planning and Visualization",
        ),
    )
    use_case = models.CharField(
        max_length=50, choices=USE_CASE_CHOICES, blank=True, null=True
    )
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)
    description_en = RichTextField(blank=True, null=True)
    description_ne = RichTextField(blank=True, null=True)

    def __str__(self):
        return str(self.title_en)


# ==================
# Card
# ==================


class Card(models.Model):
    PAGE_CHOICES = (
        ("home", "Home"),
        ("use_case", "Use Case"),
        ("about", "About"),
        ("contact", "Contact"),
    )
    TYPE_CHOICES = (
        ("major_feature", "Major Feature"),
        ("major_component", "Major Component Case"),
        ("client", "We Work With: client"),
        ("partner_and_collabrators", "We Work With: Partner and Collabrators"),
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
        ("why_use_dmaps", "Why Use Dmaps"),
    )

    page = models.CharField(max_length=50, choices=PAGE_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)
    description_en = RichTextField(blank=True, null=True)
    description_ne = RichTextField(blank=True, null=True)
    icon = models.ImageField(blank=True, null=True, upload_to="icons/")

    benefit_en = RichTextField(blank=True, null=True)
    benefit_ne = RichTextField(blank=True, null=True)

    def __str__(self):
        return str(self.title_en)


class UseCaseDetail(models.Model):
    topic_en = models.CharField(max_length=500, blank=True, null=True)
    topic_ne = models.CharField(max_length=500, blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    funding_agency_en = models.CharField(max_length=500, blank=True, null=True)
    funding_agency_np = models.CharField(max_length=500, blank=True, null=True)
    area_en = models.CharField(max_length=500, blank=True, null=True)
    area_ne = models.CharField(max_length=500, blank=True, null=True)
    task_completed_en = RichTextField(blank=True, null=True)
    task_completed_ne = RichTextField(blank=True, null=True)
    use_case_card = models.OneToOneField(
        Card,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="use_case_detail",
    )

    def __str__(self):
        return str(self.topic_en) if self.topic_en else str(self.id)


class SDG(models.Model):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    description_ne = models.TextField(blank=True, null=True)
    use_case_card = models.OneToOneField(
        Card,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="use_case_sdg",
    )

    def __str__(self):
        return str(self.title_en) if self.title_en else str(self.id)


# ==================
# About PAGE
# ==================


class Intro(AuditableModel):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)
    description_en = RichTextField(blank=True, null=True)
    description_ne = RichTextField(blank=True, null=True)

    def __str__(self):
        return str(self.title_en)


class UseCaseMajorFeature(AuditableModel):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.title_en)


class WhyUseDmaps(AuditableModel):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)
    # card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, related_name="major_feature_card")


# ==================
# Contact PAGE
# ==================


class Collaborations(AuditableModel):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)


class Collaborator(AuditableModel):
    COLLABORATORS_CHOICES = (
        ("supporter", "Supporter"),
        ("mapping_partner", "Mapping Partner"),
        ("implementing_partner", " Implementing Partner"),
    )
    collaborator = models.CharField(
        max_length=100, choices=COLLABORATORS_CHOICES, null=True, blank=True
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    organization_name = models.CharField(max_length=200, null=True, blank=True)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    designation = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(null=True, blank=True)


class Collaboration(AuditableModel):
    title_en = models.CharField(max_length=200, null=True, blank=True)
    title_ne = models.CharField(max_length=200, null=True, blank=True)


# ==================
# FAQ PAGE
# ==================


class FAQ(models.Model):
    title_en = models.CharField(max_length=500, blank=True, null=True)
    title_ne = models.CharField(max_length=500, blank=True, null=True)
    description_en = models.TextField(blank=True, null=True)
    description_ne = models.TextField(blank=True, null=True)

    def __str__(self):
        return str(self.id)


class Image(models.Model):
    images = models.ImageField(blank=True, null=True, upload_to="images/")
    major_feature_images = models.ForeignKey(
        Card,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="major_feature_images",
    )


class SDGImage(models.Model):
    sdg_images = models.ImageField(blank=True, null=True, upload_to="sdg_images/")
    sdg_data = models.ForeignKey(
        SDG,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sdg_data",
    )
