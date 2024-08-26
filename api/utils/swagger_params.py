from drf_yasg import openapi

building_sp_choices = [
    "hospitality",
    "smes",
    "retails",
    "construction_and_engineering",
    "agriculture",
    "pharmacy",
    "entertainment",
    "financial",
    "healthcare",
    "education",
    "industry_and_manufacturing",
    "media",
    "religious",
    "mall",
    "residential",
    "other",
]


# road_params = [
# openapi.Parameter(
#     name="xyz",
#     in_=openapi.IN_QUERY,
#     type=openapi.TYPE_STRING,
#     description="Search query string for filtering road data",
#     required=False,
# ),
# openapi.Parameter(
#     name="ordering",
#     in_=openapi.IN_QUERY,
#     type=openapi.TYPE_STRING,
#     description="Query string for ordering the road data",
#     required=False,
# ),
# ]

# building_params = [
#     openapi.Parameter(
#         name="search",
#         in_=openapi.IN_QUERY,
#         type=openapi.TYPE_STRING,
#         description="Search query string for filtering building data",
#         required=False,
#     ),
#     openapi.Parameter(
#         name="ordering",
#         in_=openapi.IN_QUERY,
#         type=openapi.TYPE_STRING,
#         description="Query string for ordering the building data",
#         required=False,
#     ),
# ]


installation_params = [
    openapi.Parameter("id", openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=True),
]

dashboard_feature_count_params = [
    openapi.Parameter(
        name="layer",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        enum=["building", "road"],
        description="layer type",
    ),
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="ward number",
    ),
]

public_page_feature_count_params = [
    openapi.Parameter(
        name="layer",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        enum=["building", "road"],
        description="layer type",
    ),
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="ward number",
    ),
    openapi.Parameter(
        "road_type",
        openapi.IN_QUERY,
        description="Filter by road type",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "building_use",
        openapi.IN_QUERY,
        description="Filter by building use",
        type=openapi.TYPE_STRING,
    ),
]

unique_value_params = [
    openapi.Parameter(
        name="field_name",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="field name",
    ),
]

road_field_params = [
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="ward_no",
    ),
    openapi.Parameter(
        name="field_name",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="field name",
    ),
]


dashboard_road_count_params = [
    openapi.Parameter(
        name="field_name",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        enum=["road_category", "road_type", "road_class", "road_lane"],
        required=True,
        description="road field name",
    ),
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="ward number",
    ),
]

public_page_road_count_params = [
    openapi.Parameter(
        name="field_name",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        enum=["road_category", "road_type", "road_class", "road_lane"],
        required=True,
        description="road field name",
    ),
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="ward number",
    ),
    openapi.Parameter(
        "road_type",
        openapi.IN_QUERY,
        description="Filter by road type",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "building_use",
        openapi.IN_QUERY,
        description="Filter by building use",
        type=openapi.TYPE_STRING,
    ),
]

dashboard_building_count_params = [
    openapi.Parameter(
        name="field_name",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        enum=[
            "association_type",
            "reg_type",
            "building_use",
            "roof_type",
            "building_structure",
            "temporary_type",
            "road_lane",
            "road_type",
        ],
        description="building field name",
    ),
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="ward number",
    ),
]

public_page_building_count_params = [
    openapi.Parameter(
        name="field_name",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        enum=[
            "association_type",
            "reg_type",
            "building_use",
            "roof_type",
            "building_structure",
            "temporary_type",
            "road_lane",
            "road_type",
        ],
        description="building field name",
    ),
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="ward number",
    ),
    openapi.Parameter(
        "road_type",
        openapi.IN_QUERY,
        description="Filter by road type",
        type=openapi.TYPE_STRING,
    ),
    openapi.Parameter(
        "building_use",
        openapi.IN_QUERY,
        description="Filter by building use",
        type=openapi.TYPE_STRING,
    ),
]


add_road_data = [
    openapi.Parameter(
        name="geom",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=True,
        description="add geometry",
    ),
]

add_building_data = [
    openapi.Parameter(
        name="geom",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_STRING,
        required=True,
        description="Add geometry",
    ),
    openapi.Parameter(
        name="building_sp_use",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            type=openapi.TYPE_STRING,
            enum=[choice for choice in building_sp_choices],
        ),
        required=False,
        description="Building Special Use",
    ),
]

update_building_data = [
    openapi.Parameter(
        name="building_sp_use",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            type=openapi.TYPE_STRING,
            enum=[choice for choice in building_sp_choices],
        ),
        required=False,
        description="Building Special Use",
    ),
]

building_image_get_params = [
    openapi.Parameter(
        name="building_id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
        required=True,
        description="building id",
    ),
    openapi.Parameter(
        name="image_type",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        enum=["building_image", "building_plan"],
        required=False,
        description="image type",
    ),
]

celery_params = [
    openapi.Parameter(
        name="task_id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="task_id",
    ),
]

house_numbering_params = [
    openapi.Parameter(
        name="data_id",
        in_=openapi.IN_QUERY,
        description="enter the building id",
        type=openapi.TYPE_STRING,
        required=False,
    )
]

pop_up_params = [
    openapi.Parameter(
        name="id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="layer id",
    ),
    openapi.Parameter(
        name="type",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="layer type",
        enum=["building", "road"],
        default="building",
    ),
]


public_pop_up_params = [
    openapi.Parameter(
        name="id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="layer id",
    ),
    openapi.Parameter(
        name="type",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="layer type",
        enum=["building", "road"],
        default="building",
    ),
]


palikawardparams = [
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        description="Ward no",
        type=openapi.TYPE_STRING,
        required=False,
    )
]

vector_tile_params = [
    openapi.Parameter(
        name="Vector layer id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
        required=True,
        description="Layer ID.",
    )
]

raster_layer_params = [
    openapi.Parameter(
        name="min_zoom",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_INTEGER,
        required=True,
        description="min zoom for tile generation",
    ),
    openapi.Parameter(
        name="max_zoom",
        in_=openapi.IN_FORM,
        type=openapi.TYPE_INTEGER,
        required=True,
        description="max zoom for tile generation",
    ),
]

raster_tile_parameters = [
    openapi.Parameter(
        name="raster_id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
        required=False,
        description="Raster ID.",
    ),
]
download_param = [
    openapi.Parameter(
        "file_format",
        openapi.IN_QUERY,
        description="Desired output file format",
        type=openapi.TYPE_STRING,
        enum=["shapefile", "shp", "geojson", "csv", "gpkg"],
        required=True,
    ),
    openapi.Parameter(
        "layer",
        openapi.IN_QUERY,
        description="Desired layer",
        type=openapi.TYPE_STRING,
        enum=["road", "building"],
        required=True,
    ),
]

reverse_linestring_params = [
    openapi.Parameter(
        name="id",
        in_=openapi.IN_QUERY,
        description="road id",
        type=openapi.TYPE_STRING,
        required=False,
    )
]
delete_table_params = [
    openapi.Parameter(
        name="table",
        in_=openapi.IN_QUERY,
        description="enter table name",
        type=openapi.TYPE_STRING,
        enum=["building", "buildinggeometry", "road", "roadgeometry"],
        required=False,
    )
]

bbox_params = [
    openapi.Parameter(
        name="bbox",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="bbox",
    ),
    openapi.Parameter(
        name="type",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="layer type",
        enum=["building", "road"],
        default="building",
    ),
]

history_logs_params = [
    openapi.Parameter(
        name="layer",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="layer",
    ),
    openapi.Parameter(
        name="related_id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
        required=False,
        description="related_id for edits made at the same timestamp",
    ),
    openapi.Parameter(
        name="association_id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
        required=False,
        description="association_id for every edit ever made",
    ),
]

filtered_building_plan_params = [
    openapi.Parameter(
        name="layer",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        enum=["Naxa Pass"],
        description="layer",
    ),
    openapi.Parameter(
        name="ward_no",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            type=openapi.TYPE_INTEGER,
        ),
        required=False,
        description="ward_no",
    ),
    openapi.Parameter(
        name="owner_status",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            type=openapi.TYPE_STRING,
        ),
        required=False,
        description="owner status if governmental or non_governmental",
    ),
    openapi.Parameter(
        name="reg_type",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            type=openapi.TYPE_STRING,
        ),
        required=False,
        description="registration type",
    ),
    openapi.Parameter(
        name="tole_name",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            type=openapi.TYPE_STRING,
        ),
        required=False,
        description="tole name",
    ),
]

restore_logs_params = openapi.Parameter(
    name="timestamp",
    in_=openapi.IN_FORM,
    type=openapi.TYPE_STRING,
    description="timestamp",
)
