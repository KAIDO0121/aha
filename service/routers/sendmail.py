import os
import pathlib
from urllib.request import Request


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


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(os.getenv('MAIL_SECRET'))
    return serializer.dumps(email, salt=os.getenv('SECURITY_PASSWORD_SALT'))


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(os.getenv('MAIL_SECRET'))
    try:
        email = serializer.loads(
            token,
            salt=os.getenv('SECURITY_PASSWORD_SALT'),
            max_age=expiration
        )
    except:
        return False
    return email


async def send_email_async(subject: str, email_to: str, body: dict):
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype='html',
    )

    fm = FastMail(conf)
    await fm.send_message(message, template_name='email.html')


def send_email_background(background_tasks: BackgroundTasks, subject: str, email_to: str, body: dict):
    print(subject, email_to, body)
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=body,
        subtype='html',
    )
    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message, template_name='email.html')


@router.post('/api/send-email/backgroundtasks')
def send_email_backgroundtasks(background_tasks: BackgroundTasks):
    send_email_background(background_tasks, 'Hello World',
                          'kaido0121@gmail.com', {'title': 'Hello World', 'name': 'John Doe'})
    return 'Success'


@router.post('/api/send-email/asynchronous')
async def send_email_asynchronous():
    await send_email_async('Hello World', 'kaido0121@gmail.com',
                           {'title': 'Hello World', 'name': 'John Doe'})
    return 'Success'


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
        print(e, 'EEEEEEEEE')
        return False


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
