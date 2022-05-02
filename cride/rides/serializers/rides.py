""" Rides Serializer"""
# Django
from django.db.models import Avg


# Django REST Framework
from rest_framework import serializers

# Models
from cride.rides.models import Ride, Rating
from cride.circles.models import Membership, Circle, memberships
from cride.users.models import User

# Utilities
from datetime import timedelta
from django.utils import timezone

# Serializers
from cride.users.serializers import UserModelSerializer


class RideModelSerializer(serializers.ModelSerializer):
    """Ride model serializer"""

    offered_by = UserModelSerializer(read_only=True)
    offered_in = serializers.StringRelatedField()

    passengers = UserModelSerializer(read_only=True, many=True)

    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = (
            'offered_in',
            'offered_by',
            'rating'
        )

    def update(self, instance, data):
        """Allow updates only before departure date."""
        now = timezone.now()
        if instance.departure_date <= now:
            raise serializers.ValidationError('Ongoing rides cannot be modified')
        return super(RideModelSerializer, self).update(instance, data)


class CreateRideSerializer(serializers.ModelSerializer):
    """Create ride Serializer."""

    offered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    available_seats = serializers.IntegerField(min_value=1, max_value=15)

    class Meta:
        """Meta Class"""

        model = Ride
        exclude = ('offered_in', 'passengers', 'rating', 'is_active')

    def validate_departure_date(self, data):
        """Verify date is not in the past."""

        min_date = timezone.now() + timedelta(minutes=20)
        if data < min_date:
            raise serializers.ValidationError(
                'Departure time must be at least pass the next 20 minutes window.'
            )
        return data

    def validate(self, data):
        """Validate.
        Verify that the person who offers the ride is member
        and also the same user making the request.
        """

        if self.context['request'].user != data['offered_by']:
            raise serializers.ValidationError('Rides offered on behalf of others are no allowed')

        user = data['offered_by']
        circle = self.context['circle']
        try:
            membership = Membership.objects.get(user=user, circle=circle, is_active=True)
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle')

        if data['arrival_date'] <= data['departure_date']:
            raise serializers.ValidationError('Departure date must happen before arrival date')

        self.context['membership'] = membership
        return data

    def create(self, data):
        """Create ride and update stats"""

        circle = self.context['circle']
        ride = Ride.objects.create(**data, offered_in=circle)

        # Circle
        circle.rides_offered += 1
        circle.save()

        # Membership
        membership = self.context['membership']
        membership.rides_offered += 1
        membership.save()

        # Profile
        profile = data['offered_by'].profile
        profile.rides_offered += 1

        return ride


class JoinRideSerializer(serializers.ModelSerializer):
    """Join ride serializer"""

    passenger = serializers.IntegerField()

    class Meta:
        """Meta class"""
        model = Ride
        fields = ('passenger',)

    def validate_passenger(self, data):
        """Verify passanger exists and is a circle member."""
        try:
            user = User.objects.get(pk=data)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid Passenger')

        circle = self.context['circle']
        if not Membership.objects.filter(user=user, circle=circle, is_active=True).exists():
            raise serializers.ValidationError('User is not an active member of the circle')

        try:
            membership = Membership.objects.get(user=user, circle=circle, is_active=True)
        except Membership.DoesNotExist:
            raise serializers.ValidationError('User is not an active member of the circle')

        self.context['user'] = user
        self.context['member'] = membership
        return data

    def validate(self, data):
        """Verify rides allow new passengers"""
        offset = timezone.now() - timedelta(minutes=10)
        ride = self.context['ride']
        if ride.departure_date > offset:
            serializers.ValidationError("You can't join this ride now.")

        if ride.available_seats < 1:
            serializers.ValidationError('Ride is already full.')

        if Ride.objects.filter(passengers__pk=data['passenger']).exists():
            raise serializers.ValidationError('Passanger is already in this trip.')

        return data

    def update(self, instance, data):
        """Add passanger"""
        ride = self.context['ride']
        user = self.context['user']

        ride.passengers.add(user)

        # Profile
        profile = user.profile
        profile.rides_taken += 1
        profile.save()

        # Membership
        member = self.context['member']
        member.rides_taken += 1
        member.save()

        # Circle
        circle = self.context['circle']
        circle.rides_taken += 1
        circle.save()

        return ride


class EndRideSerializer(serializers.ModelSerializer):
    """End ride serializer."""

    current_time = serializers.DateTimeField()

    class Meta:
        model = Ride
        fields = ('current_time', 'is_active')

    def validate_current_time(self, data):
        """Verify ride have indeed started"""

        ride = self.context['view'].get_object()
        if data <= ride.departure_date:
            raise serializers.ValidationError('Ride has not started yet.')
        return data


class CreateRideRatingSerializer(serializers.ModelSerializer):
    """Create ride rating serializer."""

    class Meta:
        """Meta class"""
        model = Rating
        fields = ('rating', 'comments')

    def validate(self, data):
        """Verify rating hasn't yet been emitted before"""

        ride = self.context['ride']
        user = self.context['request'].user

        if not ride.passengers.filter(user_id=user.pk).exists():
            raise serializers.ValidationError('User is not a passenger.')

        q = Rating.objects.filter(
                circle=self.context['circle'],
                ride=ride,
                rating_user=user
            )
        if q.exists():
            raise serializers.ValidationError('Rating have already been emitted!')
        return data

    def create(self, data):
        """ Create Rating. """

        offered_by = self.context['ride'].offered_by

        Rating.objects.create(
            circle=self.context['circle'],
            ride=self.context['ride'],
            ratin_user=self.context['request'].user,
            rated_user=offered_by,
            **data
        )

        ride_avg = round(
            Rating.objects.filter(
                circle=self.context['circle'],
                ride=self.context['ride']
            ).aggregate(Avg('rating'))['rating__avg'],
            1
        )

        self.context['ride'].rating = ride_avg
        self.context['ride'].save()

        user_avg = round(
            Rating.objects.filter(
                rated_user=offered_by
            ).aggregate(Avg('rating'))['rating__avg'],
            1
        )

        offered_by.profile.reputation = user_avg
        offered_by.profile.save()

        return self.context['ride']
