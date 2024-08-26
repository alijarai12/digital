from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.contrib.admin.models import LogEntry
from rest_framework import serializers
from rest_framework.views import Response
from user.models import User, WorkshopMode
from user.utils import time_ago_from_datetime
import json


class UserSerializer(serializers.ModelSerializer):
    role_type = serializers.CharField(source="group.name", read_only=True)
    date_joined = serializers.DateTimeField(
        source="date_created", format="%Y-%m-%d", read_only=True
    )
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "designation",
            "is_active",
            "role_type",
            "ward",
            "thumbnail",
            "date_joined",
            "last_login",
            "is_deleted",
            "date_modified",
        )

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            return self.context["request"].build_absolute_uri(obj.thumbnail.url)
        return None


class UserPostSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    designation = serializers.CharField(required=True)
    ward = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "gender",
            "phone",
            "address",
            "designation",
            "image",
            "ward",
            "date_modified",
        ]


class UserPatchSerializer(serializers.ModelSerializer):
    delete_image = serializers.BooleanField(required=False)
    role_type = serializers.CharField(required=False)
    ward = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "is_active",
            "designation",
            # "group",
            "ward",
            "is_deleted",
            "image",
            "delete_image",
            "role_type",
            "date_modified",
        )

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get("is_active", instance.is_active)

        username = validated_data.get("username", None)
        if username:
            instance.username = username

        designation = validated_data.get("designation", None)
        if designation:
            instance.designation = designation

        is_deleted = validated_data.get("is_deleted", None)
        if is_deleted is not None:
            instance.is_deleted = is_deleted

        image = validated_data.get("image")
        if image:
            instance.image = image

        delete_image = validated_data.get("delete_image", False)
        if delete_image:
            instance.image.delete(save=True)
            instance.thumbnail.delete()
            instance.image = None

        role_type = validated_data.get("role_type")

        ward = validated_data.get("ward")
        if ward is not None and isinstance(ward, str):
            try:
                ward_data = json.loads(ward)
                instance.ward = ward_data
            except json.JSONDecodeError:
                return Response({"message": "Invalid JSON format for ward"}, status=400)
        elif ward is not None:
            return Response({"message": "Invalid ward format"}, status=400)

        if role_type:
            try:
                print("inside role type", role_type)
                group = Group.objects.get(name=role_type)
                instance.group = group
            except Group.DoesNotExist:
                return Response({"message": "Invalid role_type"}, status=400)

        instance.save()

        return instance


class UserLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    action_time = serializers.SerializerMethodField()
    change = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = ["username", "action_time", "change", "image_url"]

    def get_username(self, obj):
        return obj.user.username if obj.user else None

    def get_action_time(self, obj):
        return time_ago_from_datetime(obj.action_time)

    def get_change(self, obj):
        if obj.is_change():
            return f"Changed {obj.content_type.name} {obj.object_repr}"
        elif obj.is_addition():
            return f"Added {obj.content_type.name} {obj.object_repr}"
        elif obj.is_deletion():
            return f"Deleted {obj.content_type.name} {obj.object_repr}"
        else:
            return ""

    def get_image_url(self, obj):
        if hasattr(obj, "user") and obj.user.image:
            return self.context["request"].build_absolute_uri(obj.user.image.url)
        return None


class UserGroupSerializerPermissions(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ["permissions"]

    def get_permissions(self, obj):
        if obj.permissions:
            data = []
            qs = obj.permissions.all().values("codename")
            for q in qs:
                data.append(q["codename"])
            return data
        return data


class WorkshopModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkshopMode
        fields = "__all__"
