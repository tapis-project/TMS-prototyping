import os

TAPIS_TENANT_URL = os.environ.get("TAPIS_TENANT_URL", "https://portals.tapis.io")
TAPIS_OAUTH_CALLBACK_URL = os.environ.get(
    "TAPIS_OAUTH_CALLBACK_URL", "http://127.0.0.1:8000/oauth-callback"
)
TAPIS_OAUTH_CLIENT_ID = os.environ.get("TAPIS_OAUTH_CLIENT_ID", "DEV.TMS-PROTO")
TAPIS_OAUTH_CLIENT_KEY = os.environ.get("TAPIS_OAUTH_CLIENT_KEY")
DEV_ENV = os.environ.get("DEV_ENV", True)
MOCK_USER = os.environ.get("MOCK_USER", "mock")
