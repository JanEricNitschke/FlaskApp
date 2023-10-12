"""Module with helper functions."""
from botocore.exceptions import ClientError


def check_error_code(error: ClientError, expected_code: str) -> bool:
    """Check the error code of the Client error against expectation.

    Args:
        error (ClientError): The client error to check the code for.
        expected_code (str): The expected error code.
    """
    try:
        return error.response["Error"]["Code"] == expected_code
    except KeyError:
        return False
