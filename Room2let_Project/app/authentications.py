from .models import BlacklistedAccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        auth = super().authenticate(request)
        if auth is None:
            return None

        user, token = auth

        #Check if the access token is blacklisted
        if BlacklistedAccessToken.objects.filter(token=str(token)).exists():
            raise AuthenticationFailed("This access token has been blacklisted.")  

        return user, token
