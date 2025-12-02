# apps/users/urls.py
from django.urls import path
from apps.user.views import UserProfileView, OtpSendView \
                            , LoginView, LogoutView, RegisterView, DeleteAccountView \
                            , PhoneNumberChangeSendOTPView, PhoneNumberChangeVerifyView

urlpatterns = [
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/delete/", DeleteAccountView.as_view(), name="user-delete-account"),
    path("profile/PhoneNumberChangeSendOTP/", PhoneNumberChangeSendOTPView.as_view(), name="phone-number-send-otp"),
    path("profile/PhoneNumberChangeVerify/", PhoneNumberChangeVerifyView.as_view(), name="phone-number-verify"),
    path("auth/OTPSend/", OtpSendView.as_view(), name="otp-send"),
    path("auth/Login/", LoginView.as_view(), name="auth-login"),
    path("auth/Logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/Register/", RegisterView.as_view(), name="auth-register")
]
