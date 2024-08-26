from django.contrib import admin
from .models import (
    NavBar,
    Header,
    Footer,
    About,
    MajorFeature,
    MajorComponent,
    WeWorkWith,
    ContactUs,
    UseCase,
    UseCaseMajorFeature,
    Card,
    Image,
    Collaboration,
    Collaborator,
    MunicipalityGeometry,
    ProvinceGeometry,
    GeometryFile,
    FAQ,
    SDG,
    SDGImage,
    UseCaseDetail,
)

# Register your models here.


@admin.register(NavBar)
class NavBarAdmin(admin.ModelAdmin):
    list_display = ["id", "title_en", "title_ne"]
    list_filter = ["title_en"]
    search_fields = ["id", "title_en", "title_ne"]


@admin.register(Header)
class HeaderAdmin(admin.ModelAdmin):
    list_display = ["id", "page", "title_en", "title_ne"]
    list_filter = ["page"]
    search_fields = ["title_en", "title_ne"]


@admin.register(Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ["id", "phone_no", "email"]
    search_fields = ["phone_no", "email"]


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ["id", "title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]


@admin.register(MajorFeature)
class MajorFeatureAdmin(admin.ModelAdmin):
    list_display = ["id", "title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]


@admin.register(MajorComponent)
class MajorComponentAdmin(admin.ModelAdmin):
    list_display = ["id", "title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]


@admin.register(WeWorkWith)
class WeWorkWithAdmin(admin.ModelAdmin):
    list_display = ["id", "partner", "title_en", "title_ne"]
    list_filter = ["partner"]
    search_fields = ["title_en", "title_ne"]


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ["id", "title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]


@admin.register(UseCase)
class UseCaseAdmin(admin.ModelAdmin):
    list_display = ["id", "title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]


@admin.register(UseCaseMajorFeature)
class UseCaseMajorFeatureAdmin(admin.ModelAdmin):
    list_display = ["id", "title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ["id", "page", "title_en", "title_ne"]
    list_filter = ["page"]
    search_fields = ["title_en", "title_ne"]
    # def major_feature_name(self, obj):
    #     return obj.major_feature.title_en
    # major_feature_name.short_description = "Major Feature (EN)"


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ["id", "images"]
    search_fields = ["images"]
    search_fields = ["images"]


admin.site.register(Collaboration)


class CollaborationAdmin(admin.ModelAdmin):
    list_display = ["id", "title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]
    search_fields = ["title_en", "title_ne"]


admin.site.register(Collaborator)


class CollaboratorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "collaborator",
        "email",
        "organization_name",
        "phone_no",
        "designation",
    )
    list_filter = ("collaborator", "organization_name", "designation")
    search_fields = ("name", "email", "organization_name", "designation")


@admin.register(GeometryFile)
class GeometryFileAdmin(admin.ModelAdmin):
    list_display = ("file_type", "file_upload")
    list_filter = ("file_type", "file_upload")
    search_fields = ("file_type", "file_upload")


@admin.register(MunicipalityGeometry)
class MunicipalityGeometryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "area")
    # list_filter = ("name",)
    search_fields = ("name",)


@admin.register(ProvinceGeometry)
class ProvinceGeometryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "area")
    list_filter = ("name",)
    search_fields = (
        "name",
        "area",
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("id", "title_en", "title_ne")
    search_fields = ("title_en", "description_en")

    def __str__(self):
        return str(self.id)


@admin.register(SDG)
class SDGAdmin(admin.ModelAdmin):
    list_display = ("id", "title_en", "title_ne", "use_case_card")
    search_fields = ["title_en", "title_ne", "use_case_card__title"]

    def __str__(self):
        return str(self.id)


@admin.register(SDGImage)
class SDGImageAdmin(admin.ModelAdmin):
    list_display = ("id", "sdg_images", "sdg_data")
    search_fields = ("id",)

    def __str__(self):
        return str(self.id)


@admin.register(UseCaseDetail)
class UseCaseDetailAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "topic_en",
        "start_date",
        "end_date",
        "funding_agency_en",
        "area_en",
    )
    search_fields = ["topic_en", "funding_agency_en", "area_en"]
    list_filter = ["funding_agency_en"]

    def __str__(self):
        return str(self.id)
