import pytest
from web_tester import WebTester
import os
import json
from loguru import logger

site = WebTester("http://127.0.0.1:5000", trace=True)
#site = WebTester("http://covid19-api.exemplartech.com", trace=True)

def test_lifecycle():

    x = site.get("/cache")
    items = json.loads(x.decode())
    for i in range(items):
        logger.info(f"cache {i+1}: {items[i]}")

    x, s = site.get_with_status("/cache/test_content.html")
    assert(x == b'')
    assert(s == 404)

    test_content = b"<html><body>hi</body></html"
    site.post("/cache/test_content.html?owner=josh", test_content)

    x = site.get("/cache")
    x = json.loads(x)
    assert(len(x) == 1)
    assert(x[0]["id"] == "test_content.html")
    assert(x[0]["owner"] == "josh")
    assert(x[0]["content_length"] == len(test_content))

    c = site.get("/cache/test_content.html")
    assert(test_content == c)

    site.delete("/cache/test_content.html?owner=josh")
    x = site.get("/cache")
    assert(x == b'[]\n')

    test_content = b"<html><body>hi</body></html"
    site.post("/cache/test_content.html?owner=josh", test_content)

 