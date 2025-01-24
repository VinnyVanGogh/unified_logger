# Constants for default values
DEFAULT_GRANT_TYPE = "client_credentials"

# Constants for integration payload attributes
INTEGRATION_NAME_KEY = "integrationName"
CONNECTION_ID_KEY = "connectionId"
RESOURCE_LIST_KEY = "resourceList"
METHOD_KEY = "method"
URL_KEY = "url"
BODY_KEY = "body"
COMPANY_ID_KEY = "clientId"
DOMAIN_NAME_KEY = "domainName"

# Constants for token payload attributes
GRANT_TYPE_KEY = "grant_type"
CLIENT_ID_KEY = "client_id"
CLIENT_SECRET_KEY = "client_secret"
SCOPE_KEY = "scope"

# Constants for token response attributes
ACCESS_TOKEN_KEY = "access_token"
EXPIRES_IN_KEY = "expires_in"

MICROSOFT_CSP = "microsoft_csp"
AZURE_O365 = "azure_o365"

class InputVariables:
    """
    Constants for the keys in the input file.
    """

    CW_OPEN_API_URL_KEY = "cwOpenAPIURL"
    CW_OPEN_API_CLIENT_ID = "cwOpenAPIClientId"
    CW_OPEN_API_CLIENT_SECRET = "cwOpenAPIClientSecret"
    CW_PARTNER_API_SCOPE = "cwPartnerAPIScope"
    CW_COMPANY_ID = "cwCompanyId"
    CW_SITE_ID = "cwSiteId"
    CW_INTEGRATION_Map = "cwIntegrationMap"
    CW_INTEGRATION_DOMAIN_NAME = "cwIntegrationDomainName"
