"""
Autonomous Credential & Environment Setup Utility
Prepares runtime credentials (.env, youtube_token.json, client_secrets.json)
safely in both local and CI (GitHub Actions) environments.
"""

import os
import sys
import json
import base64
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def decode_and_write_json(raw_val: str, target_path: Path, label: str) -> bool:
    if not raw_val:
        return False

    val = raw_val.strip().strip("\"'")
    if not val:
        return False

    # Check if raw value is already direct JSON
    if val.startswith("{"):
        try:
            parsed = json.loads(val)
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)
            print(f"✅ {label}: Successfully written from direct JSON ({target_path})")
            return True
        except Exception as e:
            print(f"⚠️ {label}: Detected direct JSON but failed to parse: {e}")

    # Attempt Base64 decode
    try:
        # Strip internal whitespace/newlines that might be introduced by shell/secrets UI
        cleaned = "".join(val.split())
        missing_padding = len(cleaned) % 4
        if missing_padding:
            cleaned += "=" * (4 - missing_padding)

        decoded_bytes = base64.b64decode(cleaned)
        decoded_str = decoded_bytes.decode("utf-8")
        parsed = json.loads(decoded_str)

        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)
        print(f"✅ {label}: Successfully decoded base64 JSON ({target_path})")
        return True
    except Exception as e:
        print(f"⚠️ {label}: Base64 decoding failed: {e}")

    # Fallback: attempt to write as raw text if it looks salvageable
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(val)
        print(f"⚠️ {label}: Written raw value to {target_path}")
        return True
    except Exception as e:
        print(f"❌ {label}: Failed to write credentials file: {e}")
        return False


def main():
    print("🔐 Setting up runtime credentials for Autonomous Video Generation...")

    # 1. YouTube OAuth Token & Client Secrets
    token_val = os.environ.get("YOUTUBE_TOKEN_JSON_BASE64") or os.environ.get("YOUTUBE_TOKEN_JSON") or ""
    client_val = os.environ.get("YOUTUBE_CLIENT_SECRETS_BASE64") or os.environ.get("YOUTUBE_CLIENT_SECRETS") or ""

    pipeline_dir = PROJECT_ROOT / "pipeline"
    pipeline_dir.mkdir(parents=True, exist_ok=True)

    token_path = pipeline_dir / "youtube_token.json"
    client_path = pipeline_dir / "client_secrets.json"

    if token_val:
        decode_and_write_json(token_val, token_path, "YouTube Token")
    elif token_path.exists():
        print(f"ℹ️ YouTube Token: Found existing file at {token_path}")
    else:
        print("⚠️ YouTube Token: Neither YOUTUBE_TOKEN_JSON_BASE64 nor local token file found.")

    if client_val:
        decode_and_write_json(client_val, client_path, "YouTube Client Secrets")
    elif client_path.exists():
        print(f"ℹ️ YouTube Client Secrets: Found existing file at {client_path}")
    else:
        print("⚠️ YouTube Client Secrets: Neither YOUTUBE_CLIENT_SECRETS_BASE64 nor local file found.")

    # 1.5 Live OAuth Validation
    if token_path.exists():
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            scopes = [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube"
            ]
            creds = Credentials.from_authorized_user_file(str(token_path), scopes)
            if not creds.valid and creds.expired and creds.refresh_token:
                print("🔄 Testing refresh of YouTube OAuth token...")
                creds.refresh(Request())
                with open(token_path, "w", encoding="utf-8") as f:
                    f.write(creds.to_json())
            print(f"✅ Verified YouTube OAuth token: Active & authenticated as client {getattr(creds, 'client_id', '')[:20]}...")
        except Exception as e:
            print(f"❌ YouTube Token Verification Error: {e}")
            if os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true":
                raise RuntimeError(f"Invalid YouTube token in CI environment: {e}")

    # 2. Configure .env file
    env_path = PROJECT_ROOT / ".env"
    existing_env = {}
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    existing_env[k.strip()] = v.strip()

    # Default brand values
    defaults = {
        "CHANNEL_NAME": os.environ.get("CHANNEL_NAME", "machinoAI"),
        "CHANNEL_HANDLE": os.environ.get("CHANNEL_HANDLE", "@machinoai-in"),
        "CHANNEL_URL": os.environ.get("CHANNEL_URL", "https://www.youtube.com/@machinoai-in"),
        "CHANNEL_WEBSITE": os.environ.get("CHANNEL_WEBSITE", "https://machinoai.in"),
        "CHANNEL_TAGLINE": os.environ.get("CHANNEL_TAGLINE", "Learn from research papers"),
        "GEMINI_MODEL_NAME": os.environ.get("GEMINI_MODEL_NAME", "gemini-flash-latest"),
        "TTS_PROVIDER": os.environ.get("TTS_PROVIDER", "kokoro"),
        "KOKORO_VOICE": os.environ.get("KOKORO_VOICE", "am_eric"),
    }

    passthrough_keys = [
        "GEMINI_API_KEY", "GROQ_API_KEY", "OPENROUTER_API_KEY",
        "ELEVENLABS_API_KEY", "SARVAM_API_KEY",
        "INSTAGRAM_ACCOUNT_ID", "INSTAGRAM_ACCESS_TOKEN",
        "TWITTER_API_KEY", "TWITTER_API_SECRET", "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_TOKEN_SECRET", "TWITTER_CLIENT_ID", "TWITTER_CLIENT_SECRET",
        "LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET", "LINKEDIN_ACCESS_TOKEN"
    ]

    for k in passthrough_keys:
        v = os.environ.get(k)
        if v:
            defaults[k] = v

    for k, v in defaults.items():
        if k not in existing_env or not existing_env[k]:
            existing_env[k] = v

    with open(env_path, "w", encoding="utf-8") as f:
        for k, v in sorted(existing_env.items()):
            f.write(f"{k}={v}\n")

    print(f"✅ Runtime .env configuration updated at {env_path}")
    print(f"   Channel: {existing_env.get('CHANNEL_NAME')} ({existing_env.get('CHANNEL_HANDLE')})")
    print(f"   TTS Provider: {existing_env.get('TTS_PROVIDER')} ({existing_env.get('KOKORO_VOICE')})")
    print(f"   LLM Model: {existing_env.get('GEMINI_MODEL_NAME')}")
    print("🚀 Credential setup completed successfully.")

if __name__ == "__main__":
    main()
