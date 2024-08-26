import requests
import pytest
from api.test.helpers import *


@pytest.fixture
def update_data():
    return {
        "name_en": "abc",
        "name_ne": "xyz",
        "description_en": "abc",
        "description_ne": "aaa",
        "logo_en": None,
        "logo_ne": None,
        "created_by": 2,
    }


def test_palika_profile(base_url):
    url = f"{base_url}palika-profile/"
    response = requests.get(url)
    assert_status_code(response, 200)


def test_update_palika_profile(base_url, update_data):
    url = f"{base_url}palika-profile/2/"
    response = requests.patch(url, data=update_data)
    assert_status_code(response, 200)


def test_create_geometry_file():
    url = "http://localhost:8000/api/v1/palika-geometry-file/"
    files = {"file_upload": open("file/MyLayer2.zip", "rb")}
    data = {
        "file_type": "palika",
    }

    response = requests.post(url, data=data, files=files)
    assert_status_code(response, 200)


def test_update_geometry_file():
    url = "http://localhost:8000/api/v1/palika-geometry-file/2/"

    files = {"file_upload": open("file/MyLayer2.zip", "rb")}

    data = {
        "file_type": "palika",
    }
    response = requests.patch(url, data=data, files=files)
    assert_status_code(response, 200)


def test_palika_ward_geojson(api_url, id=None):
    if id:
        specific_url = f"{api_url}?ward_no={id}"
        response = requests.get(specific_url)
    else:
        response = requests.get(api_url)
    assert_status_code(response, 200)


class TestPalikaWardGeojson:
    def test_get_list(self, api_url):
        test_palika_ward_geojson(api_url)

    def test_get_specific(self, api_url):
        id = 1  # Replace with ward ID
        test_palika_ward_geojson(api_url, id)
