import pytest
from typing import Tuple
import requests
import time
from lxml import html


from requests.packages import urllib3
urllib3.disable_warnings() 

def fetch(page: str) -> bytes:
    try:
        resp = requests.get(page, verify=False)
        if resp.status_code >= 300:
            pytest.fail(f"GET {page} failed with status={resp.status_code}")
        return resp.content
    except Exception as ex:
        pytest.fail(f"GET {page} failed with exception {ex}")

proxy_site = "http://covid19-api.exemplartech.com/"

def remove_identical_nodes(elem1: html.Element, elem2: html.Element) -> bool:
    
    s1 = html.tostring(elem1)
    s2 = html.tostring(elem2)
    if s1 == s2: return True

    to_remove = []
    n = min(len(elem1), len(elem2))
    for i in range(n):
        is_same = remove_identical_nodes(elem1[i], elem2[i])
        if is_same: to_remove.append(i)
    
    to_remove.reverse()
    for i in to_remove:
        elem1.remove(elem1[i])
        elem2.remove(elem2[i])

    return False

def get_unique_nodes(content_a: bytes, content_b: bytes) -> Tuple[bytes, bytes]:

    doc_a = html.fromstring(content_a)
    doc_b = html.fromstring(content_b)
    remove_identical_nodes(doc_a, doc_b)
    content_a = html.tostring(doc_a, pretty_print=True)
    content_b = html.tostring(doc_b, pretty_print=True)
    return content_a, content_b

def test_regularization_1():

    # this URL trigger the regularization rules
    url = "www.alabamapublichealth.gov/infectiousdiseases/2019-coronavirus.html"

    print("1. get content directly")
    direct_content = fetch(f"https://{url}")

    print("2. get content through raw proxy")
    raw_proxy_content = fetch(f"{proxy_site}/proxy-raw/{url}")

    if direct_content != raw_proxy_content:
        pytest.fail("Direct and Raw-Proxy differ ")

    print("3. get content through proxy w/regularization")
    proxy_content = fetch(f"{proxy_site}/proxy/{url}")

    content_a, content_b = get_unique_nodes(direct_content, proxy_content)
    print(f"==== before regularization >>>\n{content_a}<<<<\n")
    print(f"==== after regularization >>>\n{content_b}<<<<\n")

    if direct_content == proxy_content:
        pytest.fail("Direct and Proxy are the same ")

    time.sleep(5)

    print("4. get same content again")
    proxy_content_b = fetch(f"{proxy_site}/proxy/{url}")

    if proxy_content != proxy_content_b:
        pytest.fail("Proxy and Proxy B are differnt ")



