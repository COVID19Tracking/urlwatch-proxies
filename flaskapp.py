import os
from flask import Flask
import requests

from regularize import regularize

app = Flask(__name__)

# for auto-deploy support
#from webhook import webhook
#app.config['GITHUB_SECRET'] = os.environ.get('GITHUB_SECRET')
#app.config['REPO_PATH'] = os.environ.get('REPO_PATH')
#app.register_blueprint(webhook)

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