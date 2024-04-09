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
