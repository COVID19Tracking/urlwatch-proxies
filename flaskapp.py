import os
from flask import Flask, request, jsonify, Response
import requests
import json
from loguru import logger
import yaml

from public_cache import PublicCache
from regularize import regularize
from sheet_parser import SheetParser

app = Flask(__name__)

mimetypes = {
        '.html': 'text/html',
        '.xhtml': 'text/xhtml+xml',
        '.txt': 'text/plain',
        '.csv': 'text/csv',
        '.css': 'text/css',
        '.js': 'text/javascript',
        '.xml': 'text/xml',
        '.yaml': 'text/yaml',
        '.json': 'text/json',
        '.png': 'image/png',
        '.jpeg': 'image/jpeg',
        '.pdf': 'application/pdf',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}

def get_mimetype(xid: str) -> str:
    if xid == None : return None
    ext = os.path.splitext(xid)
    if ext == None or len(ext) < 2: return None
    return mimetypes.get(ext[1])

def fetch(url: str) -> [bytes, int]:
    try:
        resp = requests.get(url, verify=False)
        return resp.content, resp.status_code
    except Exception as ex:
        #logger.error(f"Exception: {ex}")
        return f"{ex}".encode(), 501


# for auto-deploy support
#from webhook import webhook
#app.config['GITHUB_SECRET'] = os.environ.get('GITHUB_SECRET')
#app.config['REPO_PATH'] = os.environ.get('REPO_PATH')
#app.register_blueprint(webhook)

# -- public cache
g_public_cache = PublicCache("/home/josh/public-cache")
#g_public_cache = PublicCache("c:\\temp\\public-cache")

@app.route("/cache", methods=["GET"])
@app.route("/cache/", methods=["GET"])
def cache_list():
    try:

        owner = request.args.get("owner")    

        full = request.args.get("full")
        items = g_public_cache.list_items()    

        if owner != None:
            items = [x for x in items if x["owner"] == owner]

        if full != "1": 
            items = [x["id"] for x in items]
        elif owner == None: 
            raise Exception("Must provide owner if full=1")


        return jsonify(items), 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return str(ex), 500

@app.route("/cache/meta-data/<xid>", methods=["GET"])
def cache_get_meta(xid: str):
    try:
        x = g_public_cache.load_meta(xid)
        if x == None: return "", 404
        return jsonify(x), 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return "", 500

@app.route("/cache/<xid>", methods=["GET"])
def cache_get(xid: str):
    try:
        x = g_public_cache.load(xid)
        if x == None: return "Missing File", 404
        mimetype = get_mimetype(xid)
        if mimetype == None: return "Invalid FileType", 415
        return Response(x, mimetype=mimetype, status=200)
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return "", 500

@app.route("/cache/<xid>", methods=["POST"])
def cache_post(xid: str):

    mimetype = get_mimetype(xid)
    if mimetype == None: return "Invalid FileType", 415

    if request.content_length > 10_000_000: return "Too Large", 413

    mimetype = get_mimetype(xid)
    if mimetype == None: return "Invalid FileType", 415

    owner = request.args.get("owner")    
    if owner == None: return "Missing owner", 401

    content = request.get_data()
    try:
        g_public_cache.save(content, xid, owner)
        return "", 200
    except Exception as ex:
        logger.error(f"Exception: {ex}")
        return "Internal Error", 500

@app.route("/cache/<xid>", methods=["DELETE"])
def cache_delete(xid: str):
    owner = request.args.get("owner")    
    if owner == None: return "Missing owner", 401

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

@app.route("/config/urlwatch/urls.yaml", methods=["GET"])
def config_urls_yaml():

    repo_url = "https://github.com/COVID19Tracking/covid-tracking/blob/master"
    yaml_url = get_rawcontent_url(repo_url, "urls.yaml")
    logger.info(f"fetch from {yaml_url}")
    x, status = fetch(yaml_url)
    return Response(x, mimetype = "text\\yaml", status=status)

@app.route("/config/urlwatch/urls.json", methods=["GET"])
def config_urls_json():

    repo_url = "https://github.com/COVID19Tracking/covid-tracking/blob/master"
    yaml_url = get_rawcontent_url(repo_url, "urls.yaml")
    logger.info(f"fetch from {yaml_url}")
    content, status = fetch(yaml_url)
    if status >= 300: return content, status

    items = yaml.load_all(content.decode(), Loader=yaml.FullLoader)
    
    result = [x for x in items]
    return jsonify(result), 200

@app.route("/config/google", methods=["GET"])
@app.route("/config/google/", methods=["GET"])
def config_google():

    main_sheet = "https://docs.google.com/spreadsheets/d/18oVRrHj3c183mHmq3m89_163yuYltLNlOmPerQ18E8w/htmlview?sle=true"
    logger.info(f"fetch from {main_sheet}")
    content, status = fetch(main_sheet)
    if status >= 300: return content, status

    parser = SheetParser()
    x = parser.get_menu(content)
    return jsonify(x), 200

@app.route("/config/google/states", methods=["GET"])
def config_google_states():

    main_sheet = "https://docs.google.com/spreadsheets/d/18oVRrHj3c183mHmq3m89_163yuYltLNlOmPerQ18E8w/htmlview?sle=true"
    logger.info(f"fetch from {main_sheet}")
    content, status = fetch(main_sheet)
    if status >= 300: return content, status

    parser = SheetParser()
    x = parser.get_config(content, "States")
    return jsonify(x), 200

@app.route("/config/google/current", methods=["GET"])
def config_google_current():

    main_sheet = "https://docs.google.com/spreadsheets/d/18oVRrHj3c183mHmq3m89_163yuYltLNlOmPerQ18E8w/htmlview?sle=true"
    logger.info(f"fetch from {main_sheet}")
    content, status = fetch(main_sheet)
    if status >= 300: return content, status

    parser = SheetParser()
    x = parser.get_config(content, "States current")
    return jsonify(x), 200


# -- github data view:

@app.route("/github-data/", methods=["GET"])
@app.route("/github-data/<path:dest>", methods=["GET"])
def github_preview(dest: str):
    try:
        if dest == "/": return "", 200

        mimetype = get_mimetype(dest)
        if mimetype == None: return "Invalid FileType", 415

        repo_url = "https://github.com/joshuaellinger/corona19-data-archive/blob/master"
        preview_url = get_rawcontent_url(repo_url, dest)

        logger.info(f"fetch from {preview_url}")
        content,  status = fetch(preview_url)
        if status >= 300: return content, status
        logger.info(f"return content as mimetype={mimetype}")

        return Response(content, mimetype=mimetype, status=status)
    except Exception as ex:
        logger.exception(ex)
        return f"Flask Error: {ex}", 500

# -- initial proxy code

@app.route("/proxy-raw/", methods=["GET"])
@app.route("/proxy-raw/<path:dest>", methods=["GET"])
def proxy_raw(dest: str):
    if dest == None or dest == "":
        return "", 200

    mimetype = get_mimetype(dest)
    if mimetype == None: return "Invalid FileType", 415

    url = f"https://{dest}"
    content, status = fetch(url)
    if status >= 300: return content, status
    return Response(content, mimetype=mimetype, status=status)
    
@app.route("/proxy/", methods=["GET"])
@app.route("/proxy/<path:dest>", methods=["GET"])
def proxy(dest: str):
    if dest == None or dest == "":
        return "", 200

    mimetype = get_mimetype(dest)
    if mimetype == None: return "Invalid FileType", 415

    url = f"https://{dest}"
    content, status = fetch(url)
    if status >= 300: return content, status
    if content != None:
        content = regularize(content)
    return Response(content, mimetype=mimetype, status=status)
    
@app.route("/", methods=["GET"])
def index():
    return Response(
        b"<html>body><h3>COVID19 urlwatch-proxies v0.06</h3></html></body>",
        mimetype="text/html", status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
