from rest_framework import serializers
from core.models import *

# ==================================================
# Palika
# ==================================================


class PalikaProfileSerializer(serializers.ModelSerializer):
    bbox = serializers.SerializerMethodField()

    class Meta:
        model = PalikaProfile
        fields = "__all__"
        read_only = ["id"]

    def get_bbox(self, obj):
        bbox = PalikaGeometry.objects.all().values("bbox")[0]["bbox"]
        return bbox


class PalikaGeometryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PalikaGeometryFile
        fields = "__all__"
        read_only = ["id"]


class PalikaGeometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PalikaGeometry
        fields = "__all__"
        read_only = ["id"]


class PalikaWardGeometrySerializer(serializers.ModelSerializer):
    buildings = serializers.SerializerMethodField()
    density = serializers.SerializerMethodField()

    class Meta:
        model = PalikaWardGeometry
        fields = [
            "id",
            "ward_no",
            "numbering_status",
            "area",
            "bbox",
            "buildings",
            "density",
        ]
        read_only = ["id"]

    def get_buildings(self, obj):
        buildings = BuildingGeometry.objects.filter(geom__within=obj.geom).count()
        return buildings

    def get_density(self, obj):
        buildings = BuildingGeometry.objects.filter(geom__within=obj.geom).count()
        area = obj.area
        density = round(buildings / area, 4)
        return density


# ==================================================
# Road
# ==================================================


class RoadUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadUpload
        fields = "__all__"
        read_only = ["id"]


class RoadPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Road
        fields = [
            "id",
            "road_id",
            "road_name_en",
            "road_name_ne",
            "road_type",
            "road_category",
            "road_class",
            "road_lane",
            "road_width",
            "remarks",
            "start_point",
            "end_point",
            "road_length",
        ]
        read_only = ["id"]

    def create(self, validated_data):
        # Check if 'road_id' is not set or is None
        if validated_data.get("road_id") is None:
            # Get the maximum value of road_id from the database
            max_road_id = Road.objects.aggregate(models.Max("road_id"))["road_id__max"]
            max_road_id = (max_road_id + 1) if max_road_id is not None else 1

            # Set the calculated 'road_id'
            validated_data["road_id"] = max_road_id

        # Create the instance using the original create method
        instance = super().create(validated_data)

        return instance


class RoadDetailSerializer(serializers.ModelSerializer):
    ward_no = serializers.SerializerMethodField()
    bbox = serializers.SerializerMethodField()
    assoc_build_no = serializers.SerializerMethodField()
    feature_id = serializers.IntegerField(source="feature.id", read_only=True)

    class Meta:
        model = Road
        fields = [
            "id",
            "feature_id",
            "road_name_en",
            "ward_no",
            "road_category",
            "road_type",
            "road_lane",
            "road_length",
            "road_width",
            "bbox",
            "assoc_build_no",
            "road_class",
            "start_point",
            "direction",
            "road_id",
            "remarks",
        ]
        read_only = ["id"]

    def get_bbox(self, instance):
        bbox = instance.feature.geom.extent
        return bbox

    def get_assoc_build_no(self, instance):
        road_id = instance.road_id
        building_count = Building.objects.filter(road_id=road_id).count()
        return building_count

    def get_ward_no(self, instance):
        ward_no = instance.ward_no
        return ward_no if ward_no else []


class RoadListSerializer(serializers.ModelSerializer):
    road_type = serializers.CharField(source="get_road_type_display")
    road_category = serializers.CharField(source="get_road_category_display")
    bbox = serializers.SerializerMethodField()
    ward_no = serializers.SerializerMethodField()

    class Meta:
        model = Road
        fields = [
            "id",
            "road_id",
            "road_name_en",
            "road_type",
            "road_category",
            "ward_no",
            "bbox",
            "updated_date",
        ]
        read_only = ["id"]

    def get_bbox(self, instance):
        bbox = instance.feature.geom.extent
        return bbox

    def get_ward_no(self, instance):
        ward_no = instance.ward_no
        return ward_no if ward_no else []


class RoadPopUpSerializer(serializers.ModelSerializer):
    road_type = serializers.CharField(source="get_road_type_display")
    road_category = serializers.CharField(source="get_road_category_display")
    road_class = serializers.CharField(source="get_road_class_display")
    start_point = serializers.SerializerMethodField()
    ward_no = serializers.SerializerMethodField()

    def get_start_point(self, instance):
        start_point = instance.start_point
        if start_point:
            return start_point.coords

    def get_ward_no(self, instance):
        ward_no = instance.ward_no
        if isinstance(ward_no, list) and len(ward_no) > 0:
            ward_no = ",".join(map(str, ward_no))
        elif isinstance(ward_no, dict) and len(ward_no) == 0:
            return []
        return ward_no

    class Meta:
        model = Road
        fields = [
            "road_name_en",
            "ward_no",
            "road_category",
            "road_length",
            "road_width",
            "start_point",
            "direction",
            "road_type",
            "road_class",
            "remarks",
            "road_id",
        ]


class RoadUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Road
        fields = [
            "road_name_en",
            "road_name_ne",
            "road_type",
            "road_category",
            "is_deleted",
            "road_width",
            "road_class",
            "road_lane",
            "remarks",
            "timestamp",
        ]


class RoadGeometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoadGeometry
        fields = "__all__"
        read_only = ["id"]


class RoadPublicPopUpSerializer(serializers.ModelSerializer):
    road_type = serializers.CharField(source="get_road_type_display")
    road_category = serializers.CharField(source="get_road_category_display")
    road_class = serializers.CharField(source="get_road_class_display")
    start_point = serializers.SerializerMethodField()
    ward_no = serializers.SerializerMethodField()

    def get_start_point(self, instance):
        start_point = instance.start_point
        if start_point:
            return start_point.coords

    def get_ward_no(self, instance):
        ward_no = instance.ward_no
        if isinstance(ward_no, list) and len(ward_no) > 0:
            ward_no = ",".join(map(str, ward_no))
        elif isinstance(ward_no, dict) and len(ward_no) == 0:
            return []
        return ward_no

    class Meta:
        model = Road
        fields = [
            "road_name_en",
            "ward_no",
            "road_category",
            "road_length",
            "road_width",
            "start_point",
            "direction",
            "road_type",
            "road_class",
            "remarks",
            "road_id",
        ]


# ==================================================
# Building
# ==================================================


class BuildingUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingUpload
        fields = "__all__"
        read_only = ["id"]


class BuildingPostSerializer(serializers.ModelSerializer):
    def validate_floor(self, value):
        """
        Validate that the floor count is a multiple of 0.5.
        """
        if value % 0.5 == 0 and value != 0.5:
            return value

        raise serializers.ValidationError(
            "Floor must be a multiple of 0.5 (e.g., 0, 1, 1.5, 2, 2.5, etc.) and not equal to 0.5."
        )

    class Meta:
        model = Building
        fields = [
            "id",
            "house_no",
            "main_building_id",
            "road_id",
            "owner_name",
            "tole_name",
            "direction",
            "gate_location",
            "association_type",
            "building_structure",
            "owner_status",
            "temporary_type",
            "roof_type",
            "reg_type",
            "building_use",
            "plinth_area",
            "road_width",
            "road_type",
            "associate_road_name",
            "floor",
            "remarks",
        ]
        read_only = ["id"]

    def to_representation(self, instance):
        # Check if 'building_id' is not set or is None
        if instance.building_id is None:
            # Calculate the next 'building_id' based on the latest one in the database
            max_building_id = Building.objects.aggregate(models.Max("building_id"))[
                "building_id__max"
            ]
            building_id = (max_building_id + 1) if max_building_id is not None else 1
            instance.building_id = building_id
            instance.save()

        return super().to_representation(instance)


class BuildingListSerializer(serializers.ModelSerializer):
    reg_type = serializers.CharField(source="get_reg_type_display")
    association_type = serializers.CharField(source="get_association_type_display")
    bbox = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = [
            "id",
            "house_no",
            "building_id",
            "owner_name",
            "tole_name",
            "reg_type",
            "bbox",
            "association_type",
            "ward_no",
            "ward_no_informal",
            "associate_road_name",
            "road_width",
            "plus_code",
            "building_sp_use",
            "lat_field",
            "long_field",
            "updated_date",
        ]
        read_only = ["id"]

    def get_bbox(self, instance):
        bbox = instance.feature.geom.extent
        return bbox

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Extract latitude and longitude from the centroid
        if instance.centroid:
            centroid = instance.centroid
            representation["lat_field"] = centroid.y
            representation["long_field"] = centroid.x

        return representation


class BuildingPopUpSerializer(serializers.ModelSerializer):
    reg_type = serializers.CharField(source="get_reg_type_display")
    building_use = serializers.CharField(source="get_building_use_display")
    building_structure = serializers.CharField(source="get_building_structure_display")
    owner_status = serializers.CharField(source="get_owner_status_display")
    temporary_type = serializers.CharField(source="get_temporary_type_display")
    building_image = serializers.ImageField(
        source="images.building_image", read_only=True
    )

    class Meta:
        model = Building
        fields = [
            "id",
            "house_no",
            "building_id",
            "ward_no",
            "ward_no_informal",
            "tole_name",
            "plus_code",
            "owner_status",
            "reg_type",
            "building_use",
            "plinth_area",
            "building_structure",
            "floor",
            "temporary_type",
            "direction",
            "gate_location",
            "owner_name",
            "building_image",
            "remarks",
            "associate_road_name",
            "road_id",
        ]


class BuildingUpdateSerializer(serializers.ModelSerializer):
    associate_road_name = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = [
            "house_no",
            "tole_name",
            "main_building_id",
            "roof_type",
            "association_type",
            "associate_road_name",
            "gate_location",
            "reg_type",
            "temporary_type",
            "floor",
            "road_type",
            "road_lane",
            "road_width",
            "road_id",
            "building_structure",
            "remarks",
            "owner_name",
            "owner_status",
            "building_use",
            "plinth_area",
            "is_deleted",
            "timestamp",
            "ref_centroid",
        ]

    def get_associate_road_name(self, obj):
        if obj.road_id:
            road = Road.objects.get(road_id=obj.road_id)
            return road.road_name_en


class BuildingDetailSerializer(serializers.ModelSerializer):
    informant_name = serializers.CharField(source="attr_data.informant", read_only=True)
    informant_contact = serializers.CharField(source="attr_data.ph_no", read_only=True)
    bbox = serializers.SerializerMethodField()
    feature_id = serializers.IntegerField(source="feature.id", read_only=True)

    class Meta:
        model = Building
        fields = [
            "feature_id",
            "house_no",
            "building_id",
            "main_building_id",
            "ward_no",
            "ward_no_informal",
            "tole_name",
            "plus_code",
            "owner_status",
            "road_type",
            "building_use",
            "reg_type",
            "bbox",
            "associate_road_name",
            "association_type",
            "plinth_area",
            "building_structure",
            "roof_type",
            "floor",
            "lat_field",
            "long_field",
            "centroid",
            "ref_centroid",
            "temporary_type",
            "building_sp_use",
            "gate_location",
            "owner_name",
            "remarks",
            "road_id",
            "road_width",
            "road_lane",
            "informant_name",
            "informant_contact",
        ]
        read_only = ["id"]

    def get_bbox(self, instance):
        bbox = instance.feature.geom.extent
        return bbox

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Extract latitude and longitude from the centroid
        if instance.centroid:
            centroid = instance.centroid
            representation["lat_field"] = centroid.y
            representation["long_field"] = centroid.x

        return representation


class BuildingGeometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BuildingGeometry
        fields = "__all__"
        read_only = ["id"]


class BuildingPublicListSerializer(serializers.ModelSerializer):
    bbox = serializers.SerializerMethodField()

    class Meta:
        model = Building
        fields = [
            "id",
            "ward_no",
            "plus_code",
            "house_no",
            "association_type",
            "associate_road_name",
            "bbox",
        ]

    def get_bbox(self, instance):
        bbox = instance.feature.geom.extent
        return bbox


class BuildingPublicPopUpSerializer(serializers.ModelSerializer):
    building_structure = serializers.CharField(source="get_building_structure_display")
    owner_status = serializers.CharField(source="get_owner_status_display")

    class Meta:
        model = Building
        fields = [
            "id",
            "house_no",
            "ward_no",
            "tole_name",
            "plus_code",
            "owner_name",
            "building_structure",
            "floor",
            "owner_status",
            "remarks",
            "associate_road_name",
        ]


# ==================================================
# Building_Image
# ==================================================


class ImageListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = [
            "image",
        ]
        read_only = ["id"]

    def get_image(self, obj):
        if obj.image:
            return self.context["request"].build_absolute_uri(obj.image.url)
        return None


class ImagePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["building", "image_type", "image"]
        read_only = ["id"]


class PhysicalInstallationPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalInstallation
        fields = ["planned", "installed", "planned_date", "updated_date", "remaining"]
        read_only = ["id"]


class PhysicalInstallationGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalInstallation
        fields = "__all__"
        read_only = ["id"]


class StatisticsSerializer(serializers.Serializer):
    building_count = serializers.IntegerField()
    road_count = serializers.IntegerField()
    built_up_area_sq_km = serializers.FloatField()


class VectorLayerStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorLayerStyle
        fields = "__all__"
        read_only = ["id"]


class VectorLayerPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorLayer
        fields = "__all__"
        read_only = ["id"]


class VectorLayerDetailSerializer(serializers.ModelSerializer):
    style = serializers.SerializerMethodField()

    class Meta:
        model = VectorLayer
        fields = "__all__"
        read_only = ["id"]

    def get_style(self, obj):
        vector_style = VectorLayerStyle.objects.filter(layer=obj.id).first()
        return vector_style.style_json if vector_style else None


class VectorLayerListSerializer(serializers.ModelSerializer):
    count = serializers.SerializerMethodField()
    style = serializers.SerializerMethodField()

    class Meta:
        model = VectorLayer
        fields = [
            "id",
            "display_name_en",
            "category",
            "data_group",
            "data_source",
            "count",
            "is_public",
            "is_downloadable",
            "default_load",
            "style",
            "geometry_type",
        ]

    def get_count(self, obj):
        return obj.feature.count()

    def get_style(self, obj):
        vector_style = VectorLayerStyle.objects.filter(layer=obj.id).first()
        return vector_style.style_json if vector_style else None


class VectorLayerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VectorLayer
        fields = [
            "layer_name",
            "display_name_en",
            "display_name_ne",
            "description_en",
            "description_ne",
            "category",
            "data_group",
            "data_source",
            "is_downloadable",
            "is_public",
            "default_load",
            "is_there_metadata",
        ]

    def create(self, validated_data):
        style_data = validated_data.pop("style", None)
        instance = super().create(validated_data)

        if style_data:
            VectorLayerStyle.objects.create(layer=instance, style_json=style_data)

        return instance


class RasterLayerPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = RasterLayer
        fields = "__all__"
        read_only = ["id"]


class RasterLayerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RasterLayer
        fields = "__all__"
        read_only = ["id"]


class RasterLayerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RasterLayer
        fields = [
            "name_en",
            "name_ne",
        ]


class RasterTileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RasterLayer
        fields = ["name_en", "sld_file", "status", "display_on_map", "is_public"]
        read_only_fields = ["id"]


class HouseNumberRequestSerializer(serializers.Serializer):
    data_id = serializers.IntegerField()

    class Meta:
        fields = "__all__"


class LineStringSerializer(serializers.Serializer):
    class Meta:
        models = Road
        fields = "__all__"


class HistoryLogSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = HistoryLog
        exclude = ["user", "content_type"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if "changes" in data:
            data["changes"].pop("updated_by", None)
        return data


class BuildingBasicFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["ward_no", "tole_name", "owner_status", "reg_type"]
