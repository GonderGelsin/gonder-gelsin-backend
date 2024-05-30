import base64
import os
from email.mime.text import MIMEText

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from rest_framework import status
from rest_framework.response import Response


class CustomErrorResponse(Response):

    def __init__(self, status_ch='NOK', status_code=None, msj='Operation failed.', error_code=666):
        data = {
            'status': status_ch,
            'message': msj,
            'data': {"isAvailable": False, 'error_code': error_code},
            "options": {},
        }
        if status_code is None or not 400 <= status_code <= 599:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        super().__init__(data=data, status=status_code)


class CustomSuccessResponse(Response):

    def __init__(self, status_msj='OK', status_code=None, msj='Operation Successfully Done.', input_data=None, input_options=None):
        if input_data is None:
            input_data = {}
        if input_options is None:
            input_options = {}
        data = {
            'status': status_msj,
            'message': msj,
            'data': input_data,

            "options": input_options,
        }
        if status_code is None or not 200 <= status_code <= 399:
            status_code = status.HTTP_202_ACCEPTED

        super().__init__(data=data, status=status_code)


SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    creds = Credentials(
        None,
        token_uri='https://oauth2.googleapis.com/token',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )
    if not creds.valid:
        creds.refresh(Request())
    service = build('gmail', 'v1', credentials=creds)
    return service


def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


def send_email(subject, body, to):
    service = get_gmail_service()
    message = create_message('me', to, subject, body)
    try:
        sent_message = service.users().messages().send(
            userId='me', body=message).execute()
        print(f'Message Id: {sent_message["id"]}')
    except Exception as error:
        print(f'An error occurred: {error}')
