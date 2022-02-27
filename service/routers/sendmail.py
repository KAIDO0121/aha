import os
import pathlib
from urllib.request import Request

from fastapi.security import HTTPBearer
from fastapi import APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from starlette.responses import JSONResponse

from dotenv import load_dotenv

from service.utils.auth_bearer import Auth

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


@router.route('/api/resend_verification_email')
async def resend_verification_email(request: Request):
    access_token = request.session.get('access_token')
    payload = auth_handler.decode_token(access_token)
    url = os.getenv('SERVER_URL')
    confirm_url = f'{url}/api/confirm/{access_token}'

    body = {
        "confirm_url": confirm_url,
        "email": payload['email']
    }

    message = MessageSchema(
        subject="Verification mail",
        recipients=[payload['email']],
        template_body=body
    )

    fm = FastMail(conf)
    try:
        await fm.send_message(message, template_name="email.html")
        return JSONResponse(status_code=200, content={'msg': 'The verification email has been sent'})
    except Exception as e:
        raise e
