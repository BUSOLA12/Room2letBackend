from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import SignupSerializer, LoginSerializer, UserProfileSerializer

signup_schema = extend_schema(
    request=SignupSerializer,
    responses={
        201: OpenApiResponse({"message": "User created successfully"}),
        400: OpenApiResponse({"error": "Invalid data"}),
    }
)

login_schema = extend_schema(
    request=LoginSerializer,
    responses={
        200: OpenApiResponse({"token": "your-auth-token"}),
        401: OpenApiResponse({"error": "Invalid credentials"}),
    }
)

edit_profile_schema = extend_schema(
    request=UserProfileSerializer, 
    responses={200: UserProfileSerializer}
)
