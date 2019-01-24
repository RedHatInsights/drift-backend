from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PHONY_DATA = {'packages': [{'name': 'gcc',
                            'status': 'SAME',
                            'hosts': [{'host1.example.com': '8.2.1-6.fc29.x86_64'},
                                      {'host2.example.com': '8.2.1-6.fc29.x86_64'}]},
                           {'name': 'gcc-c++',
                            'status': 'SAME',
                            'hosts': [{'host1.example.com': '8.2.1-6.fc29.x86_64'},
                                      {'host2.example.com': '8.2.1-6.fc29.x86_64'}]},
                           {'name': 'gcc-gdb-plugin',
                            'status': 'SAME',
                            'hosts': [{'host1.example.com': '8.2.1-6.fc29.x86_64'},
                                      {'host2.example.com': '8.2.1-6.fc29.x86_64'}]},
                           {'name': 'robert_burns',
                            'status': 'UNKNOWN',
                            'hosts': [{'host1.example.com': '1.0-1.el99.noarch'},
                                      {'host2.example.com': None}]},
                           ],
              'facts': [{'name': 'uname.release',
                         'status': 'DIFF',
                         'hosts': [{'host1.example.com': '4.19.10-300.fc29.x86_64'},
                                   {'host2.example.com': '4.19.9-300.fc29.x86_64'}]},
                        {'name': 'lscpu.socket(s)',
                         'status': 'SAME',
                         'hosts': [{'host1.example.com': '1'}, {'host2.example.com': '1'}]}]}


@app.route("/r/insights/platform/drift/compare")
def compare():
    return jsonify(PHONY_DATA)


@app.route("/r/insights/platform/drift/status")
def status():
    return jsonify({'status': "running"})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
