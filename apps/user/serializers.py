import uuid
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.user.models import PendingVerification
from apps.user.utils import SMSBusiness

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

    def get_lang(self):
        res = self.context.get("request")
        if res:
            lang = res.headers.get("Accept-Language", "uz")
            
        return lang or "uz"

    def generate_code(self):
        import secrets
        return str(secrets.randbelow(90000) + 10000)

    def get_text(self):
        code = self.generate_code()
        return code, f"Kodni hech kimga bermang! Saveuz mobil ilovasiga kirish uchun tasdiqlash kodi: {code}"
        
    def create(self, validated_data):
        phone = validated_data.get("phone")
        code, text = self.get_text()
        
        cache_key = f"sms:{phone}"
        cache.set(cache_key, code, timeout=60*2)

        sms_business = SMSBusiness(phone=f"998{phone}", text=text)
        if sms_business.send_sms() != 200:
            raise serializers.ValidationError({"msg": "sms yuborishda xatolik sodir bo'ldi"})

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
        
        phone = attrs['phone'] 
        code = attrs['code']

        cache_key = f"sms:{phone}"
        saved_code = cache.get(cache_key)

        if not saved_code or saved_code != code:
            raise serializers.ValidationError({"msg": "Kod noto‘g‘ri yoki muddati tugagan"})

        cache.delete(cache_key)

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