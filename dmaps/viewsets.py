import os
import psycopg2
from math import ceil
from django.db import connection
from rest_framework.response import Response
from dmaps.swagger_params import *
from dmaps.serializers import *
from rest_framework import viewsets, status, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from django_filters.rest_framework import DjangoFilterBackend
from dmaps.filters import HeaderFilter, UseCaseFilter, WeWorkWithFilter, CardFilter
from rest_framework import filters
from dmaps.models import (
    GeometryFile,
    MunicipalityGeometry,
    ProvinceGeometry,
    FAQ,
    SDG,
    UseCaseDetail,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from dmaps.file_handlers import handlegeometryfile
from core.tile import BinaryRenderer, BaseMVTView, split_on_last_occurrence
from rest_framework.views import APIView
from django.core.serializers import serialize
from rest_framework.pagination import PageNumberPagination
from core.models import BuildingGeometry, RoadGeometry, Building, Road


# Connect to the PostgreSQL database
conn = psycopg2.connect(
    database=os.environ.get("POSTGRES_DB", "postgres"),
    user=os.environ.get("POSTGRES_USER", "postgres"),
    password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
    port=os.environ.get("POSTGRES_PORT", "5432"),
    host=os.environ.get("POSTGRES_HOST", "localhost"),
)
cur = conn.cursor()


class DefaultPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = "page_size"
    max_page_size = 1


class NavBarViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Navigation bar.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps NavBar objects.
    It supports listing, retrieving, creating, updating, and deleting NavBar instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = NavBar.objects.all()
    serializer_class = NavBarSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single NavBar instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Nav Bar"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of NavBar objects",
        operation_description="get a list of all objects of NavBar for all pages",
        tags=["dmaps Nav Bar"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new NavBar instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Nav Bar"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a NavBar instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Nav Bar"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a NavBar instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Nav Bar"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class HeaderViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Header.

    This API view allows users to manage headers.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps Header objects.
    It supports listing, retrieving, creating, updating, and deleting Header instances.

    filter_backends: The filter class for applying filter on Header objects.
    The filtering includes "page" wise filter like 'home', 'use_case', 'about', 'contact'.
    http://localhost:8080/api/v1/dmaps/header/?page=home

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Header.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = HeaderFilter
    serializer_class = HeaderSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Header instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Header"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of Header objects",
        operation_description="Get a list of Header objects for all pages.The filter class for applying filter on Header objects.The filtering includes 'page' wise filter like 'home', 'use_case', 'about', 'contact'. Example usage: dmaps/header/?page=home",
        tags=["dmaps Header"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new Header instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Header"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a Header instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Header"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Header instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Header"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class FooterViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Footer section.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps Footer section objects.
    It supports listing, retrieving, creating, updating, and deleting footer instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Footer.objects.all()
    serializer_class = FooterSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Footer instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Footer"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of Footer objects",
        operation_description="get a list of all footer objects for all pages",
        tags=["dmaps Footer"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new Footer instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Footer"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a Footer instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Footer"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Footer instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Footer"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class AboutViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps About section in home page.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps About section objects.
    It supports listing, retrieving, creating, updating, and deleting About instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = About.objects.all()
    serializer_class = AboutSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single About instance",
        operation_description="get a single object's information by id",
        tags=["dmaps About"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of About objects",
        operation_description="get a list of all 'about' objects for home page",
        tags=["dmaps About"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new About instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps About"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch an About instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps About"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete an About instance",
        operation_description="Delete an instance by id",
        tags=["dmaps About"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class MajorFeatureViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Major Feature section in home page.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps Major Feature objects.
    It supports listing, retrieving, creating, updating, and deleting Header instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = MajorFeature.objects.all()
    serializer_class = MajorFeatureSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single majorfeature instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Major Feature"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of majorfeature objects",
        operation_description="get a list of all objects of majorfeaure of home page",
        tags=["dmaps Major Feature"],
    )
    def list(self, request, *args, **kwargs):
        latest_major_feature = MajorFeature.objects.last()

        if latest_major_feature is not None:
            cards = Card.objects.filter(type="major_feature")
            serialized_major_feature = MajorFeatureSerializer(latest_major_feature).data
            serialized_cards = CardSerializerMajorFeature(
                cards, many=True, context={"request": request}
            ).data
            for card_data in serialized_cards:
                card_images = card_data["images"]
                if card_images:
                    # Get the latest image
                    latest_image = card_images[-1]
                    card_data["images"] = [latest_image]

            serialized_major_feature = MajorFeatureSerializer(latest_major_feature).data
            serialized_major_feature["cards"] = serialized_cards

            return Response(serialized_major_feature)

        else:
            return Response({})

    @swagger_auto_schema(
        operation_summary="major Create a new feature instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Major Feature"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="major Patch a feature instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Major Feature"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="major Delete a feature instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Major Feature"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class MajorComponentViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Major Component section in home page.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps Major Component section objects.
    It supports listing, retrieving, creating, updating, and deleting Major Component instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = MajorComponent.objects.all()
    serializer_class = MajorComponentSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Major instance Component",
        operation_description="get a single object's information by id",
        tags=["dmaps Major Component"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Major Get a list of Component objects",
        operation_description="get a list of all 'major components' objects in home page",
        tags=["dmaps Major Component"],
    )
    def list(self, request, *args, **kwargs):
        latest_major_component = MajorComponent.objects.last()

        if latest_major_component is not None:
            cards = Card.objects.filter(type="major_component")
            serialized_major_component = MajorComponentSerializer(
                latest_major_component
            ).data
            serialized_cards = CardSerializer(
                cards, many=True, context={"request": request}
            ).data
            serialized_major_component["cards"] = serialized_cards
            return Response(serialized_major_component)

        else:
            return Response({})

    @swagger_auto_schema(
        operation_summary="Major Create a new Component instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Major Component"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Major Patch a Component instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Major Component"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Major Delete a Component instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Major Component"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class WeWorkWithViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps We Work With section in home page.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps We Work With objects.
    It supports listing, retrieving, creating, updating, and deleting We Work With instances.

    filter_backends: The filter class for applying filter on Header objects.
    The filtering includes "partner" wise filter like 'partner_and_collabrators', 'client'.

    http://localhost:8080/api/v1/dmaps/we-work-with/?partner=client

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = WeWorkWith.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = WeWorkWithFilter

    serializer_class = WeWorkWithSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single We instance Work With",
        operation_description="get a single object's information by id",
        tags=["dmaps We Work With"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="get a list of all objects",
        operation_description="We Work Get a list of With objects in home page.The filter class for applying filter on Header objects.The filtering includes 'partner' wise filter like 'partner_and_collabrators', 'client'. dmaps/header/?partner=client",
        tags=["dmaps We Work With"],
    )
    def list(self, request, *args, **kwargs):
        latest_we_work_with = self.filter_queryset(self.get_queryset()).last()
        value = request.query_params.get("partner", None)

        if latest_we_work_with is not None:
            cards = Card.objects.filter(type=value)
            serialized_we_work_with = WeWorkWithSerializer(latest_we_work_with).data
            serialized_cards = CardSerializer(
                cards, many=True, context={"request": request}
            ).data
            serialized_we_work_with["cards"] = serialized_cards
            return Response(serialized_we_work_with)

        else:
            return Response({})

    @swagger_auto_schema(
        operation_summary="We Work Create a new With instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps We Work With"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="We Work Patch a With instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps We Work With"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="We Work Delete a With instance",
        operation_description="Delete an instance by id",
        tags=["dmaps We Work With"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ContactUsViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Contact Us in home page.

    This class provides CRUD (Create, Read, Update, Delete) operations for Contact Us objects.
    It supports listing, retrieving, creating, updating, and deleting Contact Us instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = ContactUs.objects.all()
    serializer_class = ContactUsSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Contact instance Us",
        operation_description="get a single object's information by id",
        tags=["dmaps Contact Us"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Contact Get a list of Us objects",
        operation_description="get a list of all 'contact us' objects in home page",
        tags=["dmaps Contact Us"],
    )
    def list(self, request, *args, **kwargs):
        latest_contact_us = ContactUs.objects.last()

        if latest_contact_us is not None:
            cards = Card.objects.filter(type="contact_us")
            serialized_contact_us = ContactUsSerializer(latest_contact_us).data
            serialized_cards = CardSerializer(
                cards, many=True, context={"request": request}
            ).data
            serialized_contact_us["cards"] = serialized_cards
            return Response(serialized_contact_us)

        else:
            return Response({})

    @swagger_auto_schema(
        operation_summary="Contact Create a new Us instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Contact Us"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Contact Patch a Us instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Contact Us"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Contact Delete a Us instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Contact Us"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UseCaseViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Use Case in Use Case page.

    This class provides CRUD (Create, Read, Update, Delete) operations for Use Case objects.
    It supports listing, retrieving, creating, updating, and deleting Use Case instances.

    filter_backends: The filter class for applying filter on the objects.
    The filtering includes "use_case" wise filter like 'municipal_management', 'navigational_operations', 'data_management_and_centralization', 'geospatial_planning_and_visualization'.
    http://localhost:8080/api/v1/dmaps/use-case/?use_case=municipal_management
    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = UseCase.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = UseCaseFilter
    serializer_class = UseCaseSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Use instance Case",
        operation_description="get a single object's information by id",
        tags=["dmaps Use Case"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Use Get a list of Case objects",
        operation_description="Get a list of all UseCaseThe objects in Use Case page. has Filter class for applying filter on the objects.The filtering includes 'use_case' wise filter like 'municipal_management', 'navigational_operations','data_management_and_centralization', 'geospatial_planning_and_visualization'. dmaps/use-case/?use_case=municipal_management",
        tags=["dmaps Use Case"],
    )
    def list(self, request, *args, **kwargs):
        latest_use_case = self.filter_queryset(self.get_queryset()).last()
        value = request.query_params.get("use_case", None)

        if latest_use_case is not None:
            cards = Card.objects.filter(type=value)
            serialized_use_case = UseCaseSerializer(latest_use_case).data
            serialized_cards = CardSerializer(
                cards, many=True, context={"request": request}
            ).data
            serialized_use_case["cards"] = serialized_cards
            return Response(serialized_use_case)

        else:
            return Response({})

    @swagger_auto_schema(
        operation_summary="Use Create a new Case instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Use Case"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Use Patch a Case instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Use Case"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Use Delete a Case instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Use Case"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class IntroViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Intro in About page.

    This class provides CRUD (Create, Read, Update, Delete) operations for Intro objects.
    It supports listing, retrieving, creating, updating, and deleting Intro instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Intro.objects.all()
    serializer_class = IntroSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single intro instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Intro"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of intro objects",
        operation_description="get a list of all Intro objects in about page",
        tags=["dmaps Intro"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new intro instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Intro"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a intro instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Intro"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a intro instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Intro"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UseCaseMajorFeatureViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Use Case's Major Feature in About page.

    This class provides CRUD (Create, Read, Update, Delete) operations for Use Case Major Feature objects.
    It supports listing, retrieving, creating, updating, and deleting Use Case Major Feature instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = UseCaseMajorFeature.objects.all()
    serializer_class = UseCaseMajorFeatureSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Use instance Case Major Feature",
        operation_description="get a single object's information by id",
        tags=["dmaps Use Case Major Feature"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Use Case Major Get a list of Feature objects",
        operation_description="get a list of all 'use case major feature' objects in About page",
        tags=["dmaps Use Case Major Feature"],
    )
    def list(self, request, *args, **kwargs):
        latest_use_case_major_feature = UseCaseMajorFeature.objects.last()

        if latest_use_case_major_feature is not None:
            cards = Card.objects.filter(type="use_case_major_feature")
            serialized_use_case_major_feature = UseCaseMajorFeatureSerializer(
                latest_use_case_major_feature
            ).data
            serialized_cards = CardSerializer(
                cards, many=True, context={"request": request}
            ).data
            serialized_use_case_major_feature["cards"] = serialized_cards
            return Response(serialized_use_case_major_feature)

        else:
            return Response({})

    @swagger_auto_schema(
        operation_summary="Use Case Major Create a new Feature instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Use Case Major Feature"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Use Case Major Patch a Feature instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Use Case Major Feature"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Use Case Major Delete a Feature instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Use Case Major Feature"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class WhyUseDmapsViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Why Use Dmaps in About page.

    This class provides CRUD (Create, Read, Update, Delete) operations for Why Use Dmaps objects.
    It supports listing, retrieving, creating, updating, and deleting Why Use Dmaps instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = WhyUseDmaps.objects.all()
    serializer_class = WhyUseDmapsSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Why instance Use Dmaps",
        operation_description="get a single object's information by id",
        tags=["dmaps Why Use Dmaps"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Why Use Get a list of Dmaps objects",
        operation_description="get a list of all WhyUseDmaps objects in About page",
        tags=["dmaps Why Use Dmaps"],
    )
    def list(self, request, *args, **kwargs):
        latest_why_use = WhyUseDmaps.objects.last()

        if latest_why_use is not None:
            cards = Card.objects.filter(type="why_use_dmaps")
            serialized_why_use = WhyUseDmapsSerializer(latest_why_use).data
            serialized_cards = CardSerializerWhyUse(
                cards, many=True, context={"request": request}
            ).data
            serialized_why_use["cards"] = serialized_cards
            return Response(serialized_why_use)

        else:
            return Response({})

    @swagger_auto_schema(
        operation_summary="Why Use Create a new Dmaps instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Why Use Dmaps"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Why Use Patch a Dmaps instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Why Use Dmaps"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Why Use Delete a Dmaps instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Why Use Dmaps"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CollaborationViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Collaboration section in contact us page.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps Collaboration objects.
    It supports listing, retrieving, creating, updating, and deleting Collaboration instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Collaboration.objects.all()
    serializer_class = CollaborationSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Collaborations instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Collaborations"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of Collaborations objects",
        operation_description="get a list of all Collaboration objects in About page",
        tags=["dmaps Collaborations"],
    )
    def list(self, request, *args, **kwargs):
        latest_collaboration = Collaboration.objects.last()

        if latest_collaboration is not None:
            cards = Card.objects.filter(type="collaboration")
            serialized_collaboration = CollaborationSerializer(
                latest_collaboration
            ).data
            serialized_cards = CardSerializer(
                cards, many=True, context={"request": request}
            ).data
            serialized_collaboration["cards"] = serialized_cards
            return Response(serialized_collaboration)

        else:
            return Response({})

    @swagger_auto_schema(
        operation_summary="Create a new Collaborations instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Collaborations"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a Collaborations instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Collaborations"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Collaborations instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Collaborations"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CollaboratorViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Collaborator Form section in contact us page.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps Collaborator objects.
    It supports listing, retrieving, creating, updating, and deleting Collaborator instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            # self.action == "create"
            self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Collaborator instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Collaborator"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of Collaborator objects",
        operation_description="get a list of all Collaborator objects in Contact us page",
        tags=["dmaps Collaborator"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new Collaborator instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Collaborator"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "message": "Thank you for getting in touch with DMAPs. We will get back to you soon.",
                    "details": serializer.data,
                },
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            return Response(
                {"message": "error", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Patch a Collaborator instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Collaborator"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a Collaborator instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Collaborator"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CardViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps cards.
    It supports listing, retrieving, creating, updating, and deleting dmaps cards.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = CardFilter

    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Card instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Cards"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of Card objects",
        operation_description="get a list of all Card objects",
        tags=["dmaps Cards"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new card instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Cards"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a card instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Cards"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a card instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Cards"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ImageViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Images.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps Image objects.
    It supports listing, retrieving, creating, updating, and deleting Image instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single Image instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Image"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of Image objects",
        operation_description="get a list of all objects",
        tags=["dmaps Image"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new image instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Image"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a image instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Image"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a image instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Image"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class FooterViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Footer.

    This class provides CRUD (Create, Read, Update, Delete) operations for footer objects.
    It supports listing, retrieving, creating, updating, and deleting footer instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = Footer.objects.all()
    serializer_class = FooterSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single footer instance",
        operation_description="get a single object's information by id",
        tags=["dmaps Footer"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of footer objects",
        operation_description="get a list of latest Footer objects for all page",
        tags=["dmaps Footer"],
    )
    def list(self, request, *args, **kwargs):
        try:
            footer_last_instance = Footer.objects.filter(is_deleted="False").last()
            serializer = self.get_serializer(footer_last_instance)
            return Response(serializer.data)
        except:
            return Response({})

    @swagger_auto_schema(
        operation_summary="Create a new footer instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps Footer"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a footer instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps Footer"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a footer instance",
        operation_description="Delete an instance by id",
        tags=["dmaps Footer"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class GeometryFileViewSet(viewsets.ModelViewSet):
    """
    API view for Palika Geometry File.
    This API view allows users to get Palika Geometry File.

    """

    http_method_names = ["post", "patch"]
    queryset = GeometryFile.objects.all()
    serializer_class = GeometryFileSerializer
    parser_classes = (FormParser, MultiPartParser)

    @swagger_auto_schema(
        operation_summary="Post Geometry File",
        tags=["geometry file"],
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new Geometry File object by uploading a file.

        Returns:
            Response: A response object with the serialized Layer object and additional metadata,or an error response if the request or file is invalid.

        Raises:
            N/A (Does not raise any exceptions explicitly, but relies on Django REST Framework to handle exceptions and return appropriate error responses.)
        """
        try:
            serializer = GeometryFileSerializer(data=request.data)
            file_type = request.data.get("file_type")
            if file_type is None:
                return Response(
                    {
                        "message": "file_type is required",
                        "details": "error, file_type is required",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(
                    {"message": "error", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            response = handlegeometryfile(serializer.data.get("id"))
            return Response(
                {"message": response, "details": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": "error", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @swagger_auto_schema(
        operation_summary="Patch Geometry File",
        tags=["geometry file"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class MunicipalityBoundaryVectorTile(APIView):
    renderer_classes = (BinaryRenderer,)

    @swagger_auto_schema(
        operation_summary="Palika boundary vector-tile",
        tags=["dmaps municipality vector-tile"],
    )
    def get(self, request, *args, **kwargs):
        model_class = MunicipalityGeometry
        return BaseMVTView.get(
            self,
            request=request,
            z=kwargs.get("z"),
            x=kwargs.get("x"),
            y=kwargs.get("y"),
            model=model_class,
        )


class ProvinceBoundaryVectorTile(APIView):
    renderer_classes = (BinaryRenderer,)

    @swagger_auto_schema(
        operation_summary="Province vector-tile",
        tags=["dmaps province vector-tile"],
    )
    def get(self, request, *args, **kwargs):
        model_class = ProvinceGeometry
        return BaseMVTView.get(
            self,
            request=request,
            z=kwargs.get("z"),
            x=kwargs.get("x"),
            y=kwargs.get("y"),
            model=model_class,
        )


class MunicipalityGeojsonViewSet(viewsets.ModelViewSet):
    parser_classes = (FormParser, MultiPartParser)
    queryset = MunicipalityGeometry.objects.all()
    serializer_class = ProvinceGeometrySerializer
    http_method_names = ["get"]

    @swagger_auto_schema(
        operation_summary="Get Municipality Geojson",
        tags=["dmaps municipality-geojson"],
    )
    def list(self, request, *args, **kwargs):
        query = f"""SELECT jsonb_build_object('type','FeatureCollection', 'features', jsonb_agg(features.feature))
            FROM (
            SELECT jsonb_build_object(
                'type',       'Feature',
                'properties', to_jsonb(inputs) - 'geom',
                'geometry',   ST_AsGeoJSON(ST_Simplify(geom, 0.005, true))::jsonb
            ) AS feature
            FROM (SELECT * FROM dmaps_municipalitygeometry)inputs) features;"""

        cur.execute(query)

        # Fetch all rows
        rows = cur.fetchall()
        geojson = rows[0][0]

        # Close the cursor and connection
        # cur.close()
        # conn.close()

        return Response(geojson)

    @swagger_auto_schema(
        operation_summary="Get Municipality Geojson",
        tags=["dmaps municipality-geojson"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class ProvinceGeojsonViewSet(viewsets.ModelViewSet):
    parser_classes = (FormParser, MultiPartParser)
    queryset = ProvinceGeometry.objects.all()
    serializer_class = ProvinceGeometrySerializer
    http_method_names = ["get"]

    @swagger_auto_schema(
        operation_summary="Get Palika Ward Geojson",
        tags=["dmaps province-geojson"],
    )
    def list(self, request, *args, **kwargs):
        query = f"""SELECT jsonb_build_object('type','FeatureCollection', 'features', jsonb_agg(features.feature))
            FROM (
            SELECT jsonb_build_object(
                'type',       'Feature',
                'properties', to_jsonb(inputs) - 'geom',
                'geometry',   ST_AsGeoJSON(ST_Simplify(geom, 0.005, true))::jsonb
            ) AS feature
            FROM (SELECT * FROM dmaps_provincegeometry)inputs) features;"""

        cur.execute(query)

        # Fetch all rows
        rows = cur.fetchall()
        geojson = rows[0][0]

        # Close the cursor and connection
        # cur.close()
        # conn.close()

        return Response(geojson)

    @swagger_auto_schema(
        operation_summary="Get Palika Ward Geojson",
        tags=["dmaps province-geojson"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class PromoMapPopUp(APIView):
    """http://localhost:8080/api/v1/dmaps/map_popup/?id=870"""

    @swagger_auto_schema(
        operation_summary="Get pop up information",
        tags=["dmaps mappopup"],
        manual_parameters=dmaps_map_popup_params,
    )
    def get(self, request):
        id = request.query_params.get("id", None)
        if id:
            try:
                municipality = MunicipalityGeometry.objects.get(id=id)

            except MunicipalityGeometry.DoesNotExist:
                return Response(
                    {"error": f"No municipality found for id {id}."}, status=404
                )

        else:
            return Response({"error": "id is required."}, status=400)

        road_count = RoadGeometry.objects.filter(geom__within=municipality.geom).count()

        building_count = BuildingGeometry.objects.filter(
            geom__within=municipality.geom
        ).count()

        municipality_name = municipality.name

        province = ProvinceGeometry.objects.get(
            geom__contains=municipality.geom.centroid
        ).name
        # province = municipality.attr_data.get("Province_N")

        result = {
            "road_count": road_count,
            "building_count": building_count,
            "municipality": str(municipality_name),
            "province": str(province),
        }

        return Response(result, status=status.HTTP_200_OK)


class MapFeatureCountViewSet(APIView):
    http_method_names = ["get"]

    @swagger_auto_schema(
        operation_summary="Get Total Municipality, Province, Building And Road Feature Count",
        tags=["Dmaps maps"],
    )
    def get(self, request):
        building_count = (
            BuildingGeometry.objects.all()
            .filter(building_geometry__is_deleted=False)
            .count()
        )
        road_count = (
            RoadGeometry.objects.all().filter(road_geometry__is_deleted=False).count()
        )
        municipalities = MunicipalityGeometry.objects.all()

        municipality_counts = []

        # Loop through each MunicipalityGeometry instance and check for related BuildingGeometry
        for municipality in municipalities:
            # Use .filter().exists() to check for the existence of at least one related BuildingGeometry
            has_buildings = BuildingGeometry.objects.filter(
                geom__intersects=municipality.geom, building_geometry__is_deleted=False
            ).exists()

            if has_buildings:
                municipality_counts.append(municipality.name)

        # Count the number of municipalities with at least one building
        municipalities_with_buildings = len(municipality_counts)

        provinces = ProvinceGeometry.objects.all()

        province_counts = []

        # Loop through each ProvinceGeometry instance and check for related BuildingGeometry
        for province in provinces:
            # Use .filter().exists() to check for the existence of at least one related BuildingGeometry
            has_buildings = BuildingGeometry.objects.filter(
                geom__intersects=province.geom, building_geometry__is_deleted=False
            ).exists()

            if has_buildings:
                province_counts.append(province.name)

        provinces_with_buildings = len(province_counts)

        return Response(
            {
                "building": building_count,
                "road": road_count,
                "province": provinces_with_buildings,
                "municipalities": municipalities_with_buildings,
            }
        )


class FAQViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps FAQ in About page.

    This class provides CRUD (Create, Read, Update, Delete) operations for FAQ objects.
    It supports listing, retrieving, creating, updating, and deleting FAQ instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title_en", "description_en"]
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single FAQ instance",
        operation_description="get a single object's information by id",
        tags=["dmaps FAQ"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of FAQ objects",
        operation_description="get a list of all FAQ objects.",
        tags=["dmaps FAQ"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new FAQ instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps FAQ"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a FAQ instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps FAQ"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a FAQ instance",
        operation_description="Delete an instance by id",
        tags=["dmaps FAQ"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class SDGDetailViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Navigation bar.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps SDGDetail objects.
    It supports listing, retrieving, creating, updating, and deleting SDGDetail instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = SDG.objects.all()
    serializer_class = SDGSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single SDG Detail instance",
        operation_description="get a single object's information by id",
        tags=["dmaps SDG Details"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of SDG Detail objects",
        operation_description="get a list of all objects of SDG Detail for all pages",
        tags=["dmaps SDG Details"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new SDG Detail instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps SDG Details"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a SDG Detail instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps SDG Details"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a SDG Detail instance",
        operation_description="Delete an instance by id",
        tags=["dmaps SDG Details"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UseCaseDetailViewSet(viewsets.ModelViewSet):
    """
    API view for dmaps Navigation bar.

    This class provides CRUD (Create, Read, Update, Delete) operations for dmaps Use case Detail objects.
    It supports listing, retrieving, creating, updating, and deleting Use case Detail instances.

    """

    http_method_names = ["get", "post", "patch", "delete"]
    queryset = UseCaseDetail.objects.all()
    serializer_class = UseCaseDetailSerializer
    parser_classes = (FormParser, MultiPartParser)

    def get_permissions(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
            or self.action == "destroy"
        ):
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_summary="Get a single UseCase Detail instance",
        operation_description="get a single object's information by id",
        tags=["dmaps UseCase Details"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of UseCase Detail objects",
        operation_description="get a list of all objects of UseCase Detail for all pages",
        manual_parameters=use_case_detail_params,
        tags=["dmaps UseCase Details"],
    )
    def list(self, request, *args, **kwargs):
        card_id = request.GET.get("card_id", None)
        if card_id:
            try:
                use_case_card = Card.objects.get(id=card_id)
                use_case_detail_data = UseCaseDetail.objects.filter(
                    use_case_card=use_case_card
                )
                sdg_instance = (
                    use_case_card.use_case_sdg
                    if hasattr(use_case_card, "use_case_sdg")
                    else None
                )
                sdg_images = (
                    SDGImage.objects.filter(sdg_data=sdg_instance)
                    if sdg_instance
                    else None
                )

                card_serializer = CardSerializer(
                    use_case_card, context={"request": self.request}
                )
                detail_serializer = UseCaseDetailSerializer(
                    use_case_detail_data, many=True
                )
                sdg_serializer = SDGSerializer(sdg_instance) if sdg_instance else None
                sdg_images_serializer = (
                    SDGImageSerializer(
                        sdg_images, many=True, context={"request": self.request}
                    )
                    if sdg_images
                    else None
                )

                response_data = {
                    "use_case_card": {
                        **card_serializer.data,
                        "use_case_details": detail_serializer.data,
                        "sdg_information": {
                            **(sdg_serializer.data if sdg_serializer else {}),
                            "sdg_images": sdg_images_serializer.data
                            if sdg_images_serializer
                            else [],
                        },
                    }
                }

                return Response(
                    {"msg": "success", "data": response_data}, status=status.HTTP_200_OK
                )
            except Card.DoesNotExist:
                return Response(
                    {"msg": "error", "detail": "Card not found for the provided id."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new UseCase Detail instance",
        operation_description="Create a new instance by providing the required data in the request.",
        tags=["dmaps UseCase Details"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Patch a UseCase Detail instance",
        operation_description="Partially update an instance. Ensure you provide the unique identifier of the resource you want to update and specify the fields you wish to change. Any field not included in the request will remain unchanged.",
        tags=["dmaps UseCase Details"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a UseCase Detail instance",
        operation_description="Delete an instance by id",
        tags=["dmaps UseCase Details"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BuildingCountInMunicipalityView(APIView):
    @swagger_auto_schema(
        operation_summary="building count in each municipality",
        tags=["dmaps building count in municipalities"],
    )
    def get(self, request):
        with connection.cursor() as cursor:
            # SQL query
            sql_query = """
                SELECT
                    mg.id as municipality_id,
                    mg.name as municipality_name,
                    COUNT(b.id) as building_count
                FROM
                    dmaps_municipalitygeometry mg
                LEFT JOIN
                    core_buildinggeometry bg
                ON
                    ST_Within(bg.geom, mg.geom)
                LEFT JOIN
                    core_building b
                ON
                    b.feature_id = bg.id AND b.is_deleted = FALSE
                GROUP BY
                    mg.id, mg.name
            """
            cursor.execute(sql_query)
            rows = cursor.fetchall()

        response_data = [
            {
                "municipality_id": row[0],
                "municipality_name": row[1],
                "building_count": row[2],
            }
            for row in rows
        ]

        return Response(response_data, status=status.HTTP_200_OK)
