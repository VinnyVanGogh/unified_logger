class HttpMethod:
    """
    Enum-like class representing HTTP methods.

    This class provides a set of constants representing the HTTP methods used in requests. It simplifies the use of HTTP methods by providing a single point of reference for their string representations.

    Attributes:
        GET (str): Represents the HTTP GET method, used for retrieving resources.
        POST (str): Represents the HTTP POST method, used for creating resources.
        PUT (str): Represents the HTTP PUT method, used for updating/replacing resources.
        DELETE (str): Represents the HTTP DELETE method, used for deleting resources.
        PATCH (str): Represents the HTTP PATCH method, used for making partial updates to resources.
        OPTIONS (str): Represents the HTTP OPTIONS method, used for describing the communication options for the target resource.
        HEAD (str): Represents the HTTP HEAD method, used for retrieving the headers of a resource.
    """

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class HeaderKeys:
    """
    Enum-like class representing common HTTP header keys.

    This class defines constants for common HTTP header keys. These constants are used throughout the application to ensure consistency in the use of HTTP headers.

    Attributes:
        AUTHORIZATION (str): Represents the 'Authorization' header, used for passing auth credentials.
        BEARER (str): Represents the 'Bearer' token prefix used in Authorization headers.
        CONTENT_TYPE (str): Represents the 'Content-Type' header, indicating the media type of the resource.
        CONTENT_LENGTH (str): Represents the 'Content-Length' header, indicating the size of the entity-body in bytes.
        ACCEPT (str): Represents the 'Accept' header, indicating the media types that the client is willing to receive.
        ACCEPT_LANGUAGE (str): Represents the 'Accept-Language' header, indicating the preferred languages for the response.
        ACCEPT_ENCODING (str): Represents the 'Accept-Encoding' header, indicating the acceptable content codings.
        USER_AGENT (str): Represents the 'User-Agent' header, containing information about the user agent originating the request.
    """

    AUTHORIZATION = "Authorization"
    BEARER = "Bearer"
    CONTENT_TYPE = "Content-Type"
    CONTENT_LENGTH = "Content-Length"
    ACCEPT = "Accept"
    ACCEPT_LANGUAGE = "Accept-Language"
    ACCEPT_ENCODING = "Accept-Encoding"
    USER_AGENT = "User-Agent"


class ContentTypes:
    """
    Enum-like class representing common MIME types for content negotiation in HTTP requests and responses.

    This class provides a set of constants representing various MIME types. These constants are used throughout the application to specify the content type of HTTP request and response bodies. Using these constants helps ensure consistency and readability in specifying content types across different parts of the application.

    Attributes:
        JSON (str): Represents the MIME type for JSON content, used for most API interactions.
        FORM (str): Represents the MIME type for URL-encoded form data, commonly used in form submissions.
        TEXT (str): Represents the MIME type for plain text content.
        HTML (str): Represents the MIME type for HTML content, used in web pages.
        XML (str): Represents the MIME type for XML content, used in various web services.
        MULTIPART (str): Represents the MIME type for multipart form data, used for uploading files.
        PDF (str): Represents the MIME type for PDF documents.
        ZIP (str): Represents the MIME type for ZIP archives.
        OCTET_STREAM (str): Represents the MIME type for arbitrary binary data.
        PNG (str): Represents the MIME type for PNG images.
        JPEG (str): Represents the MIME type for JPEG images.
        GIF (str): Represents the MIME type for GIF images.
        SVG (str): Represents the MIME type for SVG vector images.
        CSV (str): Represents the MIME type for CSV files, used in data export/import.
        EXCEL (str): Represents the MIME type for Microsoft Excel files.
        WORD (str): Represents the MIME type for Microsoft Word documents.
        POWERPOINT (str): Represents the MIME type for Microsoft PowerPoint presentations.
    """

    JSON = "application/json"
    FORM = "application/x-www-form-urlencoded"
    TEXT = "text/plain"
    HTML = "text/html"
    XML = "application/xml"
    MULTIPART = "multipart/form-data"
    PDF = "application/pdf"
    ZIP = "application/zip"
    OCTET_STREAM = "application/octet-stream"
    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"
    SVG = "image/svg+xml"
    CSV = "text/csv"
    EXCEL = "application/vnd.ms-excel"
    WORD = "application/msword"
    POWERPOINT = "application/vnd.ms-powerpoint"
    AUDIO = "audio/mpeg"
    VIDEO = "video/mp4"
    STREAM = "application/octet-stream"
    ANY = "*/*"
