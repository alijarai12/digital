import requests
import pytest
from api.test.helpers import *


def test_download(base_url):
    response = requests.get(f"{base_url}download/?file_format=shapefile&layer=road")
    assert_status_code(response, 200)
