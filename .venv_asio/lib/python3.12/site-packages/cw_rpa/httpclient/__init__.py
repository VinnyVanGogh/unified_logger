"""
This module serves as the entry point for the API integration layer of the application.

It is responsible for setting up and managing the interactions with external APIs, including handling authentication, request headers, and the construction of requests. The module imports and utilizes several submodules and classes to streamline the process of sending HTTP requests and processing responses.

Imports:
    requests: Used for making HTTP requests.
    copy: Used for creating deep copies of objects, useful in request preparation.
    List, Dict: Typing imports for specifying type hints in function signatures.
    urlparse, urljoin: Functions from urllib.parse for URL manipulation.

Submodules:
    input: Module that handles input data and configurations.
    token: Module for managing authentication tokens.
    headers: Module for preparing request headers.
    models: Defines data models like HttpMethod, HeaderKeys, etc., used across the integration layer.
    constants: Contains constants like default values and key names used in API requests.

Classes and Enums Imported:
    HttpMethod: Enum representing HTTP methods (GET, POST, etc.).
    HeaderKeys: Enum for common HTTP header keys.
    ContentTypes: Enum for MIME types used in the Content-Type header.  
    InputVariables: Class or enum containing variables extracted from input configurations.

"""

import requests
import copy
from typing import List, Dict
from urllib.parse import urlparse, urljoin

from ..input import Input
from .token import Token

from .models import (
    HttpMethod,
    HeaderKeys,
    ContentTypes,
)

from .constants import (
    InputVariables,
    DEFAULT_GRANT_TYPE,
    INTEGRATION_NAME_KEY,
    CONNECTION_ID_KEY,
    RESOURCE_LIST_KEY,
    METHOD_KEY,
    URL_KEY,
    BODY_KEY,
    COMPANY_ID_KEY,
    DOMAIN_NAME_KEY,
    GRANT_TYPE_KEY,
    CLIENT_ID_KEY,
    CLIENT_SECRET_KEY,
    SCOPE_KEY,
    ACCESS_TOKEN_KEY,
    EXPIRES_IN_KEY,
    MICROSOFT_CSP,
    AZURE_O365,
)

__all__ = [
    "HttpClient",
    "HttpMethod",
    "Token",
    "HeaderKeys",
    "ContentTypes",
]


# endpoints
TOKEN_PATH = "/v1/token"
RPA_RESOLVE_PATH = "/api/platform/v1/rpa/resolve"


class HttpClient:
    """
    A class for making HTTP requests.

    This class abstracts the complexities involved in making HTTP requests and handling responses. It provides methods for sending GET, POST, PUT, DELETE, and other types of HTTP requests.
    
    HttpClient is a wrapper for the requests package. It handles token management and performs operations necessary for ConnectWise.

    This class is initialized with client details from an input file. It has properties for the integration name, connection ID, resource list, and a flag indicating whether the request is for a third party.

    The HttpClient class is responsible for fetching tokens for calling the ConnectWise API, generating integration payloads for ConnectWise integration calls, and performing validations such as required field validation and URL validation. It also provides the user with the ability to set their own client ID, client secret, and scopes for generating tokens.

    Attributes:
    - _integration_name: The name of the integration.
    - _connection_id: The connection ID.
    - _resource_list: The list of resources.
    - _is_third_party_call: A flag indicating whether the request is for a third party.
    - _token: The token.
    - client_id: The client ID.
    - client_secret: The client secret.
    - scopes: The scopes.
    - cw_api_url: The API URL.
    - company_id: The company ID.
    - integrationMap: The integration map.
    """

    _integration_name: str = None
    _connection_id: str = None
    _resource_list: List[str] = None
    _is_integration_call: bool = False
    _token: Token = None
    client_id: str = None
    client_secret: str = None
    scopes: List[str] = None
    cw_api_url: str = None
    company_id: str = None
    integrationMap : dict = None
    domain_name: str = None

    def __init__(self):
        """
        Initializes the HttpClient with client details from input file.

        This method reads the client details from an input file and sets the corresponding properties on the HttpClient instance.
        """
        try:
            input_data = Input()
            self.client_id = input_data.get_value(InputVariables.CW_OPEN_API_CLIENT_ID)
            self.client_secret = input_data.get_value(InputVariables.CW_OPEN_API_CLIENT_SECRET)
            self.scopes = input_data.get_value(InputVariables.CW_PARTNER_API_SCOPE)
            self.cw_api_url = input_data.get_value(InputVariables.CW_OPEN_API_URL_KEY)
            self.company_id = input_data.get_value(InputVariables.CW_COMPANY_ID)
            self.integrationMap = input_data.get_value(InputVariables.CW_INTEGRATION_Map)
            self.domain_name = input_data.get_value(InputVariables.CW_INTEGRATION_DOMAIN_NAME)
        except Exception:
            pass

    
    def get_integration_details(self, integration_name: str) -> dict:
        """
        Fetches the integration details.

        Args:
        - integration_name: The name of the integration.

        Returns:
        - A dictionary containing the integration details.
        """
        return self.integrationMap.get(integration_name)

    def third_party_integration(self, integration_ref_name: str, connection_id: str = None):
        """
        Sets up a third party integration.

        Args:
        - integration_name: Name of the integration.

        Returns:
        - An instance of HttpClient configured for the third party integration.
        """
        # get the integration details and check if it is valid or present or not else raise exception
        integration = self.get_integration_details(integration_ref_name)
        if not integration:
            raise Exception(f"{integration_ref_name} integration not found, please check the configured integrations")
        
        connectionId = connection_id or integration.get(CONNECTION_ID_KEY)
        if not connectionId:
            raise Exception(f"Connection ID not found for {integration_ref_name} integration, please check the configured integrations")
         
        third_party = copy.copy(self)
        third_party._integration_name = integration_ref_name
        third_party._connection_id = connectionId
        third_party._is_integration_call = True
        return third_party

    def fetch_token(self, client_id: str, client_secret: str, scopes: List[str]) -> Token:
        """
        Fetches a token for authentication.

        This method first creates a payload with the client ID, client secret, and scopes. It then validates the payload.

        It constructs the token URL and initializes the headers. It adds a content type to the headers.

        It then sends a POST request to the token URL with the payload and headers. If the request is successful, it parses the response to get the token data and returns a new Token object.

        If the request fails, it raises an exception. If the response status code is 404, it raises a specific exception indicating that the token could not be fetched.

        Args:
        - client_id: The client ID.
        - client_secret: The client secret.
        - scopes: The scopes.

        Returns:
        - A new Token object.

        Raises:
        - Exception: If the token could not be fetched.
        """
        scopes_string = " ".join(scopes if scopes is not None else [])
        payload = {
            GRANT_TYPE_KEY: DEFAULT_GRANT_TYPE,
            CLIENT_ID_KEY: client_id,
            CLIENT_SECRET_KEY: client_secret,
            SCOPE_KEY: scopes_string,
        }
        
        try:            
            self.validate_payload(payload, [GRANT_TYPE_KEY, CLIENT_ID_KEY, CLIENT_SECRET_KEY, SCOPE_KEY])
            token_url = urljoin(self.cw_api_url, TOKEN_PATH)
            headers = {}
            headers[HeaderKeys.CONTENT_TYPE] = ContentTypes.JSON
            response = requests.post(token_url, json=payload, headers=headers)
            if response.status_code == 200:
                token_data = response.json()
                return Token(token_data[ACCESS_TOKEN_KEY], token_data[EXPIRES_IN_KEY])
            
            raise Exception(f"status code: {response.status_code}, response: {response.text}")

        except Exception as e:            
            raise Exception(f"Failed to fetch token, {e}")


    def validate_payload(self, payload: Dict, required_fields: List[str]):
        """
        Validates the payload.

        Args:
        - payload: The payload to be validated.
        - required_fields: The required fields in the payload.

        Raises:
        - ValueError: If a required field is missing in the payload.
        """
        errors = []
        for field in required_fields:
            # Split the field into components to handle nested keys
            components = field.split('.')
            current_level = payload
            missing = False

            # Iterate through components to navigate the payload
            for component in components:
                if isinstance(current_level, dict) and component in current_level and current_level[component]:
                    current_level = current_level[component]
                else:
                    missing = True
                    break

            if missing:
                errors.append(f"Missing required field: {field}")

        if errors:
            raise ValueError(f"ValidationRequiredFieldMissing: {', '.join(errors)}")

    def generate_microsoftcsp_resource_list(self, url: str) -> List[str]:
        """
        Generates resource list for Microsoft CSP.

        Args:
        - url: The URL to generate the resource list from.

        Returns:
        - A list of resources.
        """
        parsed_url = urlparse(url)
        return [f"{parsed_url.scheme}://{parsed_url.netloc}"]

    def generate_integration_payload(self, integration_name: str, method: HttpMethod, url: str, body=None, resource_list: List[str] = None, connection_id: str = None) -> dict:
        """
        Generates payload for integration.

        Args:
        - integration_name: Name of the integration.
        - method: The HTTP method.
        - url: The URL.
        - body: The body of the request.
        - resource_list: List of resources for the integration.
        - connection_id: Connection ID for the integration.
        - domain_name: Domain name for the integration.

        Returns:
        - A dictionary representing the payload.
        """
        try:
            self.validate_url(url)
        except Exception as e:
            raise Exception(f"Invalid URL, {e}")

        if not resource_list and (integration_name == MICROSOFT_CSP or integration_name == AZURE_O365):
            resource_list = self.generate_microsoftcsp_resource_list(url)

        return {
            INTEGRATION_NAME_KEY: integration_name,
            CONNECTION_ID_KEY: connection_id or "",
            RESOURCE_LIST_KEY: resource_list or [],
            METHOD_KEY: method,
            URL_KEY: url,
            BODY_KEY: body or {},
            COMPANY_ID_KEY: self.company_id,
            DOMAIN_NAME_KEY: self.domain_name,
        }

    def is_token_required(self, url: str) -> bool:
        """
        Checks if token is required.

        Args:
        - url: The URL to check.

        Returns:
        - True if token is required, False otherwise.
        """
        if not self.cw_api_url:
            return False
        return url.startswith(self.cw_api_url)

    def validate_url(self, url: str):
        """
        Validates the URL.

        Args:
        - url: The URL to validate.

        Raises:
        - ValueError: If the URL is not valid.
        """

        if not url:
            raise ValueError(f"HttpClient: request URL is empty")

        parsed_url = urlparse(url)

        if not parsed_url.scheme:
            raise ValueError(
                f"HttpClient: unsupported protocol scheme: '{parsed_url.scheme}'"
            )

        if not parsed_url.netloc:
            raise ValueError(f"HttpClient: no Host in request URL")

    def send_request(self, method: HttpMethod, url: str, headers: dict = {}, **kwargs) -> requests.Response:
        """
        Sends the HTTP request.

        This method first validates the URL. If the URL is invalid, it raises an exception.

        It then checks if the headers are None. If they are, it initializes them. It also checks if the headers contain a content type. If not, it adds a default content type.

        If the request is for a third party integration, it generates the integration payload and modifies the method and URL for the request.

        It then checks if a token is required for the request. If it is, and if the token is either not present or expired, it fetches a new token. If the token is valid, it adds it to the headers.

        Finally, it sends the request and returns the response.

        Args:
        - method: The HTTP method.
        - url: The URL.
        - headers: The headers.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The response from the request.
        """

        try:
            self.validate_url(url)
        except Exception as e:
            raise Exception(f"Invalid URL, {e}")

        headers = {} if headers is None else headers
        if not headers.get(HeaderKeys.CONTENT_TYPE):
            headers[HeaderKeys.CONTENT_TYPE] = ContentTypes.JSON

        if self._integration_name and self._is_integration_call:
            body = kwargs.get("json")
            kwargs["json"] = self.generate_integration_payload(self._integration_name, method, url, body, self._resource_list, self._connection_id)
            method = HttpMethod.POST
            url = urljoin(self.cw_api_url, RPA_RESOLVE_PATH)

        if self.is_token_required(url):
            if not self._token or self._token.is_expired():
                self._token = self.fetch_token(self.client_id, self.client_secret, self.scopes)

            if self._token and self._token.is_expired() == False:
                headers[HeaderKeys.AUTHORIZATION] =  f"{HeaderKeys.BEARER} {self._token.get_token()}"
        
        return requests.request(method=method, url=url, headers=headers, **kwargs)

    def get(self, url: str, headers: dict = {}, **kwargs) -> requests.Response:
        """
        Sends a GET request.

        Args:
        - url: The URL.
        - headers: The headers.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The response from the request.
        """
        return self.send_request(HttpMethod.GET, url, headers, **kwargs)

    def post(self, url: str, headers: dict = {}, **kwargs) -> requests.Response:
        """
        Sends a POST request.

        Args:
        - url: The URL.
        - headers: The headers.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The response from the request.
        """
        return self.send_request(HttpMethod.POST, url, headers, **kwargs)

    def put(self, url: str, headers: dict = {}, **kwargs) -> requests.Response:
        """
        Sends a PUT request.

        Args:
        - url: The URL.
        - headers: The headers.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The response from the request.
        """
        return self.send_request(HttpMethod.PUT, url, headers, **kwargs)

    def delete(self, url: str, headers: dict = {}, **kwargs) -> requests.Response:
        """
        Sends a DELETE request.

        Args:
        - url: The URL.
        - headers: The headers.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The response from the request.
        """
        return self.send_request(HttpMethod.DELETE, url, headers, **kwargs)

    def patch(self, url: str, headers: dict = {}, **kwargs) -> requests.Response:
        """
        Sends a PATCH request.

        Args:
        - url: The URL.
        - headers: The headers.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The response from the request.
        """
        return self.send_request(HttpMethod.PATCH, url, headers, **kwargs)

    def options(self, url: str, headers: dict = {}, **kwargs) -> requests.Response:
        """
        Sends an OPTIONS request.

        Args:
        - url: The URL.
        - headers: The headers.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The response from the request.
        """
        return self.send_request(HttpMethod.OPTIONS, url, headers, **kwargs)

    def head(self, url: str, headers: dict = {}, **kwargs) -> requests.Response:
        """
        Sends a HEAD request.

        Args:
        - url: The URL.
        - headers: The headers.
        - **kwargs: Additional keyword arguments.

        Returns:
        - The response from the request.
        """
        return self.send_request(HttpMethod.HEAD, url, headers, **kwargs)
