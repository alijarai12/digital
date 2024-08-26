from drf_yasg import openapi

dmaps_map_popup_params = [
    openapi.Parameter(
        name="id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=True,
        description="enter object of MunicipalGeometry",
    ),
]

use_case_detail_params = (
    openapi.Parameter(
        name="card_id",
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_INTEGER,
        required=False,
        description="card_id",
    ),
)
