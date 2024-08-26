import requests
import pytest
from api.test.helpers import *


def test_building_unique_fields(base_url):
    response = requests.get(
        f"{base_url}building-unique-fields/?field_name=owner_status"
    )
    assert_status_code(response, 200)


def test_building_unique_values(base_url):
    response = requests.get(f"{base_url}building-unique-values/?field_name=ward_no")
    assert_status_code(response, 200)


def test_road_unique_fields(base_url):
    response = requests.get(f"{base_url}road-unique-fields/?field_name=road_category")
    assert_status_code(response, 200)


def test_road_unique_values(base_url):
    response = requests.get(f"{base_url}road-unique-values/?field_name=road_type")
    assert_status_code(response, 200)
