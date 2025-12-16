from django.contrib.auth import get_user_model
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiTypes
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name",
            "display_name", "role", "promoter_type", "is_promoter_approved",
            "city", "country", "bio", "avatar",
        )
        read_only_fields = ("username", "role", "is_promoter_approved")


class UserUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)
    remove_avatar = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email", "display_name",
            "bio", "avatar", "remove_avatar", "city", "country", "promoter_type",
        )

    def validate_email(self, value):
        # optional: allow updating email only if not taken by another user
        if value and User.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def update(self, instance, validated_data):
        remove = validated_data.pop("remove_avatar", False)
        instance = super().update(instance, validated_data)
        if remove and instance.avatar:
            instance.avatar.delete(save=False)
            instance.avatar = None
            instance.save(update_fields=["avatar"])
        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    token = serializers.SerializerMethodField(read_only=True)
    role = serializers.CharField(required=False)  

    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "password", "token")
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
        }

    def validate_role(self, value: str):
        if not value:
            return User.Roles.ARTIST
        v = str(value).upper()
        if v == "USER":
            v = User.Roles.PROMOTER
        allowed = {choice for choice, _ in User.Roles.choices}
        if v not in allowed:
            raise serializers.ValidationError(f"Invalid role. Choose one of: {', '.join(allowed)}")
        return v

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.pop("role", User.Roles.ARTIST)
        user = User.objects.create_user(password=password, role=role, **validated_data)
        return user

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return {"access": str(refresh.access_token), "refresh": str(refresh)}


class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()