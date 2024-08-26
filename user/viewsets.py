from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, logout
from django.contrib.auth.models import Group
from core.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView, Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import parser_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.admin.models import LogEntry
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from .serializers import (
    # UserProfileSerializer,
    UserSerializer,
    UserPostSerializer,
    UserPatchSerializer,
    UserLogSerializer,
    UserGroupSerializerPermissions,
    WorkshopModeSerializer,
)
from django.http import HttpResponse, JsonResponse
from .utils import account_activation_token
from user.swagger_params import *
from user.permissions import *
from user.filters import *

serializers = getattr(settings, "REST_AUTH_SERIALIZERS", {})

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        "password",
        "old_password",
        "new_password1",
        "new_password2",
    ),
)


# *****************Pagination******************
class UserlistPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# *****************Pagination******************


class UserViewset(ModelViewSet):
    """
    A viewset that provides CRUD operations for the User model.
    """

    http_method_names = ["get", "post", "patch", "delete"]
    parser_classes = (FormParser, MultiPartParser)
    default_serializer_class = UserSerializer
    pagination_class = UserlistPagination
    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )
    search_fields = ["username", "email"]
    ordering_fields = [
        "id",
        "username",
        "designation",
        "group",
        "is_active",
        "date_modified",
    ]
    filterset_class = UserFilter
    queryset = User.objects.all()
    serializer_classes = {
        "create": UserPostSerializer,
        "partial_update": UserPatchSerializer,
    }

    def get_permissions(self):
        """
        Get a list of permission classes based on the request action.
        Returns a list of permission classes.
        """
        if self.action == "list" or self.action == "retrieve":
            permission_classes = [HasViewPermission]
        elif self.action == "create":
            permission_classes = [HasAddPermission]
        elif self.action == "partial_update":
            permission_classes = [HasChangePermission]
        elif self.action == "destroy":
            permission_classes = [HasDeletePermission]
        else:
            permission_classes = []
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """
        Get the appropriate serializer class based on the request action.
        Returns the serializer class for the given request action.
        """
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    @swagger_auto_schema(
        operation_summary="Get a single user's information", tags=["user"]
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Get a single user's information.

        Parameters:
            request, *args, **kwargs

        Returns:
            Response: The HTTP response object with user information.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get a list of user's information",
        tags=["user"],
        manual_parameters=userlist_parameters,
    )
    def list(self, request, *args, **kwargs):
        """
        Get a list of user information.

        search_fields includes "first_name", "last_name", "username", "email"
        ordering_fields includes "id", "username", "email"

        Parameters:
            request, *args, **kwargs

        Returns:
            Response: The HTTP response object with a list of users.
        """
        self.queryset = User.objects.filter(is_deleted=False)
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a user's information",
        tags=["user"],
        manual_parameters=userpatch_parameters,
    )
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        user_instance = self.get_object()

        if response.status_code != status.HTTP_200_OK:
            return response  # Return early if the update failed

        user_instance.save()
        thumbnail_url = None
        if user_instance.thumbnail:
            thumbnail_url = request.build_absolute_uri(user_instance.thumbnail)

        response.data = {
            "message": "The information has been updated.",
            "details": {
                "username": user_instance.username,
                "is_active": user_instance.is_active,
                "ward": user_instance.ward,
                "designation": user_instance.designation,
                "role_type": user_instance.group.name if user_instance.group else None,
                "is_deleted": user_instance.is_deleted,
                "thumbnail": thumbnail_url,
                "email": user_instance.email,
            },
        }

        return response

    @swagger_auto_schema(
        operation_summary="Delete a user",
        tags=["user"],
    )
    def destroy(self, request, *args, **kwargs):
        """
        Delete a user
        """
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a user",
        tags=["user"],
        manual_parameters=userprofile_parameters,
    )
    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")

            user = User.objects.filter(email=email).first()
            if not user or (user and user.is_deleted):
                if user and user.is_deleted:
                    serializer = self.get_serializer_class()(
                        user, data=request.data, partial=True
                    )
                else:
                    serializer = self.get_serializer_class()(data=request.data)

                if serializer.is_valid():
                    user = serializer.save(is_active=False, is_deleted=False)
                    thumbnail_url = None

                    ward = request.data.get("ward")
                    if ward:
                        user.ward = ward
                    if user.thumbnail:
                        thumbnail_url = request.build_absolute_uri(user.thumbnail.url)

                    role_type = request.data.get("role_type")
                    if role_type is not None:
                        try:
                            group = Group.objects.get(name=role_type)
                            user.group = group
                        except Group.DoesNotExist:
                            return Response(
                                {"message": "Invalid role_type"}, status=400
                            )

                    user.save()

                    return Response(
                        {
                            "message": "User successfully registered. Please check email and verify account",
                            "details": {
                                "username": user.username,
                                "is_active": user.is_active,
                                "designation": user.designation,
                                "role_type": user.group.name if user.group else None,
                                "is_deleted": user.is_deleted,
                                "thumbnail": thumbnail_url,
                                "email": user.email,
                                "ward": user.ward,
                            },
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return Response({"message": str(serializer.errors)}, status=400)

            else:
                return Response({"message": "Email is already registered"}, status=400)

        except Exception as error:
            return Response({"message": str(error)}, status=400)

    @swagger_auto_schema(
        operation_summary="Get user logs",
        tags=["user"],
        manual_parameters=userlogs_parameters,
    )
    @action(detail=False, methods=["get"])
    def userlog(self, request, *args, **kwargs):
        """
        This endpoint allows you to retrieve a list of logs for the user.

        The logs are filtered based on the query parameters provided in the request.
        One can apply various filters to narrow down the logs.

        Args:
            request (Request): The HTTP request object.

        Returns:
            Response: A response object containing the serialized log entries for the user in JSON format.

        """
        logs = LogEntry.objects.all()

        filter_class = LogEntryFilter(request.query_params, queryset=logs)
        filtered_queryset = filter_class.qs

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(filtered_queryset, request)

        serializer = UserLogSerializer(
            paginated_queryset, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)


class UserPermissionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Group.objects.all()
    serializer_class = UserGroupSerializerPermissions

    def list(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return Response(
                    status=status.HTTP_403_FORBIDDEN,
                    data={"message": "You are not logged in."},
                )
            group_id = request.user.group.id
            queryset = Group.objects.filter(pk=group_id)
            serializer = UserGroupSerializerPermissions(queryset, many=True)
            raw_data = serializer.data[0].get("permissions")

            def addition(n):
                return n.lower().replace(" ", "_")

            numbers = serializer.data[0].get("permissions")
            result = map(addition, numbers)
            return Response(result, status.HTTP_200_OK)
        except Exception as error:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"Error Message": str(error)}
            )


class UserRoleUniqueField(APIView):
    @swagger_auto_schema(
        operation_summary="Get unique user role",
        tags=["user_role_unique_values"],
    )
    def get(self, request):
        groups = Group.objects.all()
        group_names = [group.name for group in groups]
        group_names = sorted(group_names)

        return Response(group_names, status=status.HTTP_200_OK)


class UserSignIn(APIView):
    """
    API view to sign in a user.
    This view handles user sign-in functionality and returns a token if the provided credentials are valid.

    Parameters:
        - username, password

    Returns:
        - 200 OK: If sign-in is successful, returns a JSON response with the following keys:
            - token (str): Authentication token for the user.
            - user_id (int): The primary key of the authenticated user.
            - email (str): The email address of the authenticated user.
            - username (str): The username of the authenticated user.
        - 400 Bad Request: If the provided username or email does not exist in the system.
        - 403 Forbidden: If the provided password is incorrect.
        - 400 Bad Request: If the user is inactive and cannot be authenticated.

    """

    parser_classes = (FormParser, MultiPartParser)

    @swagger_auto_schema(
        operation_summary="Sign in a user",
        tags=["user"],
        manual_parameters=signin_parameters,
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user sign-in using provided credentials.

        Args:
            request, *args, **kwargs

        Returns:
        - Response:If successful, returns a Response containing the user's authentication token and relevant user information.
                   If the user is inactive, returns a Response with status code 400 and a message indicating the user's status.
                   If the provided password is incorrect, returns a Response with status code 403 and a message indicating an invalid password.
                   If the user does not exist, returns a Response with status code 400 and a message indicating that the user does not exist.

        """
        email = request.data.get("email")
        password = request.data.get("password")
        if User.objects.filter(Q(email=email)).exists():
            user = User.objects.filter(Q(email=email))[0]
            if user.check_password(password):
                if user.is_active:
                    token, created = Token.objects.get_or_create(user=user)
                    return Response(
                        {
                            "token": token.key,
                            "user_id": user.pk,
                            "email": user.email,
                            "username": user.username,
                        }
                    )
                return Response(
                    {"message": "The user is inactive"},
                    status=400,
                )
            return Response({"message": "Invalid password"}, status=403)
        return Response({"message": "User does not exist."}, status=400)


class UserLogoOut(APIView):
    """
    A view for user logout.

    Permission Classes:
    - IsAuthenticated: Only authenticated users can access this view.

    Methods:
    post(self, request, *args, **kwargs) -- Logout the authenticated user.

    """

    parser_classes = (FormParser, MultiPartParser)
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Sign out a user",
        tags=["user"],
    )
    def post(self, request, *args, **kwargs):
        """
        Logout the authenticated user.

        Parameters:
            request, *args, **kwargs

        Returns:
        - Response: If the user is successfully logged out, returns a Response with status code 200 and a success message.
                   If an error occurs during logout, returns a Response with status code 400 and an error message.

        """
        try:
            logout(request)
            return Response(
                {"message": "User Logout Successfully"},
                status=status.HTTP_200_OK,
            )
        except Exception as error:
            return Response(
                {"message": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )


def activate_user(request, uidb64, token):
    # User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password == confirm_password:
                user.set_password(new_password)
                user.is_active = True
                user.save()
                return render(
                    request,
                    "password_set.html",
                    {"action": "success", "uidb64": uidb64, "token": token},
                )
            else:
                return render(
                    request,
                    "password_set.html",
                    {"action": "mismatch", "uidb64": uidb64, "token": token},
                )
        else:
            return render(
                request,
                "password_set.html",
                {"action": "confirming", "uidb64": uidb64, "token": token},
            )
    else:
        return render(
            request,
            "password_set.html",
            {"action": "invalid_link", "uidb64": uidb64, "token": token},
        )


@swagger_auto_schema(
    method="post",
    operation_summary="Change user password",
    tags=["user"],
    manual_parameters=changepassword_parameters,
)
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
@parser_classes((FormParser, MultiPartParser))
def change_password(request):
    """
    Change user password.

    This endpoint allows an authenticated user to change their password by providing the old password,
    the new password, and confirming the new password.

    Parameters:
    - request (HttpRequest): The HTTP request object containing user data.

    Returns:
    - Response: If the password change is successful, returns a Response with status code 201 and a success message.
               If the new password and confirm password do not match, returns a Response with status code 400 and an error message.
               If the old password provided is incorrect, returns a Response with status code 400 and an error message.

    """
    old_password = request.data.get("old_password", None)
    new_password = request.data.get("new_password", None)
    confirm_password = request.data.get("confirm_password", None)
    user = authenticate(username=request.user.username, password=old_password)

    if user is not None:
        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            return Response(
                status=status.HTTP_201_CREATED,
                data={"Message": "Password Successfuly Updated."},
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Error": "New and Confirm passwords do not match."},
            )

    else:
        return Response(
            status=status.HTTP_400_BAD_REQUEST, data={"Error": "Incorrect old password"}
        )


@swagger_auto_schema(
    method="post",
    operation_summary="Reset password",
    tags=["user"],
    manual_parameters=forgotpassword_parameters,
)
@api_view(["POST"])
@permission_classes(())
@parser_classes((FormParser, MultiPartParser))
def forgot_password(request):
    """
    Reset password.

    This function allows a user to request a password reset by sending a password reset email
    with a unique uid and token for validation in the next function (reset_passoword).

    Parameters:
    - request (HttpRequest): The HTTP request object containing the user's email.

    Returns:
    - Response: -If a user exists with the provided email, sends a password reset email and returns
                    a Response with status code 200 and a success message indicating that the email has been sent.
                -If no user exists with the provided email, returns a Response with status code 404 and
                    a message indicating that the user does not exist.

    """
    email = request.data.get("email", None)
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        username = user.username if user.username else email.split("@")[0]

        # password reset link email
        current_site = settings.BACKEND_URL
        email_subject = "Reset Password for Mertic"
        template = "forgot_password_email_template.html"

        email_data = {
            "user": username.replace("_", " ").title(),
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
        }

        mail_to = str(request.data["email"])
        html_message = render_to_string(template, email_data)
        email_message = strip_tags(html_message)

        email_res = send_mail(
            email_subject,
            email_message,
            settings.EMAIL_HOST_USER,
            [
                email,
            ],
            html_message=html_message,
            fail_silently=False,
        )
        email_response = (
            "We have sent an link to reset your password. Please check your email"
            if email_res
            else "Could not send and email. Please try again later"
        )
        return Response({"Message": email_response}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"Message": "User does not exists with this email."},
            status=status.HTTP_404_NOT_FOUND,
        )


def reset_passoword(request, uidb64, token):
    """
    Check if the password change request is valid and reset the password if it is valid.

    This function checks if the password change request with the provided UID and token is valid.
    If valid, the function allows the user to reset their password.

    Parameters:
    - request (HttpRequest), uidb64, token.

    Returns:
    - HttpResponse: Renders the 'forgot_password_confirm_password.html' template with appropriate action based on the validity of the UID and token.
    """

    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                return render(
                    request,
                    "forgot_password_confirm_password.html",
                    {"action": "success", "uidb64": uidb64, "token": token},
                )
            else:
                return render(
                    request,
                    "forgot_password_confirm_password.html",
                    {"action": "mismatch", "uidb64": uidb64, "token": token},
                )
        else:
            return render(
                request,
                "forgot_password_confirm_password.html",
                {"action": "confirming", "uidb64": uidb64, "token": token},
            )
    else:
        return render(
            request,
            "forgot_password_confirm_password.html",
            {"action": "invalid_link", "uidb64": uidb64, "token": token},
        )


class UserProfile(APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user, context={"request": self.request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkshopModeViewSet(viewsets.ModelViewSet):
    queryset = WorkshopMode.objects.all()
    serializer_class = WorkshopModeSerializer
    http_method_names = ["post"]
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = [HasAddPermission]

    @swagger_auto_schema(
        operation_summary="Create or Update a Workshop Mode instance",
        tags=["workshop mode"],
    )
    def create(self, request, *args, **kwargs):
        existing_instance = WorkshopMode.objects.last()

        if existing_instance:
            serializer = self.get_serializer(
                existing_instance, data=request.data, partial=True
            )
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK if existing_instance else status.HTTP_201_CREATED,
        )
