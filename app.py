from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)


@app.route("/status")
def status():
    return "application is running"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
