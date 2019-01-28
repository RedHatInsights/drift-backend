import os

from drift.app import create_app

drift_debug = os.getenv('DRIFT_DEBUG')

create_app().run(host='0.0.0.0', port=8080, debug=drift_debug)
