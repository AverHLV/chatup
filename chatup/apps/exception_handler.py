from rest_framework import exceptions, status, views


def custom_exception_handler(exc: Exception, context):
    """ Return 401 instead of 403 if authentication failed """

    response = views.exception_handler(exc, context)

    if isinstance(exc, (exceptions.AuthenticationFailed, exceptions.NotAuthenticated)):
        response.status_code = status.HTTP_401_UNAUTHORIZED

    return response
