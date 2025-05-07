from django.contrib.auth import authenticate, get_user_model
from .models import Interest, Property
from .permissions import IsAgentOrReadOnly
from rest_framework import status
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from rest_framework_simplejwt.tokens import RefreshToken  # JWT Tokens
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail
from django.conf import settings
from drf_spectacular.utils import extend_schema_view 
from django.utils.http import urlsafe_base64_decode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .emails import password_reset_email

from .serializers import (
    SignupSerializer, PropertySerializer, 
    LoginSerializer, UserProfileSerializer, 
    SendPasswordRequestTokenSerializer, PasswordResetConfirmViewSerializer
)

from .schemas import (
    list_my_properties_schema, create_property_schema, retrieve_property_schema,
    update_property_schema, delete_property_schema, list_public_properties_schema,
    retrieve_public_property_schema, signup_schema, login_schema, edit_profile_schema,
    send_password_request_token_schema, password_reset_confirm_schema, logout_schema,
    list_users_based_on_role_schema, search_properties_schema
)

UserProfile = get_user_model()

#Authentication

class SignupView(APIView):
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
    permission_classes = [IsAuthenticated]

    @logout_schema
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})
        



class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @edit_profile_schema
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @edit_profile_schema
    def patch(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ListUsersbasedOnRole(APIView):
    permission_classes = [IsAuthenticated]

    @list_users_based_on_role_schema
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

        
    
        
#--------------------------------------------------------------------------------------#


#Password reset   

class SendPasswordRequestToken(APIView):
    permission_classes = [AllowAny]

    @send_password_request_token_schema
    def post(self, request):
        serializer = SendPasswordRequestTokenSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = UserProfile.objects.get(email=email)

                # generate token for the user instance
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                password_reset_email(uidb64, token, email)
                return Response({"message": "Password reset token sent to your email if it exists"}, status=status.HTTP_200_OK) 

            except UserProfile.DoesNotExist:
                pass
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @password_reset_confirm_schema
    def post(self, request):
        serializer = PasswordResetConfirmViewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"details": "Pasword has being reset successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    get=list_my_properties_schema
)
class ListPropertiesView(ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, IsAgentOrReadOnly]

    def get_queryset(self):
        if self.request.user.role != 'agent':
            return Property.objects.none()
        return Property.objects.filter(user=self.request.user)

@extend_schema_view(
    post=create_property_schema
)
class CreatePropertyView(CreateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, IsAgentOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)  

@extend_schema_view(
    get=retrieve_property_schema
)
class RetrievePropertyView(RetrieveAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_object(self):
        try:
            return Property.objects.get(pk=self.kwargs["pk"], user=self.request.user)
        except Property.DoesNotExist:
            self.permission_denied(
                self.request,
                message="Property not found or you do not have permission."
            )

@extend_schema_view(
    patch=update_property_schema
)
class UpdatePropertyView(UpdateAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    http_method_names = ["patch"]  

    def get_queryset(self):
        return Property.objects.filter(user=self.request.user)


@extend_schema_view(
    delete=delete_property_schema
)
class DeletePropertyView(DestroyAPIView):
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, IsAgentOrReadOnly]
    lookup_field = "pk"

    def get_queryset(self):
        return Property.objects.filter(user=self.request.user)


@extend_schema_view(
    get=list_public_properties_schema
)
class ListPublicPropertiesView(ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Property.objects.all()

@extend_schema_view(
    get=retrieve_public_property_schema
)
class RetrievePublicPropertyView(RetrieveAPIView):
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]
    lookup_field = "pk"

    def get_queryset(self):
        return Property.objects.all()


@extend_schema_view(
    get=search_properties_schema
)
class SearchPropertiesView(ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        request = self.request
        user = request.user

        # Get query params
        property_type = request.query_params.get("property_type")
        purpose = request.query_params.get("purpose")
        state = request.query_params.get("state")
        local_govt = request.query_params.get("local_govt")
        area = request.query_params.get("area")
        max_price = request.query_params.get("max_price")
        bedrooms = request.query_params.get("bedrooms")

        filters = Q()
        if property_type:
            filters &= Q(property_type__icontains=property_type)
        if purpose:
            filters &= Q(purpose__iexact=purpose)
        if state:
            filters &= Q(state__icontains=state)
        if local_govt:
            filters &= Q(local_Govt__icontains=local_govt)
        if area:
            filters &= Q(area_located_or_close_to__icontains=area)
        if max_price:
            filters &= Q(price__lte=max_price)
        if bedrooms:
            filters &= Q(bedrooms__gte=bedrooms)

        # Reject request if no valid param
        if not any([property_type, purpose, state, local_govt, area, max_price, bedrooms]):
            return Property.objects.none()  # Or raise ValidationError if you'd rather

        queryset = Property.objects.filter(filters)

        # Log interest only if local govt is provided and user is authenticated
        if user.is_authenticated and local_govt:
            Interest.objects.get_or_create(
                user=user,
                state=state or "",
                local_Govt=local_govt,
                search_query=f"{property_type or ''} {purpose or ''} {area or ''}".strip()
            )

        return queryset