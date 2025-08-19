# apps/users/urls.py
from django.urls import path
from apps.user.views import UserProfileView, OtpSendView \
                            , LoginView, LogoutView, RegisterView

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("auth/OTPSend/", OtpSendView.as_view(), name="otp-send"),
    path("auth/Login/", LoginView.as_view(), name="auth-login"),
    path("auth/Logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/Register/", RegisterView.as_view(), name="auth-register")
]
