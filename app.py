from flask import Flask
app = Flask(__name__)


@app.route("/status")
def status():
    return "application is running"


if __name__ == "__main__":
    app.run()
