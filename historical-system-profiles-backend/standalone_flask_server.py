import os

from historical_system_profiles.app import create_app


port = os.getenv("PORT", 8080)

create_app().run(host="0.0.0.0", port=port)
