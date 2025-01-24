from datetime import datetime, timedelta


class Token:
    """
    Represents a token used for authentication.

    Attributes:
        token (str): The token value.
        expires_in (int): The number of seconds until the token expires.
    """

    def __init__(self, token, expires_in):
        """
        Initializes a Token object with a token and its expiration time.

        Args:
            token (str): The token value.
            expires_in (int): The number of seconds until the token expires.
        """
        self.token = token
        self.expires_in = datetime.now() + timedelta(seconds=expires_in)

    def get_token(self):
        """
        Returns the token value.

        Returns:
            str: The token value.
        """
        return self.token

    def is_expired(self):
        """
        Checks if the token has expired.

        Returns:
            bool: True if the token has expired, False otherwise.
        """
        return datetime.now() > self.expires_in
