"""Circles Invitations"""

# Django
from django.db import models

# Utilities
from cride.utils.models import CRideModel

# Managers
from cride.circles.managers import InvitationManager


class Invitation(CRideModel):
    """Circle Invitation.

    A circle invitatoin is a randdom text that acts as
     a unique code that grants access to a specific circle.
     These codes are generated by users that are already
     members of the circle and have a `remaining_invitations`
     value greater than 0
    """

    code = models.CharField(max_length=50, unique=50)

    issued_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        help_text='Circle member that is providing the invitation',
        related_name='issued_by'
    )
    used_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        help_text='User that used the code to enter the circle'
    )
    circle = models.ForeignKey('circles.Circle', on_delete=models.CASCADE)

    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(blank=True, null=True)

    # Manager
    objects = InvitationManager()

    def __str__(self):
        return '#{}: {}'.format(self.circle.slug_name, self.code)
