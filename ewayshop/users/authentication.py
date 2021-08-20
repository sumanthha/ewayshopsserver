from rest_framework.authentication import get_authorization_header
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions

from users.models import Profile as Users



import jwt


class Authentication(JSONWebTokenAuthentication):


    def authenticate(self, request):

        token = self.get_token_value_from_header(request)
        if token is None:
            return None
        try:

            value = jwt.decode(token, None, None)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()


        else:

            from users.jwt_authentication import JwtAuthentication

            return JwtAuthentication.authenticate(self, request)


    def get_token_value_from_header(self, request):

        auth = get_authorization_header(request).split()
        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)
        if auth:
            return auth[1]
        return None


    def authenticate_credentials(self, payload):

        try:
            user = Users.objects.get(email=payload.get('email'), is_active=True)
        except Users.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid signature.'))

        return user



