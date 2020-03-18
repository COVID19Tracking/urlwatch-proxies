import pytest
from web_tester import WebTester
import os
import json
from loguru import logger

site = WebTester("http://127.0.0.1:5000", trace=True)
#site = WebTester("http://covid19-api.exemplartech.com", trace=True)

def test_list():

    test_content = b"<html><body>hi</body></html"
    site.post("/cache/test_content.html?owner=josh", test_content)

    x = site.get("/cache")
    items = json.loads(x.decode())
    assert(type(items[0]) == str)

    x = site.get("/cache?full=1&owner=josh")
    items = json.loads(x.decode())
    assert(type(items[0]) == dict)
    assert(items[0]["owner"] == "josh")

    x = site.get("/cache?owner=josh")
    items2 = json.loads(x.decode())
    assert(type(items2[0]) == str)
    assert(items[0]["id"] == items2[0])

def test_metadata():

    test_content = b"<html><body>hi</body></html"
    site.post("/cache/test_content.html?owner=josh", test_content)

    x = site.get("/cache/meta-data/test_content.html")
    logger.info(f"meta = {x}")
    item = json.loads(x.decode())
    assert(item["id"] == "test_content.html")


def test_lifecycle():

    test_content = b"<html><body>hi</body></html"
    site.post("/cache/test_content.html?owner=josh", test_content)

    c = site.get("/cache/test_content.html")
    assert(test_content == c)

    site.delete("/cache/test_content.html?owner=josh")
    x, s = site.get_with_status("/cache/test_content.html")
    assert(x == b'Missing File')
    assert(s == 404)

    test_content = b"<html><body>hi</body></html"
    site.post("/cache/test_content.html?owner=josh", test_content)

 