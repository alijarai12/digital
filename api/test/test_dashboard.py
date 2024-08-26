import requests
import pytest
from api.test.helpers import *


@pytest.fixture
def dashboard_feature_url(base_url):
    return f"{base_url}dashboard/feature-count/"


def test_total_building_feature_count(dashboard_feature_url):
    # response = requests.get(f"{dashboard_feature_url}?layer=building")
    response = requests.get(f"{dashboard_feature_url}?layer=building&ward_no=7")
    assert_status_code(response, 200)


def test_total_road_feature_count(dashboard_feature_url):
    # response = requests.get(f"{dashboard_feature_url}?layer=road")
    response = requests.get(f"{dashboard_feature_url}?layer=road&ward_no=7")
    assert_status_code(response, 200)


# ================================ Floor Count ================================

# @pytest.fixture
# def dashboard_floor_url(base_url):
#     return f"{base_url}dashboard/"


# def test_total_floor_count(dashboard_floor_url):
#     response = requests.get(f"{dashboard_floor_url}floor-count/")
#     assert_status_code(response, 200)
#     print(response.json())


# def test_total_floor_count(base_url):
#     response = requests.get(f"{base_url}dashboard/floor-count/")
#     assert_status_code(response, 200)
#     print(response.json())


# =============================================================================


def test_ward_no_list(base_url):
    response = requests.get(f"{base_url}dashboard/unique-ward-no/")
    assert_status_code(response, 200)


def test_building_counts_by_road_fields(dashboard_url):
    response = requests.get(
        f"{dashboard_url}building-field-count/?field_name=road_type"
    )
    assert_status_code(response, 200)
