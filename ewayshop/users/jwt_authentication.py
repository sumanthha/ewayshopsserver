
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions

from users.models import Profile as Users

import jwt
from rest_framework_jwt.settings import api_settings

from users.authentication import Authentication


def get_username_field():
    try:

        username_field = Users.USERNAME_FIELD
    except:
        username_field = 'email'

    return username_field

def jwt_decode_handler(token):
    options = {
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
    }
    unverified_payload = jwt.decode(token, None, False)
    secret_key = jwt_get_secret_key(unverified_payload)
    return jwt.decode(
        token,
        api_settings.JWT_PUBLIC_KEY or secret_key,
        api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=None,
        issuer=None,
        algorithms=[api_settings.JWT_ALGORITHM]
    )

def jwt_get_secret_key(payload=None):

    if api_settings.JWT_GET_USER_SECRET_KEY:
        user_model = get_user_model()
        user = user_model.objects.get(pk=payload.get('user_id'))
        key = str(api_settings.JWT_GET_USER_SECRET_KEY(user))
        return key
    return api_settings.JWT_SECRET_KEY


class JwtAuthentication(Authentication):


    def authenticate(self, request):

        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            jwt_value = jwt_value.decode("utf-8")
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)
        request.user = user
        return (user, jwt_value)


