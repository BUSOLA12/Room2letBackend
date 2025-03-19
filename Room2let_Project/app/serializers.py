from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

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

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


class Send_password_request_Token_serializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")

        try:
            UserProfile.objects.get(email=email)
        except UserProfile.DoesNotExist:
            pass
        return data
    
class PasswordResetConfirmViewSerializer(serializers.Serializer):

    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    token = serializers.CharField()
    uidb64 = serializers.CharField()

    def validate(self, data):

        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password": "Password do not match"})
        
        if len(data.get('password')) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})
        
        try:
            user_id = urlsafe_base64_decode(data.get('uidb64')).decode()
            user = UserProfile.objects.get(id=user_id)

        
        except (TypeError, ValueError, OverflowError, UserProfile.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid user ID"})

        if not default_token_generator.check_token(user, data.get('token')):
            raise serializers.ValidationError({"token": "Invalid token"})
        
        self.user = user
        return data
    
    def save(self):
        self.user.set_password(self.validated_data.get('password'))
        self.user.save()
        return self.user
