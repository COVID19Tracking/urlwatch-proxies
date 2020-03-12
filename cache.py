#
# Page Cache maintains a collection of cached files on disk
#
#   It has a concept of 'version'.  If provided, it will store
#   the data in a subdirectory.
#
#   It is extracted from my scanner so it has functionality that
#   doesn't apply in a web content.
#

import os
import shutil
import re
import datetime
import requests

from datetime import datetime, timezone
from loguru import logger
import pytz

from typing import Union, List, Tuple, Dict

from requests.packages import urllib3
urllib3.disable_warnings() 

def encode_key(key: str) -> str:
    """ convert to a file-stystem safe representation of a URL """

    result = re.sub("https?:.+/", "", key)
    result = re.sub("[/?=&]", "_", result)
    result = result.replace(".aspx", ".html")
    return result

def file_age(xpath: str) -> float:
    """ get age of a file in minutes """

    #print(xpath)
    mtime = os.path.getmtime(xpath)
    mtime = datetime.fromtimestamp(mtime)

    xnow = datetime.now()
    xdelta = (xnow - mtime).seconds / 60.0

    # print(f" time = {mtime}")
    # print(f" now = {xnow}")
    # print(f" delta = {xdelta}")

    return xdelta


class PageCache:
    """  a simple disk-based page cache """

    def __init__(self, work_dir: str):
        self.work_dir = work_dir

        if not os.path.isdir(self.work_dir):
            os.makedirs(self.work_dir)

    def read_old_date(self) -> str:
        " read date of previous run as string"
        xpath = os.path.join(self.work_dir, "time_stamp.txt")
        if os.path.exists(xpath):
            with open(xpath, "r") as f:
                old_date = f.readline()
        else:
            old_date = "[NONE]"
        return old_date

    def update_dates(self) -> Tuple[str, str]:
        " update date for new run, returns new_date and old_date as string "
        xpath = os.path.join(self.work_dir, "time_stamp.txt")
        if os.path.exists(xpath):
            with open(xpath, "r") as f:
                old_date = f.readline()
        else:
            old_date = "[NONE]"

        dt = datetime.now(timezone.utc).astimezone()
        new_date = f"{dt} ({dt.tzname()})" 
        with open(xpath, "w") as f:
            f.write(f"{new_date}\n")
        return new_date, old_date

    
    def fetch(self, page: str) -> [bytes, int]:
        " get a new page (does not save it)"
        #print(f"fetch {page}")
        try:
            resp = requests.get(page, verify=False)
            return resp.content, resp.status_code
        except Exception as ex:
            logger.error(f"Exception: {ex}")
            return None, 999

    def get_cache_age(self, key: str) -> float:
        " get age of a cached file in minutes "
        file_name = encode_key(key)
        xpath = os.path.join(self.work_dir, file_name)
        if not os.path.isfile(xpath): return 10000.0

        xdelta = file_age(xpath)
        return xdelta

    def read_date_time_str(self, key: str) -> str:
        " read the date/time of a cached page in a report friendly format "
        file_name = encode_key(key)
        xpath = os.path.join(self.work_dir, file_name)
        if not os.path.isfile(xpath): return "Missing"

        mtime = os.path.getmtime(xpath)
        mtime = datetime.fromtimestamp(mtime)
        dt = mtime

        def format_mins(x : float):
            if x < 60.0:
                return f"{x:.0f} mins"
            x /= 60.0
            if x < 24.0:
                return f"{x:.1f} hours"
            return f"{x:.1f} days"

        xdelta = file_age(xpath)
        return f"changed at {dt} ({dt.tzname()}): {format_mins(xdelta)} ago" 

    def get_cache_dir(self, version: str == None, create_if_missing = False) -> str:
        if version == None:
            xdir = self.work_dir
        else:
            xdir = os.path.join(self.work_dir, version)

        if create_if_missing:
            if not os.path.exists(xdir): os.makedirs(xdir)            
        return xdir

    def get_cache_path(self, key: str, version: str = None, create_dir_if_missing = False) -> str:
        file_name = encode_key(key)
        xdir = self.get_cache_dir(version, create_dir_if_missing)
        xpath = os.path.join(xdir, file_name)
        return xpath

    def does_version_exists(self, key: str, version: str = None) -> bool:
        """ check is a cached page exists 
        if version provided, it checks a subdirecotry
        """
        xpath = self.get_cache_path(key, version)
        return os.path.exists(xpath)

    def list_html_files(self) -> List[str]:
        " lists all cached viles "
        result = []
        for x in os.listdir(self.work_dir):
            if not x.endswith(".html"): continue
            result.append(x)
        return result


    def load(self, key: str, version: str = None) -> Union[bytes, None]:
        """ load a file from the cache
        returns byte array if found, returns None if missing
        """

        xpath = self.get_cache_path(key, version, create_dir_if_missing=True)
        if not os.path.isfile(xpath): return None

        r = open(xpath, "rb")
        try:
            content = r.read()
            return content
        finally:
            r.close()

    def copy_to_version(self, key: str, version: str):

        if version == None:
            raise Exception("Missing version")

        xfrom = self.get_cache_path(key)
        xto = self.get_cache_path(key, version, create_dir_if_missing=True)

        if os.path.exists(xto): os.remove(xto)
        if os.path.exists(xfrom): shutil.copy(xfrom, xto)
            


    def save(self, content: Union[bytes, None], key: str, version: str = None):
        """ saves content (bytes) to the cache
        if content is missing, delete it from the cache
        """
        xpath = self.get_cache_path(key, version, create_dir_if_missing=True)

        if content == None: 
            if os.path.exists(xpath): os.remove(xpath)
            return
        
        if not isinstance(content, bytes):
            raise TypeError("content must be type 'bytes'")

        w = open(xpath, "wb")
        try:
            w.write(content)
        finally:
            w.close()

    def cleanup(self, max_age_mins: int, version: str = None):
        """ remove old files in cache dir """

        xdir = self.get_cache_dir(version)
        if not os.path.exists(xdir): return

        for fn in os.listdir(xdir):
            xpath = os.path.join(xdir, fn)
            if file_age(xpath) > max_age_mins:
                os.remove(xpath)

    def reset(self, version: str = None):
        " reset all files in cache dir "
        xdir = self.get_cache_dir(version)
        if not os.path.exists(xdir): return

        for fn in xdir:
            xpath = os.path.join(xdir, fn)
            os.remove(xpath)
