"""Rides Permissions"""


# Django REST Framework
from rest_framework.permissions import BasePermission


class IsRideOwner(BasePermission):
    """Verify requesting user is the rides create."""

    def has_object_permission(self, request, view, obj):
        """Verify requesting user is the ride creator"""
        return request.user == obj.offered_by


class IsNotRideOwner(BasePermission):
    """Verify requesting user is different than the one who created the ride."""

    def has_object_permission(self, request, view, obj):
        """Verify requesting user is the ride creator"""
        return request.user != obj.offered_by
