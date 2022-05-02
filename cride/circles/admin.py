"""Circles admin."""

# Django
from django.contrib import admin

# Model
from cride.circles.models import Circle, Membership, Invitation


@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    """Circle admin."""

    list_display = (
        'slug_name',
        'name',
        'is_public',
        'verified',
        'is_limited',
        'members_limit'
    )
    search_fields = ('slug_name', 'name')
    list_filter = (
        'is_public',
        'verified',
        'is_limited'
    )


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('circle', 'user', 'profile', 'used_invitations', 'remaining_invitations')
    ordering = ('circle',)
    list_filter = (
        'circle',
        'user'
    )


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ('code', 'issued_by', 'used_by', 'circle', 'used', 'used_at')
