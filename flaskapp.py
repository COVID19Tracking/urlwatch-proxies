import os
from flask import Flask


app = Flask(__name__)

# for auto-deploy support
#from webhook import webhook
#app.config['GITHUB_SECRET'] = os.environ.get('GITHUB_SECRET')
#app.config['REPO_PATH'] = os.environ.get('REPO_PATH')
#app.register_blueprint(webhook)

@app.route("/proxy/<path:dest>")
def proxy(dest: str):
    return f"<h3>proxy {dest}"

@app.route("/")
def index():
    return "<h3>COVID19 urlwatch-proxies v0.05</h3>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')