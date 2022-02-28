import os
import pathlib
from urllib.request import Request

from fastapi import APIRouter
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from python_http_client.exceptions import HTTPError

import sendgrid
from sendgrid.helpers.mail import *

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
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.getenv('MAIL_FROM'))
    to_email = To(user.get("email"))
    subject = "Verification from AHA-app"
    content = Content(
        "text/plain", f"Hello {body['email']} Click <a href='{body['confirm_url']}'>here</a> to verify your account.")
    mail = Mail(from_email, to_email, subject, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())

        print(response.status_code)
        print(response.body)
        print(response.headers)
    except HTTPError as e:
        print(e.body)
        raise HTTPError


@router.route('/api/resend_verification_email')
async def resend_verification_email(request: Request):
    access_token = request.session.get('access_token')
    payload = auth_handler.decode_token(access_token)
    url = os.getenv('SERVER_URL')
    confirm_url = f'{url}/api/confirm/{access_token}'

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.getenv('MAIL_FROM'))
    to_email = To(payload['email'])
    subject = "Verification from AHA-app"
    content = Content(
        "text/plain", f"Hello {payload['email']} Click <a href='{confirm_url}'>here</a> to verify your account.")

    mail = Mail(from_email, to_email, subject, content)
    try:
        response = sg.client.mail.send.post(request_body=mail.get())

        print(response.status_code)
        print(response.body)
        print(response.headers)
    except HTTPError as e:
        print(e.body)
        raise HTTPError
