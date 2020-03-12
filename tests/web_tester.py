import requests
import pytest
from loguru import logger
from typing import Tuple

from requests.packages import urllib3
urllib3.disable_warnings() 

class WebTester:

    def __init__(self, api_url: str, trace=False):
        self.api_url = api_url
        self.trace = trace
        self.verify = False

        if self.trace:
            logger.info(f"base site is {api_url}")

    def expand_url(self, sub_url: str):
        if sub_url == None: return self.api_url
        if sub_url.lower().startswith("http"): return sub_url
        if not sub_url.startswith("/"):
            return self.api_url + "/" + sub_url
        else:
            return self.api_url + sub_url

    def trace_before(self, method: str, url: str, content: bytes = None):
        if not self.trace: return
        if content == None:
            logger.info(f"{method} {url}")
        else:
            logger.info(f"{method} {url} with content =\n{content}")

    def trace_after(self, method: str, url: str, resp: requests.Response, check_status=True):
        if check_status and resp.status_code > 299:
            pytest.fail(f"{method} {url} failed: {resp.status_code} with content =\n{resp.content}")
        elif self.trace:
            logger.info(f"{method} {url} return\n{resp.content}")
 
    def get(self, sub_url: str) -> bytes:
        url = self.expand_url(sub_url)
        self.trace_before("GET", url)
        resp = requests.get(url, verify=self.verify)
        self.trace_after("GET", url, resp)
        return resp.content

    def get_with_status(self, sub_url: str) -> Tuple[bytes, int]:
        url = self.expand_url(sub_url)
        self.trace_before("GET", url)
        resp = requests.get(url, verify=self.verify)
        self.trace_after("GET", url, resp, check_status=False)
        return resp.content, resp.status_code

    def post(self, sub_url: str, content: bytes) -> bytes:
        url = self.expand_url(sub_url)
        self.trace_before("POST", url)
        resp = requests.post(url, data=content, verify=self.verify)
        self.trace_after("POST", url, resp)
        return resp.content

    def delete(self, sub_url: str) -> bytes:
        url = self.expand_url(sub_url)
        self.trace_before("DELETE", url)
        resp = requests.delete(url)
        self.trace_after("DELETE", url, resp)
        return resp.content
