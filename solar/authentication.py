from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class MobileNumberBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        mobile_number = kwargs.get('mobile_number', username)
        try:
            user = User.objects.get(mobile_number=mobile_number)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None
