"""This module defines models to decode UserClaims.
"""


from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
from .errors import NotAllowedError


class GrantType(str, Enum):
    """Enumeration for the possible grant types.
    """
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    IMPLICIT = "implicit"
    PASSWORD = "password"


class UserClaims(BaseModel, extra="allow"):
    """UserClaims decoded from a token.
    Inherits from pydantic BaseModel.
    """
    preferred_username: Optional[str] = None
    resource_access: Dict[str, Dict[str, List[str]]]

    def has_roles(self,
                  expected_roles: List[str],
                  client_id: str,
                  require_all: bool = False) -> bool:
        """Return True if user has expected roles for the realm, else False.

        By default, user must have all roles, but when "require_all" is set to False,
        only one role needs to be present.

        Args:
            roles (List[str]): The expected roles. If empty, always return True.
            require_all (bool): Whether or not all roles are required.

        Returns:
            bool: Whether or not any (or all) roles are in the user.
        """
        # If no roles are specified, always return true
        if not expected_roles:
            return True
        # Generator to check if all the roles are there
        generator = (role in expected_roles for role in self.resource_access[client_id]["roles"])
        if require_all:
            return all(generator)
        return any(generator)

    def check_roles(self,
                    expected_roles: List[str],
                    client_id: str,
                    require_all: bool = False) -> None:
        """Check if all expected roles are present, else raise a not allowed error.

        Args:
            expected_roles (List[str]): The expected roles.
            require_all (bool, optional): Whether or not the user should have all the
                expected roles.
                Defaults to True.

        Raises:
            NotAllowedError: Raise a NotAllowedError if the user does not have a
                required permission.
        """
        if not self.has_roles(expected_roles=expected_roles,
                              require_all=require_all,
                              client_id=client_id):
            raise NotAllowedError("User does not have required permissions")
