"""Invitation tests."""

# Django
from django.test import TestCase

# Django REST Framework
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

# Model
from cride.circles.models import Invitation, Circle, Membership
from cride.users.models import User, Profile


class InvitationsManagerTestCase(TestCase):
    """Invitations manager tests."""

    def setUp(self):
        """Create user and circle."""

        self.user = User.objects.create_user(
            first_name='Pablo',
            last_name='Trinidad',
            email='pablotrinidad@ciencias.unam.mx',
            username='pablotrinidad',
            password='admin123'
        )
        self.circle = Circle.objects.create(
            name='Facultad de Ciencias',
            slug_name='ciencias',
            about='Grupo de la facultadad de ciencias de la UNAM',
            verified=True
        )

    def test_code_generation(self):
        """Random code should be generated automatically."""
        invitation = Invitation.objects.create(
            circle=self.circle,
            issued_by=self.user,
        )
        self.assertIsNotNone(invitation.code)

    def test_code_usage(self):
        """If a code is given, there's no need to create a new one."""
        code = 'holamundo'
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )
        self.assertEqual(invitation.code, code)

    def test_code_generation_if_duplicates(self):
        """ If given code is not unique, a new one should be generated."""
        code = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle
        ).code

        # create another invitation with the past code
        invitation = Invitation.objects.create(
            issued_by=self.user,
            circle=self.circle,
            code=code
        )

        self.assertNotEqual(invitation.code, code)


class MemberInvitationsAPITestCase(APITestCase):
    """Member invitations API test case."""

    def setUp(self):
        """Create user and circle."""

        self.user = User.objects.create_user(
            first_name='Pablo',
            last_name='Trinidad',
            email='pablotrinidad@ciencias.unam.mx',
            username='pablotrinidad',
            password='admin123'
        )

        self.profile = Profile.objects.create(user=self.user)

        self.circle = Circle.objects.create(
            name='Facultad de Ciencias',
            slug_name='ciencias',
            about='Grupo de la facultadad de ciencias de la UNAM',
            verified=True
        )

        self.membership = Membership.objects.create(
            user=self.user,
            profile=self.profile,
            circle=self.circle,
            remaining_invitations=10
        )

        # Auth
        self.token = Token.objects.create(user=self.user).key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # URL
        self.url = '/circles/{}/members/{}/invitations/'.format(
            self.circle.slug_name,
            self.user.username
        )

    def test_response_success(self):
        """ Verify request succeded."""

        request = self.client.get(self.url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_invitation_creation(self):
        """Verify invitation  """
        """Invitations in DB must be 0"""
        self.assertEqual(Invitation.objects.count(), 0)

        # Call member invitations URL
        request = self.client.get(self.url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        # Verify that invitation were created
        invitations = Invitation.objects.filter(issued_by=self.user)
        self.assertEqual(invitations.count(), self.membership.remaining_invitations)
        for invitation in invitations:
            self.assertIn(invitation.code, request.data['invitations'])
