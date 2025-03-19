from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import serializers
from .serializers import PropertySerializer, SignupSerializer, LoginSerializer, UserProfileSerializer

# ==============================
# 📌 Signup Schema
# ==============================
signup_schema = extend_schema(
    request=SignupSerializer,
    responses={
        201: {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "token": "access_token_here",
                        "refresh": "refresh_token_here",
                        "user": {
                            "id": 1,
                            "username": "justin_dev",
                            "email": "justin@example.com",
                            "role": "agent"
                        }
                    }
                }
            },
        },
        400: {"description": "Invalid input data"},
    },
    summary="Register a new user",
    description="Allows users to create an account with a role of 'user' or 'agent'. The response includes an authentication token.",
)

# ==============================
# 📌 Login Schema
# ==============================
login_schema = extend_schema(
    request=LoginSerializer,
    responses={
        200: {
            "description": "User successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "token": "access_token_here",
                        "refresh": "refresh_token_here",
                        "user": {
                            "id": 1,
                            "username": "justin_dev",
                            "email": "justin@example.com",
                            "role": "agent"
                        }
                    }
                }
            },
        },
        400: {"description": "Invalid credentials"},
    },
    summary="User Login",
    description="Authenticates users and returns JWT tokens for session management.",
)

# ==============================
# 📌 Edit Profile Schema
# ==============================
edit_profile_schema = extend_schema(
    request=UserProfileSerializer,
    responses={
        200: UserProfileSerializer,
        400: {"description": "Invalid input data"},
    },
    summary="Get/Edit User Profile",
    description="Allows authenticated users to retrieve and update their profile details.",
)

# ==============================
# 📌 Add Property Schema
# ==============================
add_property_schema = extend_schema(
    request=PropertySerializer,
    responses={
        201: PropertySerializer,
        400: {"description": "Invalid input data"},
    },
    summary="Create a New Property",
    description="Allows only agents to add properties to the system.",
)

# ==============================
# 📌 Get User Properties (Agent-Only)
# ==============================
get_my_properties_schema = extend_schema(
    responses={
        200: PropertySerializer(many=True),
        403: {"description": "Forbidden. Only agents can retrieve their properties."},
    },
    summary="Retrieve Agent's Own Properties",
    description="Agents can retrieve only the properties they have listed.",
)

# ==============================
# 📌 Get All Properties (Public)
# ==============================
get_all_properties_schema = extend_schema(
    responses={200: PropertySerializer(many=True)},
    summary="Retrieve All Properties",
    description="Anyone can retrieve the list of all properties available on the platform.",
)

# ==============================
# 📌 Update Property Schema
# ==============================
update_property_schema = extend_schema(
    request=PropertySerializer,
    responses={
        200: PropertySerializer,
        403: {"description": "Forbidden. Only the property owner (agent) can update."},
        404: {"description": "Property not found."},
    },
    summary="Update a Property",
    description="Allows agents to update their listed properties.",
)

# ==============================
# 📌 Delete Property Schema
# ==============================
delete_property_schema = extend_schema(
    responses={
        204: {"description": "Property successfully deleted."},
        403: {"description": "Forbidden. Only the property owner (agent) can delete."},
        404: {"description": "Property not found."},
    },
    summary="Delete a Property",
    description="Allows agents to delete properties they have listed.",
)
