import math
from django.db import models
from django.contrib.gis.db import models
from user.models import User
from django.db.models import JSONField, Manager as GeoManager
from core.utils.managers import LayerManager
from django.utils.translation import gettext_lazy as _
from .tile import MVTManager
from multiselectfield import MultiSelectField
from core.utils.constants import (
    DIRECTION_CHOICES,
    REGISTRATION_TYPE_CHOICES,
    STRUCTURE_CHOICES,
    USE_CHOICES,
    ROAD_CATEGORY_CHOICES,
    ROAD_CLASS_CHOICES,
    PALIKA_FILE_FORMAT_CHOICES,
    FILE_FORMAT_CHOICES,
    ASSOCIATION_TYPE_CHOICES,
    PAVEMENT_TYPE_CHOICES,
    ROOF_TYPE_CHOICES,
    NUMBERING_STATUS_CHOICES,
    OWNER_STATUS_CHOICES,
    TEMPRORARY_STATUS_CHOICES,
    VECTOR_LAYER_CATEGORY_CHOICES,
    DATA_GROUP_CHOICES,
    DATA_SOURCE_CHOICES,
    STATUS_CHOICES,
    ROAD_LANE_CHOICES,
    SPECIFIC_USE_CHOICES,
    BuildingFieldChoicesType,
    RoadfieldChoicesType,
)
from django.forms.models import model_to_dict
from shapely.geometry import mapping, shape
from django.contrib.gis.geos import GEOSGeometry, WKTWriter
import json
from shapely import wkt
from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import ast
from django.db import transaction
from datetime import datetime
from django.core.exceptions import ValidationError

# from .tile import MVTManager


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


class PalikaProfile(AuditableModel, models.Model):
    name_en = models.CharField(max_length=255, null=True, blank=True)
    name_ne = models.CharField(max_length=255, null=True, blank=True)
    description_en = models.CharField(max_length=1000, null=True, blank=True)
    description_ne = models.CharField(max_length=1000, null=True, blank=True)
    logo_en = models.ImageField(upload_to="palika_logo/", null=True, blank=True)
    logo_ne = models.ImageField(upload_to="palika_logo/", null=True, blank=True)

    def __str__(self) -> str:
        return super().__str__()


class PalikaGeometryFile(models.Model):
    file_type = models.CharField(
        max_length=20, choices=PALIKA_FILE_FORMAT_CHOICES, null=True
    )
    file_upload = models.FileField(upload_to="palika")

    def __str__(self):
        return str(self.id)


class PalikaGeometry(models.Model):
    area = models.FloatField(null=True, blank=True)
    bbox = models.JSONField(null=True, blank=True)
    geom = models.GeometryField(srid=4326, blank=True, null=True)

    objects = models.Manager()
    vector_tiles = MVTManager()

    def __str__(self):
        return str(self.id)


class PalikaWardGeometry(models.Model):
    ward_no = models.IntegerField(null=True, blank=True)
    numbering_status = models.CharField(
        max_length=20, choices=NUMBERING_STATUS_CHOICES, null=True, blank=True
    )
    area = models.FloatField(null=True, blank=True)
    bbox = models.JSONField(null=True, blank=True)
    geom = models.GeometryField(srid=4326, blank=True, null=True)

    objects = models.Manager()
    vector_tiles = MVTManager()

    def __str__(self):
        return str(self.id)


class RoadUpload(models.Model):
    file_type = models.CharField(max_length=20, choices=FILE_FORMAT_CHOICES, null=True)
    file_upload = models.FileField(upload_to="Files")

    def __str__(self):
        return str(self.id)


class RoadGeometry(models.Model):
    geom = models.GeometryField(srid=4326, blank=True, null=True)
    objects = models.Manager()
    vector_tiles = MVTManager()

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="road_geom_created",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="road_geom_updated",
    )
    is_deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def get_changes(self, previous_instance):
        changes = {}

        current_dict = model_to_dict(self)
        previous_dict = model_to_dict(previous_instance)

        for field, value in current_dict.items():
            if field == "timestamp":
                previous_timestamp = self.serialize_timestamp(
                    previous_dict.get(field), previous_instance
                )
                current_timestamp = self.serialize_timestamp(value, self)
                self.timestamp = current_timestamp

            elif field == "geom":
                current_geom = self.serialize_geom(value)
                previous_geom = self.serialize_geom(previous_dict.get(field))

                if current_geom != previous_geom:
                    changes[field] = current_geom

        return changes

    def serialize_timestamp(cls, timestamp, instance):
        """
        Serialize a datetime object to an ISO 8601 formatted timestamp string.
        """
        if timestamp:
            try:
                timestamp_str = ""

                if isinstance(timestamp, str):
                    timestamp_str = timestamp
                elif isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                return timestamp_str
            except Exception as e:
                raise ValidationError(f"Error serializing timestamp: {str(e)}")

    def serialize_geom(self, geom):
        """
        Serialize a geometry to a Well-Known Text (WKT) representation.
        """
        if geom:
            try:
                shapely_geom = GEOSGeometry(geom, srid=4326)
                wkt_representation = shapely_geom.wkt
                return wkt_representation
            except Exception as e:
                raise ValidationError(f"Error serializing geometry: {str(e)}")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            try:
                is_new = not self.pk
                if not is_new:
                    action = "update"
                    if self.timestamp:
                        HistoryLog.create_log(
                            action,
                            user=self.updated_by,
                            instance=self,
                            timestamp=self.timestamp,
                        )

                super().save(*args, **kwargs)

            except Exception as e:
                raise ValidationError(f"Error while saving RoadGeometry: {str(e)}")

    def __str__(self):
        return str(self.id)


class RoadCategoryChoice(models.Model):
    alias_name = models.CharField(max_length=100, blank=True, null=True)
    alias_name_ne = models.CharField(max_length=100, blank=True, null=True)
    attribute_name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(
        max_length=100, null=True, blank=True, choices=RoadfieldChoicesType
    )
    order = models.IntegerField(default=1, blank=True, null=True)

    def __str__(self):
        return f"{self.alias_name},{self.attribute_name},{self.type}"

    def save(self, *args, **kwargs):
        # Converting alias_name to lowercase and replacing spaces with underscores, and saving it to attribute_name
        if self.alias_name:
            self.attribute_name = self.alias_name.lower().replace(" ", "_")
        super().save(*args, **kwargs)


class Road(AuditableModel, models.Model):
    feature = models.OneToOneField(
        RoadGeometry,
        on_delete=models.CASCADE,
        related_name="road_geometry",
        blank=True,
        null=True,
    )
    road_name_en = models.CharField(max_length=500, null=True, blank=True)
    road_name_ne = models.CharField(max_length=500, null=True, blank=True)
    road_id = models.IntegerField(null=True, blank=True)
    road_type = models.CharField(max_length=20, choices=[], null=True, blank=True)
    road_category = models.CharField(max_length=20, choices=[], null=True, blank=True)
    road_class = models.CharField(max_length=30, choices=[], null=True, blank=True)
    road_lane = models.CharField(max_length=30, choices=[], null=True, blank=True)
    road_width = models.FloatField(null=True, blank=True)
    road_length = models.FloatField(null=True, blank=True)
    direction = models.CharField(max_length=50, null=True, blank=True)
    ward_no = JSONField(default=dict, null=True, blank=True)
    start_point = models.PointField(null=True, blank=True)
    end_point = models.PointField(null=True, blank=True)
    attr_data = JSONField(default=dict, blank=True, null=True)
    lat_field = models.CharField(max_length=250, blank=True, null=True)
    long_field = models.CharField(max_length=250, blank=True, null=True)
    remarks = models.CharField(max_length=50, null=True, blank=True)
    bbox = JSONField(default=dict, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    objects = models.Manager()
    vector_tiles = MVTManager()

    ROAD_CHOICES_FIELDS = ["road_type", "road_category", "road_class", "road_lane"]

    def __init__(self, *args, **kwargs):
        super(Road, self).__init__(*args, **kwargs)
        for field_name in self.ROAD_CHOICES_FIELDS:
            field = self._meta.get_field(field_name)
            field.choices = self.get_other_model_choices(field_name)

    def get_other_model_choices(self, type):
        other_model_choices = RoadCategoryChoice.objects.filter(type=type).values_list(
            "attribute_name", "alias_name"
        )
        return other_model_choices

    def get_changes(self, previous_instance):
        current_dict = model_to_dict(self)
        previous_dict = model_to_dict(previous_instance)

        changes = {}

        for field, value in current_dict.items():
            if field == "timestamp":
                previous_timestamp = self.serialize_timestamp(
                    previous_dict.get(field), previous_instance
                )
                current_timestamp = self.serialize_timestamp(value, self)
                self.timestamp = current_timestamp

            else:
                if field == "start_point" or "end_point":
                    current_point = getattr(self, field)
                    setattr(self, field, current_point)

                elif value != previous_dict.get(field):
                    changes[field] = {"old": previous_dict.get(field), "new": value}

        return changes

    def serialize_timestamp(cls, timestamp, instance):
        """
        Serialize a datetime object to an ISO 8601 formatted timestamp string.
        """
        if timestamp:
            try:
                timestamp_str = ""

                if isinstance(timestamp, str):
                    timestamp_str = timestamp
                elif isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                return timestamp_str
            except Exception as e:
                raise ValidationError(f"Error serializing timestamp: {str(e)}")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            try:
                is_new = not self.pk
                if not is_new:
                    action = "update"
                    if self.timestamp:
                        HistoryLog.create_log(
                            action,
                            user=self.updated_by,
                            instance=self,
                            timestamp=self.timestamp,
                        )
                else:
                    for field in self._meta.fields:
                        field_value = getattr(self, field.attname)
                        if isinstance(field_value, float) and math.isnan(field_value):
                            setattr(self, field.attname, None)
                super().save(*args, **kwargs)

            except Exception as e:
                raise ValidationError(f"Error while saving Road: {str(e)}")

    def delete(self, *args, **kwargs):
        """
        deletes the RoadGeometry when building instance is deleted
        """
        if self.feature:
            self.feature.delete()

        return super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class BuildingUpload(models.Model):
    file_type = models.CharField(max_length=20, choices=FILE_FORMAT_CHOICES, null=True)
    file_upload = models.FileField(upload_to="Files")

    def __str__(self):
        return str(self.id)


class BuildingCategoryChoice(models.Model):
    alias_name = models.CharField(max_length=100, blank=True, null=True)
    alias_name_ne = models.CharField(max_length=100, blank=True, null=True)
    attribute_name = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(
        max_length=100, null=True, blank=True, choices=BuildingFieldChoicesType
    )
    order = models.IntegerField(default=1, blank=True, null=True)

    def __str__(self):
        return f"{self.alias_name},{self.attribute_name}, {self.type}"

    def save(self, *args, **kwargs):
        # Converting alias_name to lowercase and replacing spaces with underscores, and saving it to attribute_name
        if self.alias_name:
            self.attribute_name = self.alias_name.lower().replace(" ", "_")
        super().save(*args, **kwargs)


class BuildingGeometry(models.Model):
    geom = models.GeometryField(srid=4326, blank=True, null=True)
    objects = models.Manager()
    vector_tiles = MVTManager()
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="geom_created",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="geom_updated",
    )
    timestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    def get_changes(self, previous_instance):
        changes = {}

        current_dict = model_to_dict(self)
        previous_dict = model_to_dict(previous_instance)

        for field, value in current_dict.items():
            if field == "timestamp":
                previous_timestamp = self.serialize_timestamp(
                    previous_dict.get(field), previous_instance
                )
                current_timestamp = self.serialize_timestamp(value, self)
                self.timestamp = current_timestamp

            elif field == "geom":
                current_geom = self.serialize_geom(value)
                previous_geom = self.serialize_geom(previous_dict.get(field))

                if current_geom != previous_geom:
                    changes[field] = current_geom

        return changes

    def serialize_timestamp(cls, timestamp, instance):
        """
        Serialize a datetime object to an ISO 8601 formatted timestamp string.
        """
        if timestamp:
            try:
                timestamp_str = ""

                if isinstance(timestamp, str):
                    timestamp_str = timestamp
                elif isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                return timestamp_str
            except Exception as e:
                raise ValidationError(f"Error serializing timestamp: {str(e)}")

    def serialize_geom(self, geom):
        """
        Serialize a geometry to a Well-Known Text (WKT) representation.
        """
        if geom:
            try:
                shapely_geom = GEOSGeometry(geom, srid=4326)
                wkt_representation = shapely_geom.wkt
                return wkt_representation
            except Exception as e:
                raise ValidationError(f"Error serializing geometry: {str(e)}")

    def save(self, *args, **kwargs):
        try:
            is_new = not self.pk
            if not is_new:
                action = "update"
                if self.timestamp:
                    HistoryLog.create_log(
                        action,
                        user=self.updated_by,
                        instance=self,
                        timestamp=self.timestamp,
                    )

            super().save(*args, **kwargs)

        except Exception as e:
            raise ValidationError(f"Error while saving BuildingGeometry: {str(e)}")


class Building(AuditableModel, models.Model):
    feature = models.OneToOneField(
        BuildingGeometry,
        on_delete=models.CASCADE,
        related_name="building_geometry",
        blank=True,
        null=True,
    )
    building_id = models.IntegerField(null=True, blank=True)
    road_id = models.IntegerField(null=True, blank=True)
    main_building_id = models.IntegerField(null=True, blank=True)
    centroid = models.PointField(null=True, blank=True)
    ref_centroid = models.PointField(null=True, blank=True)
    owner_status = models.CharField(max_length=20, choices=[], null=True, blank=True)
    temporary_type = models.CharField(max_length=20, choices=[], null=True, blank=True)
    association_type = models.CharField(
        max_length=20, choices=[], null=True, blank=True
    )
    roof_type = models.CharField(max_length=20, choices=[], null=True, blank=True)
    building_structure = models.CharField(
        max_length=50, choices=[], blank=True, null=True
    )
    reg_type = models.CharField(
        max_length=50,
        verbose_name="registration type",
        choices=[],
        blank=True,
        null=True,
    )
    building_use = models.CharField(max_length=50, choices=[], blank=True, null=True)
    building_sp_use = MultiSelectField(
        max_length=500, choices=[], blank=True, null=True
    )
    associate_road_name = models.CharField(max_length=50, blank=True, null=True)
    road_type = models.CharField(max_length=20, choices=[], null=True, blank=True)
    road_lane = models.CharField(max_length=20, choices=[], null=True, blank=True)
    road_width = models.FloatField(null=True, blank=True)
    direction = models.CharField(
        max_length=10, choices=DIRECTION_CHOICES, blank=True, null=True
    )
    gate_location = models.PointField(null=True, blank=True)
    house_no = models.CharField(max_length=255, null=True, blank=True)
    ward_no = models.IntegerField(null=True, blank=True)
    ward_no_informal = models.IntegerField(null=True, blank=True)
    floor = models.FloatField(null=True, blank=True)
    tole_name = models.CharField(max_length=200, null=True, blank=True)
    owner_name = models.CharField(max_length=30, null=True, blank=True)
    plinth_area = models.FloatField(null=True, blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    metric_address = models.CharField(
        max_length=254, blank=True, null=True, db_index=True
    )
    attr_data = JSONField(default=dict, blank=True, null=True)
    lat_field = models.CharField(max_length=250, blank=True, null=True)
    long_field = models.CharField(max_length=250, blank=True, null=True)
    plus_code = models.CharField(max_length=20, blank=True, null=True)
    bbox = JSONField(default=dict, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)

    objects = models.Manager()
    vector_tiles = MVTManager()

    BUILDING_CHOICES_FIELDS = [
        "owner_status",
        "temporary_type",
        "association_type",
        "roof_type",
        "building_structure",
        "reg_type",
        "building_use",
        "building_sp_use",
        "road_type",
        "road_lane",
    ]

    def __init__(self, *args, **kwargs):
        super(Building, self).__init__(*args, **kwargs)
        for field_name in self.BUILDING_CHOICES_FIELDS:
            field = self._meta.get_field(field_name)
            field.choices = self.get_other_model_choices(field_name)

    def get_other_model_choices(self, type):
        other_model_choices = BuildingCategoryChoice.objects.filter(
            type=type
        ).values_list("attribute_name", "alias_name")
        return other_model_choices

    def get_changes(self, previous_instance):
        current_dict = model_to_dict(self)
        previous_dict = model_to_dict(previous_instance)

        changes = {}

        for field, value in current_dict.items():
            current_ref_centroid = previous_ref_centroid = None

            if field == "timestamp":
                previous_timestamp = self.serialize_timestamp(
                    previous_dict.get(field), previous_instance
                )
                current_timestamp = self.serialize_timestamp(value, self)
                self.timestamp = current_timestamp

            elif field == "ref_centroid":
                current_ref_centroid = self.serialize_ref_centroid(value, self)
                previous_ref_centroid = self.serialize_ref_centroid(
                    previous_dict.get(field), previous_instance
                )

                if current_ref_centroid != previous_ref_centroid:
                    changes[field] = {
                        "old": previous_ref_centroid,
                        "new": current_ref_centroid,
                    }
            else:
                if value != previous_dict.get(field):
                    changes[field] = {"old": previous_dict.get(field), "new": value}

        return changes

    def serialize_timestamp(cls, timestamp, instance):
        """
        Serialize a datetime object to an ISO 8601 formatted timestamp string.
        """
        if timestamp:
            try:
                timestamp_str = ""

                if isinstance(timestamp, str):
                    timestamp_str = timestamp
                elif isinstance(timestamp, datetime):
                    timestamp_str = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

                return timestamp_str
            except Exception as e:
                raise ValidationError(f"Error serializing timestamp: {str(e)}")

    def serialize_ref_centroid(cls, ref_centroid, instance):
        """
        Serialize a ref_centroid geometry to a GeoJSON-like dictionary.
        """
        if ref_centroid:
            try:
                shapely_ref_centroid = GEOSGeometry(ref_centroid, srid=4326)
                wkt = shapely_ref_centroid.wkt
                return wkt
            except Exception as e:
                raise ValidationError(f"Error serializing ref_centroid: {str(e)}")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            try:
                is_new = not self.pk

                if not is_new:
                    action = "update"
                    if self.timestamp:
                        HistoryLog.create_log(
                            action,
                            user=self.updated_by,
                            instance=self,
                            timestamp=self.timestamp,
                        )

                super().save(*args, **kwargs)

            except Exception as e:
                raise ValidationError(f"Error while saving Building: {str(e)}")

    def delete(self, *args, **kwargs):
        """
        deletes the buildinggeometry when building instance is deleted
        """
        if self.feature:
            self.feature.delete()

        return super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class Image(models.Model):
    image_choice = [
        ("building_image", "Building Image"),
        ("building_plan", "Building Plan"),
    ]
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="building_id",
    )
    image_type = models.CharField(max_length=20, choices=image_choice)
    image = models.ImageField(upload_to="Files/images", null=True, blank=True)


class PhysicalInstallation(AuditableModel, models.Model):
    planned = models.IntegerField(null=True, blank=True)
    installed = models.IntegerField(null=True, blank=True)
    remaining = models.IntegerField(null=True, blank=True)
    eta = models.IntegerField(null=True, blank=True)
    planned_date = models.DateField(null=True, blank=True)
    updated_date = models.DateField(auto_now=True, null=True, blank=True)
    objects = models.Manager()

    def __str__(self):
        return str(self.id)


# class LayerCategory(models.Model):
#     name = models.CharField(max_length=100)
#     category = models.CharField(max_length=100, choices=VECTOR_LAYER_CATEGORY_CHOICES, null=True, blank=True)
#     objects = models.Manager()

#     def __str__(self):
#         return str(self.id)


class VectorLayer(AuditableModel, models.Model):
    layer_name = models.CharField(max_length=100, blank=True, null=True)
    display_name_en = models.CharField(max_length=100, blank=True, null=True)
    display_name_ne = models.CharField(max_length=100, blank=True, null=True)
    description_en = models.CharField(max_length=500, blank=True, null=True)
    description_ne = models.CharField(max_length=500, blank=True, null=True)
    category = models.CharField(
        max_length=100, choices=VECTOR_LAYER_CATEGORY_CHOICES, null=True, blank=True
    )
    data_group = models.CharField(
        max_length=100, choices=DATA_GROUP_CHOICES, null=True, blank=True
    )
    data_source = models.CharField(
        max_length=20, choices=DATA_SOURCE_CHOICES, null=True, blank=True
    )
    file_upload = models.FileField(upload_to="Files", null=True, blank=True)
    lat_field = models.CharField(max_length=250, null=True, blank=True, default="")
    long_field = models.CharField(max_length=250, null=True, blank=True, default="")
    bbox = JSONField(default=dict, null=True, blank=True)
    geometry_type = models.CharField(max_length=250, null=True, blank=True)
    is_downloadable = models.BooleanField(default=True)
    is_boundary_data = models.BooleanField(default=True)
    is_open_space_layer = models.BooleanField(default=True)
    is_there_metadata = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    default_load = models.BooleanField(default=False)
    objects = models.Manager()
    public_objects = LayerManager()

    def __str__(self):
        return str(self.id)


class VectorLayerStyle(AuditableModel, models.Model):
    layer = models.ForeignKey(
        VectorLayer, on_delete=models.CASCADE, related_name="vector_layer_style"
    )
    style_json = JSONField(blank=True, null=True)
    icon_size = models.JSONField(default=dict, blank=True, null=True)
    show_label = models.BooleanField(default=False)
    label_field = models.CharField(max_length=100, blank=True, null=True)
    label_style = models.JSONField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return str(self.id)


class FeatureCollection(AuditableModel, models.Model):
    vector_layer = models.ForeignKey(
        VectorLayer,
        on_delete=models.CASCADE,
        related_name="feature",
        null=True,
        blank=True,
    )
    attr_data = JSONField(default=dict, null=True, blank=True)
    geom = models.GeometryField(srid=4236, null=True, blank=True)
    objects = models.Manager()
    vector_tiles = MVTManager()

    def __str__(self):
        return str(self.id)

    def get_geometry_type(self):
        return self.geom.geom_type


class RasterLayer(AuditableModel, models.Model):
    """
    A raster is a grid-based representation of geographic data. This model stores information about the raster file,
    associated layer, attribute data, and ID.

    """

    name_en = models.CharField(max_length=50, blank=True, null=True)
    name_ne = models.CharField(max_length=50, blank=True, null=True)
    raster_file = models.FileField(upload_to="raster/")
    sld_file = models.FileField(upload_to="raster/sld_uploads", null=True, blank=True)
    attr_data = JSONField(default=dict, blank=True, null=True)
    status = models.CharField(
        max_length=15, blank=True, null=True, choices=STATUS_CHOICES
    )
    # icon = models.FileField(upload_to="icons", blank=True, null=True, validators=[validate_icon_extension])
    display_on_map = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    objects = GeoManager()

    def __str__(self):
        return str(self.id)


class RasterLayerMetadata(models.Model):
    """
    Stores meta data for a raster layer
    """

    rasterlayer = models.ForeignKey(
        RasterLayer, on_delete=models.CASCADE, related_name="raster_layer_metadata"
    )
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    numbands = models.IntegerField(null=True, blank=True)
    srid = models.PositiveSmallIntegerField(null=True, blank=True)
    extent = JSONField(blank=True, null=True)
    legend = JSONField(blank=True, null=True)
    stats = JSONField(blank=True, null=True)
    pixel_size = models.FloatField(default=0)
    minx = models.FloatField(default=0)
    maxx = models.FloatField(default=0)
    file_name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.rasterlayer.raster_file.name


class HistoryLog(models.Model):
    ACTION_CHOICES = (
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    object_id = models.PositiveIntegerField()
    association_id = models.IntegerField(
        null=True, blank=True
    )  # To view every changes made in Building or Road and their related geometry
    content_object = GenericForeignKey("content_type", "object_id")
    timestamp = models.DateTimeField(null=True, blank=True)
    related_id = models.IntegerField(
        null=True, blank=True
    )  # To ensure Road or Building when edited are linked with their respective geometries when geom and attributes are changed together
    changes = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp}"

    @classmethod
    def create_log(cls, action, user, instance, timestamp):
        content_type = ContentType.objects.get_for_model(instance)
        object_id = instance.pk

        previous_instance = instance.__class__.objects.get(pk=instance.pk)
        changes = instance.get_changes(previous_instance)
        for change in changes:
            if change is not {}:
                related_logs = None
                related_id = None

                if isinstance(instance, (Building, BuildingGeometry)):
                    if isinstance(instance, BuildingGeometry):
                        building_instance = Building.objects.get(feature=object_id)
                        association_id = building_instance.id
                    else:
                        association_id = object_id
                    related_logs = cls.objects.filter(
                        timestamp=timestamp,
                        content_type__in=[
                            ContentType.objects.get_for_model(Building),
                            ContentType.objects.get_for_model(BuildingGeometry),
                        ],
                    ).exclude(object_id=object_id)

                if isinstance(instance, (Road, RoadGeometry)):
                    if isinstance(instance, RoadGeometry):
                        road_instance = Road.objects.get(feature=object_id)
                        association_id = road_instance.id
                    else:
                        association_id = object_id
                    related_logs = cls.objects.filter(
                        timestamp=timestamp,
                        content_type__in=[
                            ContentType.objects.get_for_model(Road),
                            ContentType.objects.get_for_model(RoadGeometry),
                        ],
                    ).exclude(object_id=object_id)

                if related_logs.exists():
                    related_id = related_logs.first().related_id
                    if related_id is None:
                        related_id = related_logs.first().id

                log = cls.objects.create(
                    user=user,
                    action=action,
                    content_type=content_type,
                    object_id=object_id,
                    content_object=instance,
                    timestamp=timestamp,
                    related_id=related_id,
                    association_id=association_id,
                    changes=changes,
                )
                if related_id is None:
                    log.related_id = log.id
                    log.save()

            return log
