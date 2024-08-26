import six
from django.contrib.auth import authenticate
from user.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime
import pytz


def user_authenticate(self, username=None, password=None):
    kwargs = {"email": username}
    try:
        user = authenticate(username=username, password=password)
        if user is not None:
            return user
        else:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
            else:
                return None
    except User.DoesNotExist:
        return None


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk)
            + six.text_type(timestamp)
            + six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()


def time_ago_from_datetime(past_datetime):
    current_datetime = datetime.now(pytz.timezone("UTC"))
    time_difference = current_datetime - past_datetime

    if time_difference.days > 365:
        years_ago = time_difference.days // 365
        return f"{years_ago} year{'s' if years_ago > 1 else ''} ago"
    elif time_difference.days > 30:
        months_ago = time_difference.days // 30
        return f"{months_ago} month{'s' if months_ago > 1 else ''} ago"
    elif time_difference.days > 0:
        return (
            f"{time_difference.days} day{'s' if time_difference.days > 1 else ''} ago"
        )
    else:
        seconds_ago = time_difference.seconds
        if seconds_ago < 60:
            return f"{seconds_ago} second{'s' if seconds_ago > 1 else ''} ago"
        elif seconds_ago < 3600:
            minutes_ago = seconds_ago // 60
            return f"{minutes_ago} minute{'s' if minutes_ago > 1 else ''} ago"
        else:
            hours_ago = seconds_ago // 3600
            return f"{hours_ago} hour{'s' if hours_ago > 1 else ''} ago"
