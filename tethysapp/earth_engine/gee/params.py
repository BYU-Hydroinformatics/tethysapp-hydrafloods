import os
# from .app import EarthEngine as app
from .. import app

dirname = os.path.dirname(__file__)

service_account = app.EarthEngine.get_custom_setting('service_account')  # your google service account
private_key = app.EarthEngine.get_custom_setting('path_to_json_key') # path to the json private key for the service account