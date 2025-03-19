from django.contrib.auth import authenticate, get_user_model
from .models import Property
from .permissions import IsAgentOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken  # JWT Tokens
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_decode
# from django.utils.encoding import force_text
from .serializers import SignupSerializer, PropertySerializer, LoginSerializer, UserProfileSerializer, Send_password_request_Token_serializer, PasswordResetConfirmViewSerializer

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

#Authentication

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


class LogoutView(APIView):
    """
    Logout API
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        


#===============================================================================#
#================================================================================#


#View Profile Info

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
    

class List_Users_based_on_role(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        role = request.query_params.get("role", None)

        valid_roles = ['agent', 'user']

        if role not in valid_roles and role is not None:
            return Response({"error": "Invalid role. Enter valid role"}, status=status.HTTP_400_BAD_REQUEST)  

        
        if role is not None:
            users = UserProfile.objects.filter(role=role.lower())

        else:
            users = UserProfile.objects.all()

        serializer = UserProfileSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

        
    
#=======================================================================================#
#=======================================================================================#       



#Password reset   

class Send_password_request_Token(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        # validate email
        serializer = Send_password_request_Token_serializer(data=request.data)

        if serializer.is_valid():

            # Get the email
            email = serializer.validated_data["email"]

            # Get user instance associated with the email
            try:
                user = UserProfile.objects.get(email=email)

                # generate token for the user instance
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))


                # send email to the user

                subject ="Password Reset Token"

                reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm/{uidb64}/{token}"

                message = f"""
                Hello,
                
                You have requested to reset your password. Please click the link below to reset your password:
                
                {reset_url}
                
                If you did not request this, please ignore this email.
                
                Thank you.
                """

                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False,)

                return Response({"message": "Password reset token sent to your email if it exists"}, status=status.HTTP_200_OK) 

            except UserProfile.DoesNotExist:
                pass
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PasswordResetConfirmViewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"details": "Pasword has being reset successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#====================================================================================#
#====================================================================================#

# Property Views

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