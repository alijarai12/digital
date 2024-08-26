import requests
import pytest
from api.test.helpers import *


def test_map_pop_up(base_url):
    response = requests.get(f"{base_url}map-popup/?id=3178&type=building")
    assert_status_code(response, 200)
