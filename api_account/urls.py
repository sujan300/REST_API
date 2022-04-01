from django.urls import path
from .views import UserRegisterView
from api_account import views


urlpatterns = [
    path("register/",UserRegisterView.as_view(),name="signup"),
    path("get/",UserRegisterView.as_view(),name="get_users"),
    path("get/<int:pk>/",UserRegisterView.as_view(),name="gat_user"),
    path('login/',views.UserLogInView.as_view(),name="login"),
    path("profile/",views.UserProfileView.as_view(),name="user_profile"),
    path("changepassword/",views.UserPasswordChangeView.as_view(),name="change_password"),
    path("passwordrest/",views.UserResetPasswordEmailSendView.as_view(),name="resetpassword"),
    path("validate-link/<uid>/<token>/",views.UserValidateAndResetPasswordView.as_view(),name="validate_and_change_password"),
]