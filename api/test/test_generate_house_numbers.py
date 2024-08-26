import requests
import pytest
from api.test.helpers import *


def test_generate_house_numbers(base_url):
    response = requests.get(f"{base_url}generate-house-numbers/?data_id=3180")
    assert_status_code(response, 200)
