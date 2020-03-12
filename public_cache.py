#
# Public Cache - a way for people to submit content with minimal friction
#
# POST to /cache?id=name&user=you to create/update an item
# DELETE to /cache?id=name&user=you to delete an items
# GET to /cache to list items
# GET to /cache?id=name to get an item
#

from cache import PageCache
import re
import json
import datetime

from typing import List, Dict

class PublicCache:

    def __init__(self, xdir: str):
        self.cache =  PageCache(xdir)

    def validate_id(self,xid: str):

        if xid == None or len(xid) < 5:
            raise Exception(f"ID ({xid}) must be at least 5 characters")

        new_id = re.sub("[/?=&:+<>!@*()#]", "_", xid)
        if new_id != xid:
            raise Exception(f"ID ({xid}) cannot contain /?=&:+<>!@*()#")
        new_id = new_id.lower()
        if new_id.startswith("http"):
            raise Exception(f"ID ({xid}) cannot start with http")
        if new_id.endswith(".meta"):
            raise Exception(f"ID ({xid}) cannot end with .meta")

    def list_items(self) -> List:

        result = []
        items = self.cache.list_files(suffix=".meta")
        for x in items:
            c = self.cache.load(x)
            m = json.loads(c.decode())
            result.append(m)
        return result

    def exists(self, xid: str) -> bool:
        self.validate_id(xid)
        return self.cache.does_version_exists(xid)

    def load(self, xid: str) -> bytes:
        self.validate_id(xid)
        return self.cache.load(xid)

    def load_meta(self, xid: str) -> Dict:
        m_bytes = self.cache.load(xid + ".meta")
        if m_bytes == None: return None
        m = m_bytes.decode()
        return json.loads(m)

    def make_meta(self, content: bytes, xid: str, owner: str) -> Dict:
        return {
            "content_length": len(content),
            "id": xid,
            "owner": owner,
            "saved_at": datetime.datetime.now().isoformat()
        }

    def validate_owner(self, xid: str, owner: str):
        if len(owner) == 0:
            raise Exception("Missing Owner")
        m = self.load_meta(xid)                
        if m != None and m.get("owner") != owner:
            raise Exception(f"ID {xid} is owned by {m.get['owner']}")

    def save(self, content: bytes, xid: str, owner: str):
        self.validate_id(xid)
        self.validate_owner(xid, owner)
        m = self.make_meta(content, xid, owner)
        m_str = json.dumps(m)
        self.cache.save(m_str.encode(), xid + ".meta")
        self.cache.save(content, xid)

    def delete(self, xid: str, owner: str):
        self.validate_id(xid)
        self.validate_owner(xid, owner)
        self.cache.delete(xid)
        self.cache.delete(xid + ".meta")

