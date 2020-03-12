import pytest
from web_tester import WebTester
import os
import json

site = WebTester("http://127.0.0.1:5000", trace=True)

def delete_dir_if_exists(xdir: str):
    if not os.path.exists(xdir): return

    for fn in os.listdir(xdir):
        xpath = os.path.join(xdir, fn)
        os.remove(xpath)

def test_lifecycle():

    delete_dir_if_exists("c:\\temp\\public-cache")

    x = site.get("/cache")
    assert(x == b'[]\n')

    x, s = site.get_with_status("/cache/test_content.html")
    assert(x == b'')
    assert(s == 304)

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

 