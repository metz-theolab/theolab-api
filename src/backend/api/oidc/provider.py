"""The OIDC provider provides functions to attach the OIDC provider
to a FastAPI container.
"""


from typing import List

import fastapi
from starlette.status import HTTP_403_FORBIDDEN

from .errors import NotAllowedError
from .oidc_auth_client import APIOIDCAuth, OIDCAuthClient
from .models import UserClaims


user = APIOIDCAuth()


def check_user(expected_roles: List[str],
               client_id: str,
               require_all: bool = False,
               ):
    """Check if the user has the right roles.

    Args:
        roles (List[str]): List of allowed user roles.
        require_all (bool): Whether or not all roles are required for the user.

    Returns:
        The check_user function wrapped in a FastAPI Depends.
    """
    async def check_current_user_roles(
        user_: UserClaims = fastapi.Security(user),
    ) -> UserClaims:
        """Check if the user has the right roles. If not, raise a NotAllowed error.
        Else, return the user parsed as user claims.

        Args:
            user_ (UserClaims, optional): The claims for the user.
                Defaults to fastapi.Security applied to the current_user.

        Returns:
            UserClaims: The claimed user if the parsing was successful.
        """
        if not expected_roles:
            return user_
        try:
            user_.check_roles(expected_roles,
                              require_all=require_all,
                              client_id=client_id)
        except NotAllowedError as exc:
            raise fastapi.HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Not allowed",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        return user_
    return fastapi.Depends(check_current_user_roles)


def oidc_provider(app) -> None:
    """Define an oidc_provider to be attached to a FastAPI app.

    Args:
        app: The container to attach the logger to.
    """
    # If OIDC is enabled
    if app.state.settings.oidc.enabled:
        # Set client ID on swagger UI
        if app.swagger_ui_init_oauth is None:
            app.swagger_ui_init_oauth = {"clientId": app.state.settings.oidc.client_id}
        else:
            app.swagger_ui_init_oauth["clientId"] = app.state.settings.oidc.client_id
    # Create oidc client given the API settings
    oidc = OIDCAuthClient(
        issuer_url=app.state.settings.oidc.issuer_url,
        realm=app.state.settings.oidc.realm,
        client_id=app.state.settings.oidc.client_id,
        retry=app.state.settings.oidc.retry,
        max_attempts=app.state.settings.oidc.max_attempts,
        enabled=app.state.settings.oidc.enabled
    )
    # Update the Auth provider with this information
    if app.state.settings.oidc.enabled:
        APIOIDCAuth.update_model(oidc)
    # Attach oidc provider to app
    app.state.oidc = oidc
