from django.urls import path, re_path
from .views import SignupView, LoginView, ProfileView, LogoutView, RefreshTokenView, Send_password_request_Token, PasswordResetConfirmView, List_Users_based_on_role
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('user/profile/', ProfileView.as_view(), name='profile'),
    path('user/profile-role/', List_Users_based_on_role.as_view(), name='profile-role'),

    # auth urls
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password-reset/', Send_password_request_Token.as_view(), name='Send-reset-token'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='Confirm-password'),

     # Spectacular Schema Endpoints
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-ui'),
]
