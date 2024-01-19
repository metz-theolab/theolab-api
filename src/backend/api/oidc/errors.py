"""This module defines different encountered exceptions due to bad credentials.
"""



class AuthorizationError(Exception):
    """Exceptions that will be raised when the user is unauthorized.
    """
    code = 403
    details = "Unauthorized"


class InvalidCredentialsError(AuthorizationError):
    """Exceptions that will be raised when credentials are invalid.
    """
    code = 403
    details = "Invalid credentials"


class NotAllowedError(AuthorizationError):
    """Exceptions that will be raised when a user performs an exception that is
    not allowed.
    """
    code = 403
    details = "Not allowed"
