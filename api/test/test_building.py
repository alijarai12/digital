import requests
import pytest
from api.test.helpers import *


def test_building(base_url):
    url = f"{base_url}building-data/"
    response = requests.get(url)
    assert_status_code(response, 200)


def test_specific_building(base_url):
    url = f"{base_url}building-data/1593"
    response = requests.get(url)
    assert_status_code(response, 200)


def test_building_images(base_url):
    # url = f"{base_url}building-images/?building_id=1593&image_type=building_image"
    url = f"{base_url}building-images/?building_id=1593"
    response = requests.get(url)
    assert_status_code(response, 200)


def test_building_geometry(base_url):
    url = f"{base_url}building-geometry/1594/"
    response = requests.get(url)
    assert_status_code(response, 200)
