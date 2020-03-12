import re
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from typing import Callable

class CaptiveBrowser:

    def __init__(self):

        self.driver = webdriver.Chrome()

    def get(self, url: str):
        self.driver.get(url)
    
    def wait(self, secs: int, wait_for: Callable = None):
        w = WebDriverWait(self.driver, secs)
        if wait_for != None:
            w.until(wait_for)

    def page_source(self):
        return self.driver.page_source


# ---------------------------

def test():

    b = CaptiveBrowser()

    #url = 'https://app.powerbigov.us/view?r=eyJrIjoiMWQ1YjdmZjgtYWE3YS00YTg5LTk4NGEtMDE2NWY1ZWJkYWJmIiwidCI6IjJkZWEwNDY0LWRhNTEtNGE4OC1iYWUyLWIzZGI5NGJjMGM1NCJ9'
    #url = "https://www.azdhs.gov/preparedness/epidemiology-disease-control/infectious-disease-epidemiology/index.php#novel-coronavirus-home"
    url = "https://tableau.azdhs.gov/views/COVID-19Table/COVID-19table?:embed=y&:showVizHome=no&:host_url=https%3A%2F%2Ftableau.azdhs.gov%2F&:embed_code_version=3&:tabs=no&:toolbar=no&:showAppBanner=false&:display_spinner=no&iframeSizedToWindow=true&:loadOrderID=0"
    b.get(url)

    content = b.page_source()
    print(content)

if __name__ == "__main__":
    test()


