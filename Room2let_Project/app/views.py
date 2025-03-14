from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken  # JWT Tokens

from .serializers import SignupSerializer, LoginSerializer, UserProfileSerializer
from .schemas import signup_schema, login_schema, edit_profile_schema

UserProfile = get_user_model()

class SignupView(APIView):
    """
    User Signup API (No Authentication Required)
    """
    permission_classes = [AllowAny]  # Anyone can sign up

    @signup_schema
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate JWT Token on signup
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    User Login API (No Authentication Required)
    """
    permission_classes = [AllowAny]  # Anyone can log in

    @login_schema
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate JWT Token on login
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """
    Edit and Get Profile
    """
    permission_classes = [IsAuthenticated]

    @edit_profile_schema
    def get(self, request):
        """
        Get the authenticated user's profile.
        """
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @edit_profile_schema
    def patch(self, request):
        """
        Edit the authenticated user's profile.
        """
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
