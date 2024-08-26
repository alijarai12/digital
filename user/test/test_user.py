import requests
import pytest
from user.test.helpers import *

# ============================== Get Requests ==============================


def test_user_list(base_url):
    url = f"{base_url}"
    response = requests.get(url)
    assert_status_code(response, 200)


def test_single_user(base_url):
    url = f"{base_url}/2"
    response = requests.get(url)
    assert_status_code(response, 200)


@pytest.fixture(scope="session")
def api_session():
    url = f"{URL}sign-in/"
    data = {"email": "alija@naxa.com", "password": "dmaps"}
    response = requests.post(url, data=data)
    assert_status_code(response, 200)
    session = requests.Session()
    session.headers.update({"Authorization": f"Token {response.json()['token']}"})
    yield session


def test_user_profile(api_session):
    url = f"{URL}profile/"
    response = api_session.get(url)
    assert_status_code(response, 200)


def test_user_role_unique_field():
    url = f"{URL}user-role-unique-fields"
    response = requests.get(url)
    assert_status_code(response, 200)


# ================================ POST Requests ==========================================

# def assert_status_code(response, expected_code):
#     assert (
#         response.status_code == expected_code
#     ), f"Expected {expected_code}, but got {response.status_code}"


# def test_create_user(base_url):
#     url = f"{base_url}"
#     data = {
#         "username": "thumbelina",
#         "designation": "princess",
#         "role_type": "super admin",
#         "email": "thumbelina@gmail.com",
#     }
#     response = requests.post(url, data=data)
#     assert_status_code(response, 201)
