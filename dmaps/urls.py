from django.urls import include, path, re_path
from rest_framework import routers
from dmaps.viewsets import (
    NavBarViewSet,
    HeaderViewSet,
    MajorFeatureViewSet,
    MajorComponentViewSet,
    WeWorkWithViewSet,
    ContactUsViewSet,
    AboutViewSet,
    UseCaseViewSet,
    UseCaseMajorFeatureViewSet,
    WhyUseDmapsViewSet,
    CardViewSet,
    ImageViewSet,
    CollaborationViewSet,
    CollaboratorViewSet,
    IntroViewSet,
    GeometryFileViewSet,
    MunicipalityBoundaryVectorTile,
    ProvinceBoundaryVectorTile,
    MunicipalityGeojsonViewSet,
    ProvinceGeojsonViewSet,
    PromoMapPopUp,
    FooterViewSet,
    MapFeatureCountViewSet,
    FAQViewSet,
    SDGDetailViewSet,
    UseCaseDetailViewSet,
    BuildingCountInMunicipalityView,
)

router = routers.DefaultRouter()

router.register("nav-bar", NavBarViewSet, basename="nav_bar")
router.register("major-feature", MajorFeatureViewSet, basename="major_feature")
router.register("major-component", MajorComponentViewSet, basename="major_component")
router.register("we-work-with", WeWorkWithViewSet, basename="we_work_with")
router.register("contact-us", ContactUsViewSet, basename="contact_us")
router.register("about", AboutViewSet, basename="about")
router.register("use-case", UseCaseViewSet, basename="use_case")
router.register("intro", IntroViewSet, basename="intro_dmaps")
router.register("sdg-detail", SDGDetailViewSet, basename="sdg-detail")
router.register("use-case-detail", UseCaseDetailViewSet, basename="use-case-detail")
router.register(
    "use-case-major-feature",
    UseCaseMajorFeatureViewSet,
    basename="use_case_major_feature",
)
router.register("why-use-dmaps", WhyUseDmapsViewSet, basename="why_use_dmaps")
router.register("cards", CardViewSet, basename="cards_dmaps")
router.register("images", ImageViewSet, basename="images_dmaps")
router.register("collaboration", CollaborationViewSet, basename="collaboration_dmaps")
router.register("collaborator", CollaboratorViewSet, basename="collaborator_dmaps")
router.register("header", HeaderViewSet, basename="header_dmaps")
router.register("footer", FooterViewSet, basename="footer_dmaps")
router.register("geometry-file", GeometryFileViewSet, basename="geometry_file")
router.register("province-geojson", ProvinceGeojsonViewSet, basename="province_geojson")
router.register(
    "municipality-geojson", MunicipalityGeojsonViewSet, basename="municipality_geojson"
)
router.register("faq", FAQViewSet, basename="faq")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "municipality-boundary/<int:z>/<int:x>/<int:y>/",
        MunicipalityBoundaryVectorTile.as_view(),
        name="municipality_boundary",
    ),
    path(
        "province-boundary/<int:z>/<int:x>/<int:y>/",
        ProvinceBoundaryVectorTile.as_view(),
        name="province_boundary",
    ),
    path(
        "map-popup/",
        PromoMapPopUp.as_view(),
        name="map_popup",
    ),
    path(
        "map-feature-count/",
        MapFeatureCountViewSet.as_view(),
        name="map_feature_count",
    ),
    path(
        "building-count-in-municipalities/",
        BuildingCountInMunicipalityView.as_view(),
        name="building_count_in_municipalities",
    ),
]
