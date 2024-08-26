from django_filters import rest_framework as filters
from django.contrib.admin.models import LogEntry
from user.models import User
from django_filters import rest_framework as df_filters
from django_filters.fields import CSVWidget, MultipleChoiceField
from django.db.models import Q


class MultipleField(MultipleChoiceField):
    def valid_value(self, value):
        return True


class MultipleFilter(df_filters.MultipleChoiceFilter):
    field_class = MultipleField


class LogEntryFilter(filters.FilterSet):
    """
    http://localhost:8000/api/v1/user/user/userlog/?action_time__date__gte=2023-07-01&username=admin
    """

    username = filters.CharFilter(field_name="user__username", lookup_expr="icontains")
    action_time = filters.DateTimeFilter(field_name="action_time", lookup_expr="exact")
    content_type = filters.CharFilter(
        field_name="content_type__model", lookup_expr="exact"
    )
    object_id = filters.CharFilter(field_name="object_id", lookup_expr="exact")

    class Meta:
        model = LogEntry
        fields = {
            # "username": ["exact", "icontains"],
            "action_time": ["exact", "date__gte", "date__lte"],
            "content_type": ["exact"],
            "object_id": ["exact"],
        }


class UserFilter(filters.FilterSet):
    """
    http://localhost:8080/api/v1/user/user/?ward=2,3
    """

    is_active = filters.BooleanFilter(field_name="is_active", method="filter_is_active")
    username = MultipleFilter(
        field_name="username", lookup_expr="icontains", widget=CSVWidget
    )
    designation = MultipleFilter(
        field_name="designation", lookup_expr="icontains", widget=CSVWidget
    )

    class Meta:
        model = User
        fields = [
            "username",
            "designation",
            "is_active",
        ]

    def filter_queryset(self, queryset):
        params = self.data
        q_obj = Q()
        if "ward" in params and params["ward"]:
            q_obj = Q()
            ward_numbers = params.get("ward")
            ward_no_values = [int(value) for value in ward_numbers.split(",")]
            for ward_no_value in ward_no_values:
                q_obj |= Q(ward__contains=ward_no_value)
            queryset = queryset.filter(q_obj)
        return queryset

    def filter_is_active(self, queryset, name, value):
        if value is not None:
            return queryset.filter(is_active=value)
        return queryset
