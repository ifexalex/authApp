from distutils.log import error
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        print()

        custom_error = []
        for key, value in response.data.items():
            error = {"field": key, "message": value}
            custom_error.append(error)

        custom_response = {
            "code": response.status_code,
            "status": "Failed",
            "message": response.data.get("detail", None)
            if 'detail' in response.data
            else "Missing fieids. Ensure you fill all required fields"
            if len(custom_error) > 1
            else custom_error[0]["message"][0],
            "errors": None
            if "detail" in [response.data, custom_error[0]["field"]]
            else custom_error,
        }

        response.data = custom_response

    return response
