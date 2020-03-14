import pytest
from web_tester import WebTester
import os
import json

import yaml

site = WebTester("http://127.0.0.1:5000", trace=True)
#site = WebTester("http://covid19-api.exemplartech.com", trace=True)

def test_yaml():

    content, status = site.get_with_status("/config/urls.yaml")
    assert(status == 200)
    
    items = yaml.load_all(content.decode())
    for x in items:
        assert(x["name"] == "Alaska")
        break

    content, status = site.get_with_status("/config/urls.json")
    assert(status == 200)
    
    items = json.loads(content.decode())
    for x in items:
        assert(x["name"] == "Alaska")
        break

def test_google():

    content, status = site.get_with_status("/config/google-sheet.json")
    assert(status == 200)

    y = json.loads(content.decode())
    print(y)
    print(y[0])
    assert(y[0]["State"] == "AK")
