from api.serializers.core_serializers import BuildingListSerializer
from django.contrib import admin
import geopandas as gpd
from user.admin import export_as_csv
from core.script import house_numbering
from django.conf import settings
from .models import (
    Road,
    Building,
    RoadGeometry,
    BuildingGeometry,
    BuildingUpload,
    RoadUpload,
    PalikaProfile,
    PalikaGeometryFile,
    PalikaGeometry,
    PalikaWardGeometry,
    PhysicalInstallation,
    VectorLayer,
    FeatureCollection,
    RasterLayer,
    BuildingCategoryChoice,
    Image,
    RoadCategoryChoice,
    VectorLayerStyle,
    HistoryLog,
)


def make_house_number_null(modeladmin, request, queryset):
    queryset.update(house_no=None)


def generate_house_number(modeladmin, request, queryset):
    for house in queryset:
        house_numbering(data_id=house.id)


make_house_number_null.short_description = "Make house number of selected data null"
generate_house_number.short_description = (
    "Generate house number of selected house data collection"
)


# Register your models here.
class RoadAdmin(admin.ModelAdmin):
    actions = [export_as_csv]
    list_display = [
        "id",
        "road_id",
        "road_name_en",
        "road_category",
        "road_type",
        "ward_no",
    ]
    list_filter = ["road_category", "road_type", "ward_no", "road_lane", "direction"]
    search_fields = ["id", "road_name_en", "road_id"]


class BuildingAdmin(admin.ModelAdmin):
    actions = [export_as_csv, make_house_number_null, generate_house_number]
    list_display = [
        "id",
        "house_no",
        "building_id",
        "main_building_id",
        "tole_name",
        "ward_no",
        "association_type",
        "road_id",
        "plus_code",
    ]
    list_filter = [
        "association_type",
        "building_use",
        "temporary_type",
        "roof_type",
        "building_structure",
        "ward_no",
        "tole_name",
        # "house_no",
    ]
    search_fields = [
        "id",
        "building_id",
        "main_building_id",
        "associate_road_name",
        "tole_name",
        "owner_name",
        "metric_address",
        "house_no",
    ]


class VectorLayerAdmin(admin.ModelAdmin):
    actions = [export_as_csv]
    list_display = [
        "id",
        "display_name_en",
        "description_en",
        "category",
        "data_group",
        "data_source",
    ]
    list_filter = [
        "display_name_en",
        "category",
        "data_group",
    ]


class BuildingCategoryChoiceAdmin(admin.ModelAdmin):
    actions = [export_as_csv]
    list_display = [
        "id",
        "alias_name",
        "alias_name_ne",
        "attribute_name",
        "type",
        "order",
    ]
    list_filter = [
        "type",
    ]
    search_fields = [
        "attribute_name",
        "type",
    ]


class RoadCategoryChoiceAdmin(admin.ModelAdmin):
    actions = [export_as_csv]
    list_display = [
        "id",
        "alias_name",
        "alias_name_ne",
        "attribute_name",
        "type",
        "order",
    ]
    list_filter = [
        "type",
    ]
    search_fields = [
        "attribute_name",
        "type",
    ]


class RoadGeometryAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class BuildingGeometryAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class BuildingUploadAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class PhysicalInstallationAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class RoadUploadAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class PalikaProfileAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class PalikaGeometryFileAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class PalikaGeometryAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class PalikaWardGeometryAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class FeatureCollectionAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class RasterLayerAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class ImageAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


class Admin(admin.ModelAdmin):
    actions = [export_as_csv]


class VectorLayerStyleAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "get_layer_name",
        "style_json",
        "label_field",
    ]

    def get_layer_name(self, obj):
        return obj.layer.layer_name

    get_layer_name.short_description = "Layer Name"


class HistoryLogAdmin(admin.ModelAdmin):
    actions = [export_as_csv]
    list_display = [
        "id",
        "related_id",
        "timestamp",
        "association_id",
        "content_type",
        "object_id",
        "changes",
    ]
    list_filter = [
        "related_id",
        "action",
        "content_type",
        "association_id",
    ]
    search_fields = [
        "id",
        "related_id",
        "action",
        "content_type",
        "object_id",
        "association_id",
    ]


admin.site.site_header = "D-MAPs Admin Panel"

admin.site.register(RoadCategoryChoice, RoadCategoryChoiceAdmin)
admin.site.register(BuildingCategoryChoice, BuildingCategoryChoiceAdmin)
admin.site.register(BuildingUpload, BuildingUploadAdmin)
admin.site.register(PhysicalInstallation, PhysicalInstallationAdmin)
admin.site.register(RoadUpload, RoadUploadAdmin)
admin.site.register(Road, RoadAdmin)
admin.site.register(RoadGeometry, RoadGeometryAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(BuildingGeometry, BuildingGeometryAdmin)
admin.site.register(PalikaProfile, PalikaProfileAdmin)
admin.site.register(PalikaGeometryFile, PalikaGeometryFileAdmin)
admin.site.register(PalikaGeometry, PalikaGeometryAdmin)
admin.site.register(PalikaWardGeometry, PalikaWardGeometryAdmin)
admin.site.register(VectorLayer, VectorLayerAdmin)
admin.site.register(FeatureCollection, FeatureCollectionAdmin)
admin.site.register(RasterLayer, RasterLayerAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(VectorLayerStyle, VectorLayerStyleAdmin)
admin.site.register(HistoryLog, HistoryLogAdmin)
