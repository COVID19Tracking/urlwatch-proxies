import pytest
from public_cache import PublicCache
from cache import PageCache

def test_1():

    d = PageCache("c:\\temp\\cache")
    d.reset()
    c = PublicCache(d)

    x = c.list_items()
    assert(len(x) == 0)

    x = c.load("test_content.html")
    assert(x == None)

    test_content = b"<html><body>hi</body></html"
    c.save(test_content, "test_content.html", "josh")

    x = c.list_items()
    assert(len(x) == 1)
    assert(x[0]["id"] == "test_content.html")
    assert(x[0]["owner"] == "josh")
    assert(x[0]["content_length"] == len(test_content))

    c = c.load("test_content.html")
    assert(test_content == c)