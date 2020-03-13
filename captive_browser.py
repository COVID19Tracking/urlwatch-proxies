import re
import requests
import os
import io
import shutil
from loguru import logger
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from typing import Callable
from datetime import datetime, timezone

import numpy as np
import imageio
import time

class CaptiveBrowser:

    def __init__(self):

        #https://github.com/mozilla/geckodriver/releases
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)

        #options = webdriver.ChromeOptions()
        #options.add_argument('headless')
        #self.driver = webdriver.Chrome(options=options)

    def get(self, url: str):
        self.driver.get(url)
    
    def wait(self, secs: int, wait_for: Callable = None):
        w = WebDriverWait(self.driver, secs)
        if wait_for != None:
            w.until(wait_for)

    def page_source(self):
        return self.driver.page_source

    def post_to_remote_cache(self, id: str, owner: str, content: bytes):
        url = f"http://covid19-api.exemplartech.com/cache/{id}?owner={owner}"
        resp = requests.post(url, data=content, verify=False)
        if resp.status_code >= 300:
            logger.error(f"post to cache at {url} failed status={resp.status_code}")
        return url

    def save_screenshot(self, xpath: str):
        self.driver.save_screenshot(xpath)

    def close(self):
        self.driver.close()

# ---------------------------

def test_az_tableau_content():

    b = CaptiveBrowser()

    print("1. get content from AZ")
    url = "https://tableau.azdhs.gov/views/COVID-19Table/COVID-19table?:embed=y&:showVizHome=no&:host_url=https%3A%2F%2Ftableau.azdhs.gov%2F&:embed_code_version=3&:tabs=no&:toolbar=no&:showAppBanner=false&:display_spinner=no&iframeSizedToWindow=true&:loadOrderID=0"
    b.get(url)
    content = b.page_source()

    print(f"2. post cache")
    cache_url = b.post_to_remote_cache("tableau_az.html", "joshua_ellinger", content)
    print(f"posted {len(content)} bytes to cache at {cache_url}")


def are_images_the_same(path1: str, path2: str, out_path: str) -> bool:

    buffer1 = imageio.imread(path1, as_gray=True)
    buffer2 = imageio.imread(path2, as_gray=True)

    diff = buffer1 - buffer2
    xmin, xmax = diff.min(), diff.max()
    if xmin != xmax and xmin != 0 and xmax != 255.0:
        scale = 255.0 / (xmax - xmin)
        diff = ((diff - xmin) * scale).astype(np.uint8)
        h = np.histogram(diff)
        print(h)
        imageio.imwrite(out_path, diff, format="jpg")
        return False

    return True


def format_datetime(dt: datetime):
    #return dt.isoformat().replace(":", "_x_").replace("+", "_p_")
    return dt.strftime('%Y%m%d-%H%M%S')

def test_az_tableau_image():

    xpath = "c:\\temp\\public-cache\\az_tableau.png"
    xpath_temp = "c:\\temp\\public-cache\\az_tableau_temp.png"
    xpath_prev = "c:\\temp\\public-cache\\az_tableau_prev.png"
    xpath_diff = "c:\\temp\\public-cache\\az_tableau_diff.png"

    if True:
        b = CaptiveBrowser()
    
        print("1. get content from AZ")
        url = "https://tableau.azdhs.gov/views/COVID-19Table/COVID-19table?:embed=y&:showVizHome=no&:host_url=https%3A%2F%2Ftableau.azdhs.gov%2F&:embed_code_version=3&:tabs=no&:toolbar=no&:showAppBanner=false&:display_spinner=no&iframeSizedToWindow=true&:loadOrderID=0"
        b.get(url)
        
        time.sleep(5)

        print("2. save screenshot")
        b.save_screenshot(xpath_temp)
        b.close()
   
    if os.path.exists(xpath):
        if are_images_the_same(xpath, xpath_temp, xpath_diff):
            logger.info("images are the same")
            #if os.path.exists(xpath_temp): os.remove(xpath_temp)
            #if os.path.exists(xpath_diff): os.remove(xpath_diff)
            return
        else:
            logger.info("images are different")
            if os.path.exists(xpath_prev): os.remove(xpath_prev)
            if os.path.exists(xpath): os.rename(xpath, xpath_prev)
            os.rename(xpath_temp, xpath)
    else:
        logger.info("image is new")
        os.rename(xpath_temp, xpath)

    #dt = datetime.now(timezone.utc)
    #xpath_unique = xpath.replace(".png", "_" + format_datetime(dt) + ".png")
    #shutil.copyfile(xpath, xpath_unique)



if __name__ == "__main__":
    test_az_tableau_image()


