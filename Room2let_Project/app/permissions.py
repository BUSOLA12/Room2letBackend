from rest_framework import permissions

class IsAgentOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow agents to create, update, or delete properties.
    """

    def has_permission(self, request, view):
        # Allow GET requests for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow modifications only if the user is authenticated and is an agent
        return request.user.is_authenticated and request.user.role == 'agent'

    def has_object_permission(self, request, view, obj):
        # Allow GET for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow the agent who owns the property to modify it
        return obj.user == request.user
