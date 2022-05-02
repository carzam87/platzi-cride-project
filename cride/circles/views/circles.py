"""Circles View."""

# Django
from django.db.models import Count

# Django REST Framework
from rest_framework import mixins, viewsets
from rest_framework.response import Response

# Permissions
from rest_framework.permissions import IsAuthenticated
from cride.circles.permissions import IsCircleAdmin

# Filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

# Models
from cride.circles.models import Membership

# Serializers
from cride.circles.serializers import Circle, CircleModelSerializer


class CircleViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """Circle view set. """

    serializer_class = CircleModelSerializer
    lookup_field = 'slug_name'

    # Filters
    filter_backends = (SearchFilter, OrderingFilter, DjangoFilterBackend)
    search_fields = ('slug_name', 'name')
    ordering_fields = ('rides_offered', 'rides_taken', 'name', 'created', 'member_limit')
    ordering = ('-members_count', '-rides_offered', '-rides_taken')
    filter_fields = ('verified', 'is_limited')

    def get_permissions(self):
        """Assign permissions based on action"""
        permissions = [IsAuthenticated]
        if self.action in ['update', 'partial_update']:
            permissions.append(IsCircleAdmin)
        return [permission() for permission in permissions]

    def get_queryset(self):
        """Restrict list to public only"""
        queryset = Circle.objects.all()
        if self.action == 'list':
            return queryset.annotate(members_count=Count('members')).filter(is_public=True)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        print('entro al retrieve')
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Assign Circle Admin """
        circle = serializer.save()
        user = self.request.user
        profile = user.profile
        Membership.objects.create(
            user=user,
            profile=profile,
            circle=circle,
            is_admin=True,
            remaining_invitations=10
        )
