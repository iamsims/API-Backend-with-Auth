import json
from datetime import datetime
from typing import Dict, Any

import google.oauth2.credentials


def credentials_to_dict(credentials) -> Dict[str, Any]:
    return json.loads(credentials.to_json())


def dict_to_credentials(credentials_dict):
    credentials = google.oauth2.credentials.Credentials(**credentials_dict)
    credentials.expiry = datetime.strptime(credentials.expiry, '%Y-%m-%dT%H:%M:%S.%fZ')
    return credentials
