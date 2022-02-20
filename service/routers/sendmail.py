import os
import pathlib


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import BackgroundTasks, Security, APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from dotenv import load_dotenv

from itsdangerous import URLSafeTimedSerializer
from utils.auth_bearer import Auth

security = HTTPBearer()
auth_handler = Auth()

router = APIRouter()
load_dotenv()
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=f'{pathlib.Path(__file__).parent.resolve()}/templates'
)


async def send_with_template(user: dict, body: dict):
    message = MessageSchema(
        subject="Verification mail",
        recipients=[user.get("email")],
        template_body=body
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message, template_name="email.html")
        return 'Success'
    except Exception as e:
        raise e


@router.get('/api/resend_verification_email')
async def resend_verification_email(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = auth_handler.decode_token(token)
    url = os.getenv('SERVER_URL')
    confirm_url = f'{url}/api/confirm/{token}'

    body = {
        "confirm_url": confirm_url,
        "name": payload['name']
    }

    message = MessageSchema(
        subject="Verification mail",
        recipients=[payload['email']],
        template_body=body
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message, template_name="email.html")
        return 'Success'
    except:
        return False
