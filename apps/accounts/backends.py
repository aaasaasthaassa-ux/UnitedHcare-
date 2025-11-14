from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """Authenticate using either username or email address.

    This backend is case-insensitive for both username and email lookups.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get('identifier') or kwargs.get('email')

        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.filter(
                Q(username__iexact=username) | Q(email__iexact=username)
            ).order_by('id').first()
        except Exception:
            return None

        if user and user.check_password(password):
            return user
        return None
