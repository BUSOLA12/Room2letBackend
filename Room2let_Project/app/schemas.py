from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import serializers
from .serializers import (
    SignupSerializer, 
    LoginSerializer,
    PropertySerializer,
    UserProfileSerializer,
    SendPasswordRequestTokenSerializer,
    PasswordResetConfirmViewSerializer
)

# Authentication Schemas

signup_schema = extend_schema(
    summary="User Signup",
    description="Registers a new user and returns a JWT token.",
    request=SignupSerializer,
    responses={
        201: {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "refresh": {"type": "string"},
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "email": {"type": "string"},
                        "role": {"type": "string"},
                    },
                },
            },
        },
        400: {"description": "Invalid input data"},
    },
)

login_schema = extend_schema(
    summary="User Login",
    description="Authenticates a user and returns a JWT token.",
    request=LoginSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "refresh": {"type": "string"},
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "username": {"type": "string"},
                        "email": {"type": "string"},
                        "role": {"type": "string"},
                    },
                },
            },
        },
        400: {"description": "Invalid credentials"},
    },
)

logout_schema = extend_schema(
    summary="User Logout",
    description="Logs out the user by blacklisting the refresh token.",
    request=serializers.Serializer,
    responses={205: None, 400: {"description": "Invalid token"}},
)

# Profile Schemas

edit_profile_schema = extend_schema(
    summary="View or Edit Profile",
    description="Allows a user to view or update their profile details.",
    request=UserProfileSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "email": {"type": "string"},
                "role": {"type": "string"},
            },
        },
        400: {"description": "Invalid data"},
    },
)

list_users_based_on_role_schema = extend_schema(
    summary="List Users by Role",
    description="Retrieves a list of users based on their role.",
    parameters=[
        OpenApiParameter(name="role", description="Filter users by role (agent or user)", required=False, type=str),
    ],
    responses={200: serializers.Serializer, 400: {"description": "Invalid role"}},
)

# Password Reset Schemas

send_password_request_token_schema = extend_schema(
    summary="Request Password Reset",
    description="Sends a password reset token to the user's email.",
    request=SendPasswordRequestTokenSerializer,
    responses={200: {"message": "Password reset token sent"}, 400: {"description": "Invalid email"}},
)

password_reset_confirm_schema = extend_schema(
    summary="Reset Password",
    description="Resets a user's password using the provided token.",
    request=PasswordResetConfirmViewSerializer,
    responses={200: {"details": "Password has been reset successfully"}, 400: {"description": "Invalid token"}},
)

# Property Schemas

list_my_properties_schema = extend_schema(
    summary="List My Properties",
    description="Retrieves all properties owned by the authenticated agent.",
    request=PropertySerializer,
    responses={200: serializers.Serializer},
)

create_property_schema = extend_schema(
    summary="Create Property",
    description="Allows an agent to create a new property.",
    request=PropertySerializer,
    responses={201: serializers.Serializer, 400: {"description": "Invalid data"}},
)

retrieve_property_schema = extend_schema(
    summary="Retrieve Property",
    description="Retrieves details of a property owned by the authenticated agent.",
    responses={200: serializers.Serializer, 404: {"description": "Property not found"}},
)

update_property_schema = extend_schema(
    summary="Update Property",
    description="Allows an agent to update their property details.",
    request=PropertySerializer,
    responses={200: serializers.Serializer, 400: {"description": "Invalid data"}},
)

delete_property_schema = extend_schema(
    summary="Delete Property",
    request=PropertySerializer,
    description="Deletes a property owned by the authenticated agent.",
    responses={204: None, 404: {"description": "Property not found"}},
)

list_public_properties_schema = extend_schema(
    summary="List All Properties",
    request=PropertySerializer,
    description="Retrieves a list of all properties available to the public.",
    responses={200: serializers.Serializer},
)

retrieve_public_property_schema = extend_schema(
    request=PropertySerializer,
    summary="Retrieve Public Property",
    description="Retrieves details of a single property available to the public.",
    responses={200: serializers.Serializer, 404: {"description": "Property not found"}},
)
