from django.urls import path, re_path
from .views import SignupView, LoginView, ProfileView, LogoutView, SendPasswordRequestToken, PasswordResetConfirmView
from .views import (
    SignupView, LoginView, 
    ProfileView, ListPropertiesView, 
    CreatePropertyView, UpdatePropertyView, 
    DeletePropertyView, RetrievePropertyView, 
    ListPublicPropertiesView, RetrievePublicPropertyView,
    ListUsersbasedOnRole
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('user/profile/', ProfileView.as_view(), name='profile'),
    path('user/profile-role/', ListUsersbasedOnRole.as_view(), name='profile-role'),

    # auth urls
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/password-reset/', SendPasswordRequestToken.as_view(), name='Send-reset-token'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='Confirm-password'),

    # property urls
    path('property/agent/list', ListPropertiesView.as_view(), name='list-property'),
    path('property/agent/detail/<int:pk>', RetrievePropertyView.as_view(), name='property-detail'),
    path('property/agent/create', CreatePropertyView.as_view(), name='create-property'),
    path('property/agent/update/<int:pk>', UpdatePropertyView.as_view(), name='update-property'),
    path('property/agent/delete/<int:pk>', DeletePropertyView.as_view(), name='delete-property'),
    path('property/public', ListPublicPropertiesView.as_view(), name='public-properties'),
    path('property/public/detail/<int:pk>', RetrievePublicPropertyView.as_view(), name='public-property-detail'),

    # Spectacular Schema Endpoints
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-ui'),
]
