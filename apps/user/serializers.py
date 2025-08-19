import uuid
from rest_framework import serializers

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
    phone = serializers.CharField(max_length=32)
    code = serializers.CharField(max_length=4)
    token = serializers.CharField(max_length=128, read_only=True)

    def validate(self, attrs):
        from rest_framework.authtoken.models import Token
        attrs = super().validate(attrs)

        user_exists = User.objects.filter(phone_number=attrs['phone']).first()
        if not user_exists:
            raise serializers.ValidationError({"phone": "User not found"})
        
        token, is_created = Token.objects.get_or_create(user=user_exists)
        attrs["token"] = token.key

        return attrs
        
class RegisterSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=4, read_only=True)
    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "code",
        )

    