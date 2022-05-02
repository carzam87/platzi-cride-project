from django.contrib import admin

from cride.rides.models import Ride


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    """Ride admin."""

    list_display = (
        'offered_by',
        'offered_in',
        'available_seats',
        'departure_location',
        'departure_date',
        'arrival_location',
        'arrival_date',
        'rating',
        'is_active',
    )
