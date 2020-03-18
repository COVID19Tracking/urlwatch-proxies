import pytest
from web_tester import WebTester
import os
import json

site = WebTester("http://127.0.0.1:5000", trace=True)

def test_good_mime():

    x = site.get("/github-data/extract/index.html")
    assert(b"<html" in x)
    x, status = site.get_with_status("/github-data/extract/index.json")
    assert(status == 404)
    x = site.get("/github-data/extract/change_list.json")
    assert(len(json.load(x.decode())) > 0)

def test_bad_mime():

    x, status = site.get_with_status("/github-data/extract/index.exe")
    assert(status == 415)
    assert(x == b"Invalid FileType")

