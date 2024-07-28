# ../permissions.py
from rest_framework.permissions import BasePermission
from rest_framework import permissions

class IsWriterOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if request.user.is_authenticated:
                if request.user == obj.owner:
                    return True
                return False
            else:
                return False