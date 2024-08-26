import pytest


# Common URL for the API
URL = "http://localhost:8000/api/v1/"


# Fixture to set up the base URL for the API
@pytest.fixture
def base_url():
    return f"{URL}"


def assert_status_code(response, expected_code):
    assert (
        response.status_code == expected_code
    ), f"Expected {expected_code}, but got {response.status_code}"


@pytest.fixture
def dashboard_url(base_url):
    return f"{base_url}dashboard/"


@pytest.fixture
def api_url():
    return "http://localhost:8000/api/v1/palika-ward-geojson/"


@pytest.fixture
def palika_ward_api_url():
    return "http://localhost:8000/api/v1/palika-ward/"
