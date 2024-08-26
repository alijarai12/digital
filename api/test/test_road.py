import requests
import pytest
from api.test.helpers import *


def test_road(base_url):
    url = f"{base_url}road-data/"
    response = requests.get(url)
    assert_status_code(response, 200)


def test_specific_road(base_url):
    url = f"{base_url}road-data/201/"
    response = requests.get(url)
    assert_status_code(response, 200)
