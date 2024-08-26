from rest_framework.views import exception_handler

def exception_handler_rest_api(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'status': False,
            'errors': response.data
        }

    return response