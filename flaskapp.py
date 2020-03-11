# application functionality for proxy

from flask import Flask
app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Hello World 2</h1>"

if __name__ == "__main__":
    app.run(host='0.0.0.0')