from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from user.viewsets import (
    UserSignIn,
    UserLogoOut,
    activate_user,
    change_password,
    forgot_password,
    reset_passoword,
    UserViewset,
    UserRoleUniqueField,
    UserPermissionViewSet,
    UserProfile,
    WorkshopModeViewSet,
)


router = routers.DefaultRouter()
router.register(r"user", UserViewset, basename="user")
router.register(r"permissions", UserPermissionViewSet, basename="permissions")
router.register(r"workshop-mode", WorkshopModeViewSet, basename="workshop_mode")

urlpatterns = [
    path("", include(router.urls)),
    path("sign-in/", UserSignIn.as_view()),
    path("logout/", UserLogoOut.as_view()),
    path(
        "email-verification/<str:uidb64>/<str:token>/",
        activate_user,
        name="email_activate",
    ),
    path("change-password/", change_password, name="change_password"),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path(
        "reset-password/<str:uidb64>/<str:token>/",
        reset_passoword,
        name="reset_password",
    ),
    path(
        "user-role-unique-fields",
        UserRoleUniqueField.as_view(),
        name="user_role_unique_fields",
    ),
    path("profile/", UserProfile.as_view(), name="user-profile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
