import django_filters
from django_filters import rest_framework as df_filters
from django_filters.fields import CSVWidget, MultipleChoiceField
from core.models import Road, Building, VectorLayer, BuildingGeometry, RoadGeometry
from django.db.models import Q


class MultipleField(MultipleChoiceField):
    def valid_value(self, value):
        return True


class MultipleFilter(df_filters.MultipleChoiceFilter):
    field_class = MultipleField


class RoadFilter(django_filters.FilterSet):
    id = MultipleFilter(field_name="id", lookup_expr="exact", widget=CSVWidget)
    road_type = MultipleFilter(
        field_name="road_type", lookup_expr="exact", widget=CSVWidget
    )

    class Meta:
        model = Road
        fields = ["id", "road_type"]

    def filter_queryset(self, queryset):
        params = self.data
        q_obj = Q()
        if "ward_no" in params and params["ward_no"]:
            q_obj = Q()
            ward_numbers = params.get("ward_no")
            ward_no_values = [int(value) for value in ward_numbers.split(",")]
            for ward_no_value in ward_no_values:
                q_obj |= Q(ward_no__contains=ward_no_value)
            queryset = queryset.filter(q_obj)
        if "road_type" in params and params["road_type"]:
            field_name = "road_type"
            value = params.get("road_type")
            values = value.split(",") if "," in value else [value]
            q_obj = Q(**{f"{field_name}__in": values})
            queryset = queryset.filter(q_obj)

        return queryset


class BuildingFilter(django_filters.FilterSet):
    id = MultipleFilter(field_name="id", lookup_expr="exact", widget=CSVWidget)
    ward_no = MultipleFilter(
        field_name="ward_no", lookup_expr="exact", widget=CSVWidget
    )
    tole_name = MultipleFilter(
        field_name="tole_name", lookup_expr="icontains", widget=CSVWidget
    )
    reg_type = MultipleFilter(
        field_name="reg_type", lookup_expr="exact", widget=CSVWidget
    )
    # owner_name = django_filters.CharFilter(field_name="owner_name", lookup_expr="icontains")

    class Meta:
        model = Building
        fields = ["id", "ward_no", "house_no", "tole_name", "reg_type", "owner_name"]


class VectorLayerFilter(django_filters.FilterSet):
    class Meta:
        model = VectorLayer
        fields = ["display_name_en", "category", "data_group"]


class BuildingVectorTileFilter(django_filters.FilterSet):
    building_id = MultipleFilter(
        field_name="building_geometry__id",
        lookup_expr="exact",
        widget=CSVWidget,
    )
    ward_no = MultipleFilter(
        field_name="building_geometry__ward_no",
        lookup_expr="exact",
        widget=CSVWidget,
    )
    tole_name = MultipleFilter(
        field_name="building_geometry__tole_name",
        lookup_expr="icontains",
        widget=CSVWidget,
    )
    reg_type = MultipleFilter(
        field_name="building_geometry__reg_type",
        lookup_expr="icontains",
        widget=CSVWidget,
    )
    association_type = MultipleFilter(
        field_name="building_geometry__association_type",
        lookup_expr="icontains",
        widget=CSVWidget,
    )
    owner_status = MultipleFilter(
        field_name="building_geometry__owner_status",
        lookup_expr="exact",
        widget=CSVWidget,
    )
    building_category = MultipleFilter(
        field_name="building_geometry__building_sp_use",
        lookup_expr="icontains",
        widget=CSVWidget,
    )
    road_type = MultipleFilter(
        field_name="building_geometry__road_type",
        lookup_expr="icontains",
        widget=CSVWidget,
    )

    class Meta:
        model = BuildingGeometry
        fields = [
            "building_id",
            "ward_no",
            "tole_name",
            "reg_type",
            "association_type",
            "owner_status",
            "building_category",
            "road_type",
        ]


class RoadVectorTileFilter(django_filters.FilterSet):
    road_id = MultipleFilter(
        field_name="road_geometry__id", lookup_expr="exact", widget=CSVWidget
    )
    road_type = MultipleFilter(
        field_name="road_geometry__road_type",
        lookup_expr="icontains",
        widget=CSVWidget,
    )
    road_name = MultipleFilter(
        field_name="road_geometry__road_name_en",
        lookup_expr="icontains",
        widget=CSVWidget,
    )
    road_category = MultipleFilter(
        field_name="road_geometry__road_category",
        lookup_expr="icontains",
        widget=CSVWidget,
    )
    ward_no = django_filters.CharFilter(method="filter_ward_no", lookup_expr="exact")

    def filter_ward_no(self, queryset, name, value):
        ward_numbers = [int(num) for num in value.split(",") if num.isdigit()]
        q_objects = Q()
        for ward_num in ward_numbers:
            q_objects |= Q(road_geometry__ward_no__contains=[ward_num])
        return queryset.filter(q_objects)

    class Meta:
        model = RoadGeometry
        fields = ["road_id", "road_type", "road_name", "road_category"]


class BuildingBasicFilter(django_filters.FilterSet):
    ward_no = MultipleFilter(
        field_name="ward_no", lookup_expr="exact", widget=CSVWidget
    )
    tole_name = MultipleFilter(
        field_name="tole_name", lookup_expr="icontains", widget=CSVWidget
    )
    reg_type = MultipleFilter(
        field_name="reg_type", lookup_expr="exact", widget=CSVWidget
    )
    owner_status = MultipleFilter(
        field_name="owner_status", lookup_expr="exact", widget=CSVWidget
    )

    class Meta:
        model = Building
        fields = ["ward_no", "tole_name", "reg_type", "owner_status"]
