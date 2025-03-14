from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

UserProfile = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ['name', 'email', 'password', 'role']  # Ensure 'name' is included
        extra_kwargs = {'username': {'required': False}, 'role': {'required': False}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = UserProfile.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)  # Authenticate using email
            if not user:
                raise serializers.ValidationError("Invalid email or password")

            data["user"] = user
        else:
            raise serializers.ValidationError("Both email and password are required")

        return data

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['name', 'username', 'address', 'email', 'profile_picture', 'about', 'phone_number']  # Lists everything in UserProfile
        read_only_fields = ['property_count', 'created_at', 'updated_at']
