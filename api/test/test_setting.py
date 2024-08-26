import requests
import pytest
from api.test.helpers import *


def test_physical_installation(base_url):
    response = requests.get(f"{base_url}settings/physical-installation/")
    assert_status_code(response, 200)


def test_physical_installation(base_url):
    response = requests.get(f"{base_url}settings/physical-installation/latest/")
    assert_status_code(response, 200)


def test_specific_physical_installation(base_url):
    response = requests.get(f"{base_url}settings/physical-installation/1/")
    assert_status_code(response, 200)
