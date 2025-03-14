from django.contrib.auth.models import BaseUserManager

class UserProfileManager(BaseUserManager):
    def create_user(self, email, name, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")
        if not name:
            raise ValueError("The Name field is required")

        email = self.normalize_email(email)
        if not username:  
            username = email.split('@')[0]  # Auto-generate a username if not provided

        extra_fields["username"] = username  # Ensure username is set
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, name, password, username, **extra_fields)
