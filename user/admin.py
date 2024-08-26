from django.contrib import admin
from .models import User, WorkshopMode
import csv
from django.http import HttpResponse


def export_as_csv(modelAdmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    model_name = queryset.model.__name__
    response["Content-Disposition"] = f'attachment; filename ="{model_name}.csv"'
    writer = csv.writer(response)
    fields = [field.name for field in queryset.model._meta.fields]
    writer.writerow(fields)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in fields])
    return response


export_as_csv.short_description = "Export as csv"


class UserAdmin(admin.ModelAdmin):
    actions = [export_as_csv]
    list_display = (
        "id",
        "username",
        "email",
        "group",
    )
    list_filter = (
        "gender",
        "group",
        "is_deleted",
        "is_active",
    )
    search_fields = (
        "id",
        "username",
        "designation",
        "email",
        "address",
    )
    exclude = ("password",)


class WorkshopModeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "workshop_mode",
    )
    list_filter = (
        "id",
        "workshop_mode",
    )
    search_fields = (
        "id",
        "workshop_mode",
    )


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(WorkshopMode, WorkshopModeAdmin)
