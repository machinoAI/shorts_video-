from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

BASE_DIR = Path(__file__).resolve().parent
CLIENT_FILE = BASE_DIR / "client_secrets.json"
TOKEN_FILE = BASE_DIR / "youtube_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube",
]

if not CLIENT_FILE.exists():
    raise FileNotFoundError(f"Missing credentials: {CLIENT_FILE}")

print("Starting YouTube OAuth authorization...")

flow = InstalledAppFlow.from_client_secrets_file(
    str(CLIENT_FILE), scopes=SCOPES
)

creds = flow.run_local_server(
    port=0,
    access_type="offline",
    prompt="consent"
)

if not creds.refresh_token:
    raise RuntimeError("No refresh token returned by Google")

creds.refresh(Request())

TOKEN_FILE.write_text(creds.to_json())
TOKEN_FILE.chmod(0o600)

print("SUCCESS: YouTube token generated and verified!")
print(f"Saved to: {TOKEN_FILE}")
