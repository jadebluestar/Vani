def test_otp_send_returns_dev_otp_in_development(client, unique_phone):
    resp = client.post("/auth/otp/send", json={"phone": unique_phone})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "dev_otp" in body
    assert len(body["dev_otp"]) == 6


def test_otp_verify_creates_new_user(client, unique_phone):
    otp = client.post("/auth/otp/send", json={"phone": unique_phone}).json()["dev_otp"]
    resp = client.post(
        "/auth/otp/verify",
        json={"phone": unique_phone, "otp": otp, "name": "Nayana"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["user"]["name"] == "Nayana"
    assert body["user"]["coins_balance"] == 100
    assert "access_token" in body


def test_otp_verify_rejects_wrong_code(client, unique_phone):
    client.post("/auth/otp/send", json={"phone": unique_phone})
    resp = client.post(
        "/auth/otp/verify",
        json={"phone": unique_phone, "otp": "000000"},
    )
    assert resp.status_code == 400


def test_otp_verify_rejects_missing_otp(client, unique_phone):
    resp = client.post(
        "/auth/otp/verify",
        json={"phone": unique_phone, "otp": "123456"},
    )
    assert resp.status_code == 400
    assert "expired" in resp.json()["detail"].lower()


def test_otp_verify_is_idempotent_on_returning_user(client, unique_phone):
    otp1 = client.post("/auth/otp/send", json={"phone": unique_phone}).json()["dev_otp"]
    first = client.post(
        "/auth/otp/verify", json={"phone": unique_phone, "otp": otp1, "name": "Nayana"}
    ).json()

    otp2 = client.post("/auth/otp/send", json={"phone": unique_phone}).json()["dev_otp"]
    second = client.post(
        "/auth/otp/verify", json={"phone": unique_phone, "otp": otp2, "name": "Someone Else"}
    ).json()

    assert first["user"]["id"] == second["user"]["id"]
    assert second["user"]["name"] == "Nayana"  # existing user record wins, not the new name


def test_otp_send_rate_limited_per_phone_after_three_requests(client, unique_phone):
    # send_otp enforces two independent limits: a per-IP slowapi limit
    # (5/minute) and a per-phone counter (max 3 attempts / 10 minutes,
    # tracked in the cache). The per-phone counter is stricter and fires
    # first for repeated requests to the same number.
    for _ in range(3):
        resp = client.post("/auth/otp/send", json={"phone": unique_phone})
        assert resp.status_code == 200
    resp = client.post("/auth/otp/send", json={"phone": unique_phone})
    assert resp.status_code == 429


def test_otp_send_rate_limited_per_ip_across_different_phones(client):
    # The slowapi 5/minute limit is keyed by IP, not phone, so five
    # requests to five *different* numbers should still trip it.
    for _ in range(5):
        resp = client.post("/auth/otp/send", json={"phone": _make_unused_phone()})
        assert resp.status_code == 200
    resp = client.post("/auth/otp/send", json={"phone": _make_unused_phone()})
    assert resp.status_code == 429


def _make_unused_phone():
    import uuid
    return "9" + str(uuid.uuid4().int)[:9]


def test_me_requires_auth(client):
    resp = client.get("/auth/me")
    assert resp.status_code in (401, 403)


def test_me_returns_current_user(client, signup):
    headers, user = signup(name="Ravi")
    resp = client.get("/auth/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["user"]["id"] == user["id"]


def test_invalid_token_rejected(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401
