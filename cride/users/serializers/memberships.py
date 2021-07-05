"""Membership serializers."""

# Django REST Framework
from rest_framework import serializers

# Models
from cride.circles.models import Membership


class MembershipModelSerializer(serializers.ModelSerializer):
    """Member model serializer."""

    class Meta:
        """Meta class"""
        model = Membership
        fields = (
            'user',
            'is_admin','is_active',
            'used_invitations',
            'remaining_invitations',
            'invited_by',
            'rides_taken',
            'rides_offered',
            'joined_at'
        )
        read_only_fields = (
            'user',
            'used_invitations',
            'rides_taken',
            'rides_offered'
        )
