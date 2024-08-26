from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group
from user.models import WorkshopMode


def get_permission_list(request):
    group_id = request.user.group.id
    permission_qs = Group.objects.get(id=group_id).permissions.all().values("codename")
    permission_list = [data["codename"] for data in permission_qs]
    return permission_list


def workshop_mode_status():
    try:
        latest_workshop_instance = WorkshopMode.objects.last()
        workshop_mode_status = latest_workshop_instance.workshop_mode
        return workshop_mode_status
    except WorkshopMode.DoesNotExist:
        return False


class HasViewPermission(BasePermission):
    message = {"message": "You don't have permission to view this page."}

    def has_permission(self, request, view):
        try:
            workshop_mode = workshop_mode_status()
            if workshop_mode:
                return True

            permission_list = get_permission_list(request)

            model_name = view.queryset.model.__name__
            required_permission = f"view_{model_name.lower()}"

            if required_permission in permission_list:
                return True

            return False
        except Exception as e:
            return False


class HasChangePermission(BasePermission):
    message = {"message": "You don't have permission to change this page."}

    def has_permission(self, request, view):
        try:
            workshop_mode = workshop_mode_status()
            if workshop_mode:
                return True

            permission_list = get_permission_list(request)

            model_name = view.queryset.model.__name__
            required_permission = f"change_{model_name.lower()}"

            if required_permission in permission_list:
                return True

            return False
        except Exception as e:
            return False


class HasAddPermission(BasePermission):
    message = {"message": "You don't have permission to add data."}

    def has_permission(self, request, view):
        try:
            workshop_mode = workshop_mode_status()
            if workshop_mode:
                return True

            permission_list = get_permission_list(request)

            model_name = view.queryset.model.__name__
            required_permission = f"add_{model_name.lower()}"

            if required_permission in permission_list:
                return True

            return False
        except Exception as e:
            return False


class HasDeletePermission(BasePermission):
    message = {"message": "You don't have permission to delete this data."}

    def has_permission(self, request, view):
        try:
            workshop_mode = workshop_mode_status()
            if workshop_mode:
                return True

            permission_list = get_permission_list(request)

            model_name = view.queryset.model.__name__
            required_permission = f"delete_{model_name.lower()}"

            if required_permission in permission_list:
                return True

            return False
        except Exception as e:
            return False
