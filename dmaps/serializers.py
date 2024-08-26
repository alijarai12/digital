from rest_framework import serializers
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
    Intro,
    UseCaseMajorFeature,
    WhyUseDmaps,
    Card,
    Image,
    Collaboration,
    Collaborator,
    GeometryFile,
    MunicipalityGeometry,
    ProvinceGeometry,
    FAQ,
    SDG,
    UseCaseDetail,
    SDGImage,
)


class NavBarSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = NavBar
        fields = "__all__"

    def get_icon(self, obj):
        request = self.context.get("request")
        if obj.icon:
            return request.build_absolute_uri(obj.icon.url).replace(
                "http://", "https://"
            )
        else:
            return None


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        image_url = instance.images.url
        data["images"] = (
            self.context["request"]
            .build_absolute_uri(image_url)
            .replace("http://", "https://")
        )
        return data


class CardSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Card
        exclude = ["benefit_en", "benefit_ne"]

    def get_icon(self, obj):
        request = self.context.get("request")
        if obj.icon:
            return request.build_absolute_uri(obj.icon.url).replace(
                "http://", "https://"
            )
        else:
            return None


class CardSerializerWhyUse(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = "__all__"

    def get_icon(self, obj):
        request = self.context.get("request")
        if obj.icon:
            return request.build_absolute_uri(obj.icon.url)
        else:
            return None


class CardSerializerMajorFeature(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    images = ImageSerializer(many=True, read_only=True, source="major_feature_images")

    class Meta:
        model = Card
        exclude = ["benefit_en", "benefit_ne"]

    def get_icon(self, obj):
        request = self.context.get("request")
        if obj.icon:
            return request.build_absolute_uri(obj.icon.url).replace(
                "http://", "https://"
            )
        else:
            return None


class MajorFeatureSerializer(serializers.ModelSerializer):
    cards = CardSerializer(
        many=True, read_only=True, source='card.filter(type="major_feature")'
    )

    class Meta:
        model = MajorFeature
        fields = "__all__"


class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = "__all__"


class FooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Footer
        fields = "__all__"


class AboutSerializer(serializers.ModelSerializer):
    class Meta:
        model = About
        fields = "__all__"


class MajorComponentSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True, source="major_component_card")

    class Meta:
        model = MajorComponent
        fields = "__all__"


class WeWorkWithSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True, source="we_work_with_card")

    class Meta:
        model = WeWorkWith
        fields = "__all__"


class ContactUsSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True, source="contact_us_card")

    class Meta:
        model = ContactUs
        fields = "__all__"


class UseCaseSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True, source="use_case_card")

    class Meta:
        model = UseCase
        fields = "__all__"


class IntroSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True, source="use_case_card")

    class Meta:
        model = Intro
        fields = "__all__"


class UseCaseMajorFeatureSerializer(serializers.ModelSerializer):
    cards = CardSerializer(
        many=True, read_only=True, source="use_case_major_feature_card"
    )

    class Meta:
        model = UseCaseMajorFeature
        fields = "__all__"


class WhyUseDmapsSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhyUseDmaps
        fields = "__all__"


class CollaborationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaboration
        fields = "__all__"


class CollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaborator
        fields = "__all__"
        extra_kwargs = {
            "email": {"required": True},
            "phone_no": {"required": True},
        }


class GeometryFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeometryFile
        fields = "__all__"
        read_only = ["id"]


class MunicipalityGeometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MunicipalityGeometry
        fields = "__all__"
        read_only = ["id"]


class ProvinceGeometrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProvinceGeometry
        fields = "__all__"
        read_only = ["id"]


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"
        read_only = ["id"]


class UseCaseDetailSerializer(serializers.ModelSerializer):
    # use_case_card = CardSerializer()

    class Meta:
        model = UseCaseDetail
        fields = [
            "topic_en",
            "topic_ne",
            "start_date",
            "end_date",
            "funding_agency_en",
            "funding_agency_np",
            "area_en",
            "area_ne",
            "task_completed_en",
            "task_completed_ne",
            "use_case_card",
        ]


class SDGImageSerializer(serializers.ModelSerializer):
    sdg_images = serializers.SerializerMethodField()

    class Meta:
        model = SDGImage
        fields = "__all__"

    def get_sdg_images(self, obj):
        request = self.context.get("request")
        if obj.sdg_images:
            return request.build_absolute_uri(obj.sdg_images.url).replace(
                "http://", "https://"
            )
        else:
            return None


class SDGSerializer(serializers.ModelSerializer):
    class Meta:
        model = SDG
        fields = "__all__"
