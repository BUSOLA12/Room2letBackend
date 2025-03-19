from django.contrib.auth import authenticate, get_user_model
from .models import Property
from .permissions import IsAgentOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken  # JWT Tokens

from .serializers import PropertySerializer, SignupSerializer, LoginSerializer, UserProfileSerializer
from .schemas import (
    signup_schema, 
    login_schema, 
    edit_profile_schema,
    add_property_schema,
    get_my_properties_schema,
    get_all_properties_schema,
    update_property_schema,
    delete_property_schema
)

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
    

class PropertyView(APIView):
    permission_classes = [IsAuthenticated, IsAgentOrReadOnly]

    @get_my_properties_schema
    def get(self, request, pk=None):
        """Agents can retrieve only their properties."""
        if not request.user.is_authenticated or request.user.role != 'agent':
            return Response({"error": "Only agents can view their own properties"}, status=status.HTTP_403_FORBIDDEN)

        if pk:
            try:
                property_obj = Property.objects.get(pk=pk, user=request.user)
                serializer = PropertySerializer(property_obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Property.DoesNotExist:
                return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

        properties = Property.objects.filter(user=request.user)
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @add_property_schema
    def post(self, request):
        """Create a new property (Only agents can create)"""
        serializer = PropertySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  # Assign logged-in user as the property owner
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @update_property_schema
    def put(self, request, pk):
        """Update a property (Only the agent who owns the property can update)"""
        try:
            property_obj = Property.objects.get(pk=pk, user=request.user)
        except Property.DoesNotExist:
            return Response({"error": "Property not found or you do not have permission"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PropertySerializer(property_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @delete_property_schema
    def delete(self, request, pk):
        """Delete a property (Only the agent who owns the property can delete)"""
        try:
            property_obj = Property.objects.get(pk=pk, user=request.user)
            property_obj.delete()
            return Response({"message": "Property deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Property.DoesNotExist:
            return Response({"error": "Property not found or you do not have permission"}, status=status.HTTP_404_NOT_FOUND)


class PublicPropertyAPIView(APIView):
    """Anyone can view all properties from all agents."""
    permission_classes = [AllowAny]

    @get_all_properties_schema
    def get(self, request, pk=None):
        """Retrieve all properties or a single property."""
        if pk:
            try:
                property_obj = Property.objects.get(pk=pk)
                serializer = PropertySerializer(property_obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Property.DoesNotExist:
                return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

        properties = Property.objects.all()
        serializer = PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)