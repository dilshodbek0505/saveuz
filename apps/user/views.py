# apps/users/views.py
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.core.cache import cache
from django.contrib.auth import get_user_model

from apps.user.serializers import UserProfileSerializer, OTPSendSerializer \
                                  , LoginSerializer, RegisterSerializer

User = get_user_model()


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

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
            return Response({"msg": "error"}, status=400)

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
