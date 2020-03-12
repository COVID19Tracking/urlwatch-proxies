import os
from flask import Flask, request, jsonify
import requests
import json
from loguru import logger
from public_cache import PublicCache
from regularize import regularize

app = Flask(__name__)

# for auto-deploy support
#from webhook import webhook
#app.config['GITHUB_SECRET'] = os.environ.get('GITHUB_SECRET')
#app.config['REPO_PATH'] = os.environ.get('REPO_PATH')
#app.register_blueprint(webhook)

# -- public cache
#g_public_cache = PublicCache("/home/josh/public-cache")
g_public_cache = PublicCache("c:\\temp\\public-cache")

@app.route("/cache")
def pc_list():
    try:
        return jsonify(g_public_cache.list_items()), 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return str(ex), 500

@app.route("/cache/meta/<xid>", methods=["GET"])
def pc_get_meta(xid: str):
    try:
        x = g_public_cache.load_meta(xid)
        if x == None: return "", 304
        return jsonify(x), 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return "", 500

@app.route("/cache/<xid>", methods=["GET"])
def pc_get(xid: str):
    try:
        x = g_public_cache.load(xid)
        if x == None: return "", 304
        return x, 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return "", 500

@app.route("/cache/<xid>", methods=["POST"])
def pc_post(xid: str):
    owner = request.args.get("owner")    
    content = request.get_data()
    try:
        g_public_cache.save(content, xid, owner)
        return "", 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return "", 500

@app.route("/cache/<xid>", methods=["DELETE"])
def pc_delete(xid: str):
    owner = request.args.get("owner")    
    try:
        g_public_cache.delete(xid, owner)
        return "", 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return "", 500

# -- initial proxy code

def fetch(url: str) -> [bytes, int]:
    try:
        resp = requests.get(url, verify=False)
        return resp.content, resp.status_code
    except Exception as ex:
        #logger.error(f"Exception: {ex}")
        return f"{ex}", 501

@app.route("/proxy-raw/")
@app.route("/proxy-raw/<path:dest>")
def proxy_raw(dest: str):
    if dest == None or dest == "":
        return "", 200

    url = f"https://{dest}"
    content, status = fetch(url)
    return content, status
    
@app.route("/proxy/")
@app.route("/proxy/<path:dest>")
def proxy(dest: str):
    if dest == None or dest == "":
        return "", 200

    url = f"https://{dest}"
    content, status = fetch(url)
    if content != None:
        content = regularize(content)
    return content, status
    
@app.route("/")
def index():
    return "<h3>COVID19 urlwatch-proxies v0.05</h3>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')