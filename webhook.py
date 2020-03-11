import os
import sys
from loguru import logger 
import hmac
from flask import request, Blueprint, jsonify, current_app, make_response
from git import Repo

webhook = Blueprint('webhook', __name__, url_prefix='')

g_log_path = "/tmp/github_hook.log"
logger.add(g_log_path, level="INFO")
logger.add(sys.stderr, level="ERROR")

@webhook.route('/log-file', methods=['GET']) 
def log_file():
    """ display log file """

    if not os.path.exists(g_log_path):
        with open(g_log_path, "r") as f:
            response = make_response(f, 200)
    else:
        response = make_response("", 200)

    response.mimetype = "text/plain"
    return response     
    

@webhook.route('/github', methods=['POST']) 
def github_hook(): 
    """ handle callback from github """

    signature = request.headers.get('X-Hub-Signature') 
    sha, signature = signature.split('=')

    secret = current_app.config.get('GITHUB_SECRET')
    if secret == None:
        logger.error("Missing GITHUB_SECRET config variable")
        return jsonify("Missing GITHUB_SECRET"), 500

    repo_path = current_app.config.get('REPO_PATH')
    if repo_path == None:
        logger.error("Missing REPO_PATH config variable")
        return jsonify("Missing REPO_PATH"), 500

    secret = str.encode(secret)

    hashhex = hmac.new(secret, request.data, digestmod='sha1').hexdigest()
    if hmac.compare_digest(hashhex, signature): 
        logger.info(f"pull {repo_path}")
        repo = Repo(repo_path) 
        origin = repo.remotes.origin 
        origin.pull('--rebase')

    commit = request.json['after'][0:6]
    logger.info(f"Repository updated with commit {commit}")
    return jsonify({}), 200