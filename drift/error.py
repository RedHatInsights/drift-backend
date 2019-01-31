from flask import current_app, jsonify


def handle_http_error(error):
    json_response = jsonify({'message': error.message})
    response = current_app.make_response(json_response)
    response.status_code = error.status_code
    return response
