
from passlib.context import CryptContext 
import jwt
import os
from datetime import datetime, timedelta
from utils.utils import CREDENTIALS_EXCEPTION, INVALID_CREDENTIAL_SCHEME, INVALID_OR_EXPIRED_TOKEN, cast_to_number

API_SECRET_KEY = os.environ.get('API_SECRET_KEY') or None
if API_SECRET_KEY is None:
    raise BaseException('Missing API_SECRET_KEY env var.')
API_ALGORITHM = os.environ.get('API_ALGORITHM') or 'HS256'
API_ACCESS_TOKEN_EXPIRE_MINUTES = cast_to_number('API_ACCESS_TOKEN_EXPIRE_MINUTES') or 15
API_REFRESH_TOKEN_EXPIRE_HOURS = cast_to_number('API_REFRESH_TOKEN_EXPIRE_HOURS') or 10


'''
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise INVALID_CREDENTIAL_SCHEME
            if not self.verify_jwt(credentials.credentials):
                raise INVALID_OR_EXPIRED_TOKEN
            return credentials.credentials
        else:
            raise CREDENTIALS_EXCEPTION

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = jwt.encode(jwtoken, API_SECRET_KEY, algorithm=API_ALGORITHM)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
'''

class Auth():
    hasher= CryptContext(schemes=['bcrypt'])
    secret = API_SECRET_KEY

    '''
    def encode_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)
    '''

    def encode_token(self, username):
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES),
            'iat' : datetime.utcnow(),
        'scope': 'access_token',
            'sub' : username
        }
        return jwt.encode(
            payload, 
            self.secret,
            algorithm= API_ALGORITHM
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=[API_ALGORITHM])
            if (payload['scope'] == 'access_token'):
                return payload['sub']   
            raise INVALID_CREDENTIAL_SCHEME
        except jwt.ExpiredSignatureError:
            raise INVALID_OR_EXPIRED_TOKEN
        except jwt.InvalidTokenError:
            raise CREDENTIALS_EXCEPTION

    def encode_refresh_token(self, username):
        payload = {
            'exp' : datetime.utcnow() + timedelta(days=0, hours=API_REFRESH_TOKEN_EXPIRE_HOURS),
            'iat' : datetime.utcnow(),
        'scope': 'refresh_token',
            'sub' : username
        }
        return jwt.encode(
            payload, 
            self.secret,
            algorithm= API_ALGORITHM
        )
    def refresh_token(self, refresh_token):
        try:
            payload = jwt.decode(refresh_token, self.secret, algorithms=[API_ALGORITHM])
            if (payload['scope'] == 'refresh_token'):
                username = payload['sub']
                new_token = self.encode_token(username)
                return new_token
            raise INVALID_CREDENTIAL_SCHEME
        except jwt.ExpiredSignatureError:
            raise INVALID_OR_EXPIRED_TOKEN
        except jwt.InvalidTokenError:
            raise CREDENTIALS_EXCEPTION