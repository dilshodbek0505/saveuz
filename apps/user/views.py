# apps/users/views.py
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.core.cache import cache
from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.user.serializers import UserProfileSerializer, OTPSendSerializer \
                                  , LoginSerializer, RegisterSerializer \
                                  , PhoneNumberChangeSendOTPSerializer, PhoneNumberChangeVerifySerializer

User = get_user_model()


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    


class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        
        # Token'ni o'chirish
        try:
            Token.objects.filter(user=user).delete()
        except Exception:
            pass
        
        # Soft delete - user'ni deactivate qilish
        user.is_active = False
        user.save()
        
        return Response(
            {"message": "Account successfully deactivated"},
            status=status.HTTP_200_OK
        )


class PhoneNumberChangeSendOTPView(generics.CreateAPIView):
    serializer_class = PhoneNumberChangeSendOTPSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Send OTP code to new phone number for phone number change",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone_number'],
            properties={
                'phone_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New phone number (without +998)',
                    example='901234567'
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="OTP code sent successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'phone_number': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: "Bad Request - Phone number already in use or invalid",
            401: "Unauthorized"
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class PhoneNumberChangeVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Verify OTP code and change phone number",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['phone_number', 'code'],
            properties={
                'phone_number': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='New phone number (without +998)',
                    example='901234567'
                ),
                'code': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='OTP code received via SMS',
                    example='12345'
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Phone number changed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Success message'
                        ),
                        'phone_number': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='New phone number'
                        )
                    }
                )
            ),
            400: "Bad Request - Invalid code, expired code, or phone number already in use",
            401: "Unauthorized"
        }
    )
    def post(self, request):
        serializer = PhoneNumberChangeVerifySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        new_phone_number = serializer.validated_data['phone_number']
        
        # Phone numberni yangilash
        user.phone_number = new_phone_number
        user.save()
        
        lang = request.headers.get("Accept-Language", "uz")
        message = "Telefon raqam muvaffaqiyatli o'zgartirildi"
        if lang == "ru":
            message = "Номер телефона успешно изменен"
        if lang == "en":
            message = "Phone number successfully changed"
        
        return Response(
            {"message": message, "phone_number": new_phone_number},
            status=status.HTTP_200_OK
        )

class OtpSendView(generics.CreateAPIView):
    serializer_class = OTPSendSerializer
    permission_classes = [permissions.AllowAny]

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=200)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"msg": "Logged out"}, status=200)
        except Exception as err:
            return Response({"msg": "error"}, status=200)

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
