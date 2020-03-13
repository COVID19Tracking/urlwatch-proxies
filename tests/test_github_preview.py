import pytest
from web_tester import WebTester
import os
import json

site = WebTester("http://127.0.0.1:5000", trace=True)
#site = WebTester("http://covid19-api.exemplartech.com", trace=True)

def test_az():

    content, status = site.get_with_status("/github-data/captive-browser/az_tableau.html")
    assert(b'Arizona' in content)
    assert(status == 200)

    content = content.decode()

    idx = content.index("src='images/")
    idx += 5
    eidx = content.index("'", idx)
    img_link = content[idx:eidx]
    print(img_link)

    img = site.get_with_status(f"/github-data/{img_link}")
    assert(img != None)
    assert(status == 200)
