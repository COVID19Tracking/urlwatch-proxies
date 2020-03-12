import pytest
from typing import Tuple
import time
from lxml import html
from loguru import logger
from web_tester import WebTester

#site = WebTester("http://covid19-api.exemplartech.com/")
#site = WebTester("http://127.0.0.1:5000", trace=True)
site = None

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

    if site == None:
        logger.warning("Site connection disabled")
        return

    # this URL trigger the regularization rules
    url = "www.alabamapublichealth.gov/infectiousdiseases/2019-coronavirus.html"

    logger.info("1. get content directly")
    direct_content = site.get(f"https://{url}")

    logger.info("2. get content through raw proxy")
    raw_proxy_content = site.get(f"/proxy-raw/{url}")

    if direct_content != raw_proxy_content:
        pytest.fail("Direct and Raw-Proxy differ ")

    logger.info("3. get content through proxy w/regularization")
    proxy_content = site.get(f"/proxy/{url}")

    content_a, content_b = get_unique_nodes(direct_content, proxy_content)
    logger.info(f"==== before regularization >>>\n{content_a}<<<<\n")
    logger.info(f"==== after regularization >>>\n{content_b}<<<<\n")

    if direct_content == proxy_content:
        pytest.fail("Direct and Proxy are the same ")

    time.sleep(5)

    logger.info("4. get same content again")
    proxy_content_b = site.get(f"/proxy/{url}")

    if proxy_content != proxy_content_b:
        pytest.fail("Proxy and Proxy B are differnt ")



