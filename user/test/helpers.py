import pytest


# Common URL for the API
URL = "http://localhost:8000/api/v1/user/"


# Fixture to set up the base URL for the API
@pytest.fixture
def base_url():
    return f"{URL}user"


def assert_status_code(response, expected_code):
    assert (
        response.status_code == expected_code
    ), f"Expected {expected_code}, but got {response.status_code}"
