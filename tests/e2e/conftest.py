"""Fixtures for end-to-end tests"""
import os
import re

import pytest
import requests
import requests_mock
from urllib3 import HTTPResponse

from tergite.qiskit.providers import Tergite, Provider
from tergite.qiskit.providers.provider_account import ProviderAccount
from tests.utils.env import is_end_to_end


@pytest.mark.skipif(not is_end_to_end(), reason="is end-to-end test")
@pytest.fixture
def mock_backend_servers():
    with requests_mock.Mocker(real_http=True) as mocker:
        matcher = re.compile(r"http://qiskit_pulse_")
        mocker.register_uri(requests_mock.ANY, matcher, raw=proxy_request)
        yield mocker


@pytest.mark.skipif(not is_end_to_end(), reason="is end-to-end test")
@pytest.fixture
def backend_provider(mock_backend_servers) -> Provider:
    """A provider that is authenticated using API token"""
    api_url = os.environ.get("API_URL")
    api_token = os.environ.get("API_TOKEN")
    account = ProviderAccount(service_name="test", url=api_url, token=api_token)
    return Tergite.use_provider_account(account)


def proxy_request(request: requests.Request, context) -> HTTPResponse:
    """A proxy server for the backends

    This is essential as the backend urls contain domain names
    that are specific to the docker network

    Args:
        request: the received request
        context: the context for the mocker

    Returns:
        the response
    """
    url: str = request.url
    url = url.replace("qiskit_pulse_1q:8000", "localhost:8001")
    url = url.replace("qiskit_pulse_2q:8000", "localhost:8000")
    forwarded_response = requests.request(
        method=request.method,
        url=url,
        headers=request.headers,
        data=request.body,
    )
    context.status_code = forwarded_response.status_code

    return forwarded_response.raw
