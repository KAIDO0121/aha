
from pprint import pprint
from passlib.context import CryptContext
import jwt
import os
from datetime import datetime, timedelta
from service.utils.utils import CREDENTIALS_EXCEPTION, INVALID_CREDENTIAL_SCHEME, INVALID_OR_EXPIRED_TOKEN, cast_to_number

API_SECRET_KEY = os.environ.get('API_SECRET_KEY') or None
if API_SECRET_KEY is None:
    raise BaseException('Missing API_SECRET_KEY env var.')
API_ALGORITHM = os.environ.get('API_ALGORITHM') or 'HS256'
API_ACCESS_TOKEN_EXPIRE_MINUTES = cast_to_number(
    'API_ACCESS_TOKEN_EXPIRE_MINUTES') or 15
API_REFRESH_TOKEN_EXPIRE_HOURS = cast_to_number(
    'API_REFRESH_TOKEN_EXPIRE_HOURS') or 10


class Auth():
    hasher = CryptContext(schemes=['bcrypt'])
    secret = API_SECRET_KEY

    def encode_token(self, email, _id, name=None):

        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow(),
            'scope': 'access_token',
            'email': email,
            'id': _id
        }
        if name:
            payload['name'] = name

        return jwt.encode(
            payload,
            self.secret,
            algorithm=API_ALGORITHM
        )

    def decode_token(self, token, options=None):
        try:
            payload = jwt.decode(token, self.secret,
                                 algorithms=[API_ALGORITHM], options=options)
            if (payload['scope'] == 'access_token'):
                return payload
            raise INVALID_CREDENTIAL_SCHEME
        except jwt.ExpiredSignatureError:
            raise INVALID_OR_EXPIRED_TOKEN
        except jwt.InvalidTokenError:
            raise CREDENTIALS_EXCEPTION

    def encode_refresh_token(self, email, _id):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=0, hours=API_REFRESH_TOKEN_EXPIRE_HOURS),
            'iat': datetime.utcnow(),
            'scope': 'refresh_token',
            'email': email,
            'id': _id
        }

        return jwt.encode(
            payload,
            self.secret,
            algorithm=API_ALGORITHM
        )

    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.secret,
                                 algorithms=[API_ALGORITHM])
            if (payload['scope'] == 'refresh_token'):
                new_token = self.encode_token(
                    payload['email'], payload['id'], payload.get("name"))
                return new_token
            raise INVALID_CREDENTIAL_SCHEME
        except jwt.ExpiredSignatureError:
            raise INVALID_OR_EXPIRED_TOKEN
        except jwt.InvalidTokenError:
            raise CREDENTIALS_EXCEPTION
