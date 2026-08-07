def test_start_conversation_returns_session(client, signup):
    headers, _ = signup()
    resp = client.post("/conversation/start", json={"language": "en"}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["language"] == "en"
    assert "session_id" in body


def test_respond_requires_a_valid_session(client, signup):
    headers, _ = signup()
    resp = client.post(
        "/conversation/respond",
        json={"session_id": "does-not-exist", "user_message": "hi"},
        headers=headers,
    )
    assert resp.status_code == 404


def test_respond_returns_ai_reply_and_feedback(client, signup):
    headers, _ = signup()
    session = client.post("/conversation/start", json={"language": "en"}, headers=headers).json()

    resp = client.post(
        "/conversation/respond",
        json={"session_id": session["session_id"], "user_message": "Hello, I want to practice."},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ai_response"]
    assert body["conversation_id"]
    assert body["turn_number"] == 1


def test_history_is_paginated_and_scoped_to_the_user(client, signup):
    headers, _ = signup()
    session = client.post("/conversation/start", json={"language": "en"}, headers=headers).json()
    client.post(
        "/conversation/respond",
        json={"session_id": session["session_id"], "user_message": "First message"},
        headers=headers,
    )

    resp = client.get("/conversation/history?page=1", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"]["page"] == 1
    assert body["pagination"]["total"] >= 1
    assert all("user_message" in c for c in body["conversations"])


def test_history_does_not_leak_across_users(client, signup):
    headers_a, _ = signup(name="User A")
    headers_b, _ = signup(name="User B")

    session = client.post("/conversation/start", json={"language": "en"}, headers=headers_a).json()
    client.post(
        "/conversation/respond",
        json={"session_id": session["session_id"], "user_message": "User A's private message"},
        headers=headers_a,
    )

    resp = client.get("/conversation/history", headers=headers_b)
    messages = [c["user_message"] for c in resp.json()["conversations"]]
    assert "User A's private message" not in messages


def test_delete_conversation_requires_ownership(client, signup):
    headers_a, _ = signup(name="Owner")
    headers_b, _ = signup(name="Intruder")

    session = client.post("/conversation/start", json={"language": "en"}, headers=headers_a).json()
    respond = client.post(
        "/conversation/respond",
        json={"session_id": session["session_id"], "user_message": "hello"},
        headers=headers_a,
    ).json()

    resp = client.delete(f"/conversation/{respond['conversation_id']}", headers=headers_b)
    assert resp.status_code == 404
