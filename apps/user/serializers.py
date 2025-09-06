import uuid
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from apps.user.models import PendingVerification

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "logo",
        )

class OTPSendSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=32)
    deep_link = serializers.CharField(read_only=True)

    def create(self, validated_data):
        token = uuid.uuid4()
        phone = validated_data['phone']
       
        deep_link = f"https://t.me/saveuzapp_bot?start={token}"
        PendingVerification.objects.create(phone=phone, uuid=token)
        validated_data['deep_link'] = deep_link
       
        return validated_data

class LoginSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(max_length=128, read_only=True)
    last_name = serializers.CharField(max_length=128, read_only=True)
    phone = serializers.CharField(max_length=32)
    code = serializers.CharField(max_length=5)
    token = serializers.CharField(max_length=128, read_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        user_exists = User.objects.filter(phone_number=attrs['phone']).first()
        if not user_exists:
            raise serializers.ValidationError({"phone": "User not found"})
        
        token, is_created = Token.objects.get_or_create(user=user_exists)
        attrs["token"] = token.key

        attrs['first_name'] = user_exists.first_name
        attrs['last_name'] = user_exists.last_name
        attrs['id'] = user_exists.pk

        return attrs
        
class RegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=5)
    token = serializers.CharField(max_length=128, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "code",
            "token",
            "fcm_token"
        )

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone_number=validated_data.get('phone_number'),
            fcm_token=validated_data.get("fcm_token")
        )

        token, created = Token.objects.get_or_create(user=user)
        validated_data['token'] = token.key
        
        return validated_data