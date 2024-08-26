import django_filters
from dmaps.models import Header, UseCase, WeWorkWith, Card


class HeaderFilter(django_filters.FilterSet):
    class Meta:
        model = Header
        fields = ["page"]


class UseCaseFilter(django_filters.FilterSet):
    class Meta:
        model = UseCase
        fields = ["use_case"]


class WeWorkWithFilter(django_filters.FilterSet):
    class Meta:
        model = WeWorkWith
        fields = ["partner"]


class CardFilter(django_filters.FilterSet):
    class Meta:
        model = Card
        fields = ["type"]
