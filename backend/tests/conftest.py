import os
import tempfile
import uuid

import pytest

# Settings() is instantiated at import time in app/config.py and several
# fields have no default, so every required env var must be set before
# anything under `app` (or `main`) is imported — including by other test
# files, since conftest.py is guaranteed to run first.
_DB_FD, _DB_PATH = tempfile.mkstemp(suffix=".db")
os.close(_DB_FD)
os.environ["VANI_DB_PATH"] = _DB_PATH

os.environ.setdefault("SUPABASE_URL", "http://127.0.0.1:1")
os.environ.setdefault("SUPABASE_KEY", "test-key")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")
# Deliberately not a "gsk_" or "sk-or-" prefixed key, so LLMService stays in
# mock mode — tests must not depend on a real network call succeeding.
os.environ.setdefault("GROQ_API_KEY", "test-key-mock-mode")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-tests-only")
os.environ.setdefault("TWILIO_ACCOUNT_SID", "test-sid")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test-token")
os.environ.setdefault("TWILIO_SMS_FROM", "+10000000000")
os.environ.setdefault("R2_ACCOUNT_ID", "test-account")
os.environ.setdefault("R2_ACCESS_KEY_ID", "test-access-key")
os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test-secret-key")
os.environ.setdefault("R2_ENDPOINT", "http://127.0.0.1:1")
os.environ.setdefault("SOLANA_WALLET_PRIVATE_KEY", "test-private-key")
os.environ.setdefault("APP_ENV", "development")
# Deliberately unreachable so the cache always falls back to SimpleCache —
# tests shouldn't depend on a Redis instance being available in CI.
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:1")

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402
from app.rate_limiter import limiter  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Each test gets a fresh rate-limit budget instead of sharing one across the whole session."""
    limiter.reset()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _random_phone():
    return "9" + str(uuid.uuid4().int)[:9]


@pytest.fixture
def unique_phone():
    return _random_phone()


@pytest.fixture
def signup(client):
    """Runs the real OTP send/verify flow and returns (headers, user) for an authenticated user.

    Generates a fresh phone number per call (not per test) so that calling
    signup() twice in one test produces two distinct users.
    """
    def _signup(name="Test User", phone=None):
        phone = phone or _random_phone()
        send_resp = client.post("/auth/otp/send", json={"phone": phone})
        assert send_resp.status_code == 200, send_resp.text
        otp = send_resp.json()["dev_otp"]

        verify_resp = client.post(
            "/auth/otp/verify",
            json={"phone": phone, "otp": otp, "name": name},
        )
        assert verify_resp.status_code == 200, verify_resp.text
        body = verify_resp.json()
        headers = {"Authorization": f"Bearer {body['access_token']}"}
        return headers, body["user"]

    return _signup
