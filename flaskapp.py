import os
from flask import Flask, request, jsonify
import requests
import json
from loguru import logger

from public_cache import PublicCache
from regularize import regularize
from sheet_parser import SheetParser

app = Flask(__name__)

# for auto-deploy support
#from webhook import webhook
#app.config['GITHUB_SECRET'] = os.environ.get('GITHUB_SECRET')
#app.config['REPO_PATH'] = os.environ.get('REPO_PATH')
#app.register_blueprint(webhook)

# -- public cache
g_public_cache = PublicCache("/home/josh/public-cache")
#g_public_cache = PublicCache("c:\\temp\\public-cache")

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
        if x == None: return "", 404
        return jsonify(x), 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return "", 500

@app.route("/cache/<xid>", methods=["GET"])
def pc_get(xid: str):
    try:
        x = g_public_cache.load(xid)
        if x == None: return "", 404
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


# -- data source:


def get_rawcontent_url(repo: str, link: str):
    base_path = repo.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob", "")
    return base_path + "/" + link

@app.route("/config/urls.yaml")
def config_urls():

    repo_url = "https://github.com/COVID19Tracking/covid-tracking/blob/master"
    preview_url = get_rawcontent_url(repo_url, "urls.yaml")
    logger.info(f"fetch from {preview_url}")
    return fetch(preview_url)

@app.route("/config/google-sheet.json")
def config_google():

    main_sheet = "https://docs.google.com/spreadsheets/d/18oVRrHj3c183mHmq3m89_163yuYltLNlOmPerQ18E8w/htmlview?sle=true"
    content, status = fetch(main_sheet)
    logger.info(f"status = {status}")

    if status >= 300: return "", status

    parser = SheetParser()
    x = parser.get_config(content)
    return jsonify(x), 200




# -- github data view:

@app.route("/github-data/")
@app.route("/github-data/<path:dest>")
def github_preview(dest: str):

    repo_url = "https://github.com/joshuaellinger/corona19-data-archive/blob/master"
    preview_url = get_rawcontent_url(repo_url, dest)

    logger.info(f"fetch from {preview_url}")
    return fetch(preview_url)


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
