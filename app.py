from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PHONY_DATA = {'packages': [{'name': 'gcc',
                            'status': 'SAME',
                            'hosts': ['8.2.1-6.fc29.x86_64', '8.2.1-6.fc29.x86_64']},
                           {'name': 'gcc-c++',
                            'status': 'SAME',
                            'hosts': ['8.2.1-6.fc29.x86_64', '8.2.1-6.fc29.x86_64']},
                           {'name': 'gcc-gdb-plugin',
                            'status': 'SAME',
                            'hosts': ['8.2.1-6.fc29.x86_64', '8.2.1-6.fc29.x86_64']},
                           {'name': 'robert_burns',
                            'status': 'UNKNOWN',
                            'hosts': ['1.0-0.el99.noarch', None]},
                           ],
              'metadata': {'hosts': ['host1.example.com', 'host2.example.com']},
              'facts': [{'name': 'uname.release',
                         'status': 'DIFF',
                         'hosts': ['4.19.10-300.fc29.x86_64', '4.19.9-300.fc29.x86_64']},
                        {'name': 'lscpu.socket(s)',
                         'status': 'SAME',
                         'hosts': ['1', '1']}]}


@app.route("/compare")
def compare():
    return jsonify(PHONY_DATA)


@app.route("/status")
def status():
    return jsonify({'status': "running"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
