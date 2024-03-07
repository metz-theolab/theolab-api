"""This module provides a class to perform token decoding and checks
user claims.
"""

import json
import time
from typing import Any, Dict, List, Optional
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

import fastapi
import httpx
import jwt
import jwt.algorithms
from loguru import logger
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import (
    OAuthFlowAuthorizationCode,
    OAuthFlowClientCredentials,
    OAuthFlowImplicit,
    OAuthFlowPassword,
)
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.status import HTTP_401_UNAUTHORIZED

from .errors import AuthorizationError, InvalidCredentialsError
from .models import UserClaims, GrantType


class Singleton(type):
    """The singleton class allows to create a class which will mutate
    every instance of this class when changed.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class OIDCAuthClient:
    """The OIDCAuthClient provides authentification mechanisms through
    an OIDC provider.
    """

    def __init__(
        self,
        issuer_url: str,
        realm: str,
        client_id: str,
        algorithms: Optional[List[str]] = ["RS256"],
        retry: bool = False,
        enabled: bool = True,
        max_attempts: int = 500
    ) -> None:
        """Create a new OIDCAuthClient.

        Args:
            issuer_url (str): The URL that will issue authentification.
            realm (str): The name of the realm to use for logging.
            algorithms (Optional[List[str]], optional): The algorithms used for decoding.
                Defaults to "RS256".
            retry (bool, optional): Whether or not to retry connection to keycloak when there is
                a failure. Defaults to False.
            max_attempts (int, optional): Maximum number of attempts to try connecting the OIDC
                server. Defaults to 500.
        """
        self.issuer_url = issuer_url
        self.realm = realm
        self.well_known_uri = \
            f"{issuer_url}/realms/{self.realm}/.well-known/openid-configuration"
        self.algorithms = algorithms
        self.token_alg = "RS256"
        self.client_id = client_id
        self.enabled = enabled
        # Create http client to make corresponding requests
        # Do not verify SSL certificates because ours are self signed
        self.http_client = httpx.Client(verify=False)
        if self.enabled:
            # If retry is enabled, retry until connected
            # Wait time is 5 seconds before retrying connexion to the OIDC server

            if retry:
                connected = False
                attempts = 1
                while not connected and attempts < max_attempts:
                    try:
                        self.well_known = self.get_server_metadata()
                        self.public_key = self.get_public_key()
                        connected = True
                        logger.info("Successfully retrieved OIDC metadata from "
                                    f"{self.well_known_uri} after {attempts} attempt")
                    except ValueError:
                        time.sleep(5)
                        logger.info("Failed to retrieve OIDC metadata from "
                                    f"{self.well_known_uri} after {attempts} attempt")
                        attempts += 1
                # Last attempt, if this fails the code breaks
                if not connected:
                    self.well_known = self.get_server_metadata()
                    self.public_key = self.get_public_key()
            # Else fail on first attempt
            else:
                self.well_known = self.get_server_metadata()
                self.public_key = self.get_public_key()
                logger.info("Successfully retrieved OIDC metadata from "
                            f"{self.well_known_uri}")

    def get_server_metadata(self) -> Dict[str, Any]:
        """Get the metadata from the well know uri, and return the well_known
        dictionary.

        Returns:
            Dict[str, Any]: The information from the server.
        """
        try:
            resp = self.http_client.get(self.well_known_uri)
        except httpx.HTTPError as err:
            raise ValueError("Failed to fetch OIDC well known config") from err
        if resp.status_code != 200:
            raise ValueError(
                f"Could not fetch OIDC server metadata with status code {resp.status_code}")
        return resp.json()

    def get_public_key(self) -> RSAPublicKey:
        """Load the public key that will be used to decode the token.

        Returns:
            str: The public key
        """
        resp = self.http_client.get(self.well_known["jwks_uri"])
        jwks = resp.json()
        # Check if the decoding algorithm is supported.
        for jwk in jwks["keys"]:
            if jwk["alg"].upper() in self.algorithms:
                # When found, store it for decoding
                self.token_alg = jwk["alg"].upper()
                break
        else:
            raise Exception(
                "OpenID Connect issuer does not support any of"
                f"the accepted algorithms: {self.algorithms}")
        # Load the public key after decoding
        pubkey = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        if isinstance(pubkey, RSAPublicKey):
            return pubkey
        raise ValueError("A public key was expected, but received a private key")

    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode a token access.

        Args:
            token (str): The token to be decoded.

        Returns:
            Dict[str, Any]: The decoded token.
        """
        return dict(
            jwt.decode(
                token,
                key=self.public_key,
                algorithms=[self.token_alg],
                options={"verify_aud": False}
            )
        )

    def get_user_claim(self, token: str) -> UserClaims:
        """Validate JWT token signature and parse it into a UserClaims model

        Args:
            token (str): The token to be decoded.

        Raises:
            InvalidCredentialsError: An invalid credential error, either in the case
                of an error when decoding or in the case of an expired signature.

        Returns:
            UserClaims: _description_
        """
        try:
            return UserClaims(**self.decode_token(token))
        except jwt.DecodeError as exc:
            raise InvalidCredentialsError("Error decoding the token.") from exc
        except jwt.ExpiredSignatureError as exc:
            raise InvalidCredentialsError("Token has expired.") from exc


class APIOIDCAuth(SecurityBase, metaclass=Singleton):
    """Create an OIDC authentificator, that inherits from fastapi SecurityBase, to check
    for proper authentification.
    """

    scheme_name = "openIdConnect"

    def __init__(self):
        """Initialize an object of class APIOIDCAuth, with the proper authentification method,
        as found using the authorization schemes.
        It inherits as a metaclass from Singleton, which means a single APIOIDCAuth object is
        available over the whole application.
        """
        self.grant_types = [GrantType.IMPLICIT]
        flows = OAuthFlowsModel()
        self.model = OAuth2Model(flows=flows)

    async def __call__(self, request: fastapi.Request) -> UserClaims:
        """Given a fastapi Request, call the oidc auth provider on this request.

        Args:
            request (fastapi.Request): The request that will require authentification.

        Returns:
            UserClaims: The parsed claims of the user.
        """
        # Get the oidc provider from the app
        oidc = request.app.state.oidc
        # Bypass authentication when disabled and return default model
        if not oidc.enabled:
            return UserClaims(**{
                "given_name": "anonymous",
                "resource_access": {
                    request.app.state.settings.oidc.client_id: {
                        "roles": ["read"]
                    }
                }
            })
        # Get the authorization from the request
        authorization = request.headers.get("Authorization")
        scheme, token = get_authorization_scheme_param(authorization)
        try:
            # If there is no authorization data and not in the case of a bearer
            if not authorization or scheme.lower() != "bearer":
                # Raise an invalid credentials
                raise InvalidCredentialsError("No credentials found")
            # Else get the user claim
            return oidc.get_user_claim(token)
        except AuthorizationError as exc:
            raise fastapi.HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc

    @classmethod
    def update_model(cls, client: OIDCAuthClient) -> None:
        """Update the OAuth model to take into account the data in the configuration file.
        Because class is a singleton, every instance of the class will be mutated accordingly.
        """
        auth = cls()
        grant_types = set(client.well_known["grant_types_supported"])
        grant_types = grant_types.intersection(auth.grant_types)

        flows = OAuthFlowsModel()

        authz_url = client.well_known["authorization_endpoint"]
        token_url = client.well_known["token_endpoint"]

        if GrantType.AUTHORIZATION_CODE in grant_types:
            flows.authorizationCode = OAuthFlowAuthorizationCode(
                authorizationUrl=authz_url,
                tokenUrl=token_url,
            )

        if GrantType.CLIENT_CREDENTIALS in grant_types:
            flows.clientCredentials = OAuthFlowClientCredentials(tokenUrl=token_url)

        if GrantType.PASSWORD in grant_types:
            flows.password = OAuthFlowPassword(tokenUrl=token_url)

        if GrantType.IMPLICIT in grant_types:
            flows.implicit = OAuthFlowImplicit(
                authorizationUrl=authz_url,
                scopes={"client_id": client.client_id}
            )

        auth.model.flows = flows
        # Since the class generates singleton, it should modify the value everywhere it's used
        auth.model.openIdConnectUrl = client.issuer_url
