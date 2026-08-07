import sqlite3

import pytest

from app.database import supabase, _SQLITE_DB_PATH


async def test_insert_and_select_round_trip():
    result = await supabase.table("users").insert(
        {"phone": "+19999999001", "name": "DB Test User", "preferred_language": "en"}
    ).execute()
    assert len(result.data) == 1
    user = result.data[0]
    assert user["name"] == "DB Test User"
    assert "id" in user
    assert "created_at" in user

    fetched = await supabase.table("users").select("*").eq("id", user["id"]).execute()
    assert fetched.data[0]["phone"] == "+19999999001"


async def test_update_and_delete():
    inserted = await supabase.table("users").insert(
        {"phone": "+19999999002", "name": "Before Update"}
    ).execute()
    user_id = inserted.data[0]["id"]

    await supabase.table("users").update({"name": "After Update"}).eq("id", user_id).execute()
    fetched = await supabase.table("users").select("*").eq("id", user_id).execute()
    assert fetched.data[0]["name"] == "After Update"

    await supabase.table("users").delete().eq("id", user_id).execute()
    fetched_after_delete = await supabase.table("users").select("*").eq("id", user_id).execute()
    assert fetched_after_delete.data == []


async def test_progress_insert_does_not_require_created_at():
    """
    Regression test: `progress` has no `created_at` column (it tracks
    `updated_at` instead). _do_insert() used to stamp `created_at`
    unconditionally on every insert, which broke every progress-score write.
    """
    result = await supabase.table("progress").insert(
        {"user_id": "regression-test-user", "skill": "fluency", "score": 42, "trend": 0}
    ).execute()
    assert result.data[0]["score"] == 42
    assert "updated_at" in result.data[0]


async def test_json_and_bool_fields_round_trip():
    result = await supabase.table("credentials").insert(
        {
            "user_id": "json-test-user",
            "certificate_id": "CERT-TEST-001",
            "skills": ["speaking", "grammar"],
            "verified": True,
        }
    ).execute()
    row = result.data[0]
    assert row["skills"] == ["speaking", "grammar"]
    assert row["verified"] is True


def test_indexes_exist_on_hot_query_columns():
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    try:
        names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'")}
    finally:
        conn.close()
    for expected in (
        "idx_conversations_user_created",
        "idx_interviews_user_created",
        "idx_progress_user_skill",
    ):
        assert expected in names


def test_conversations_query_uses_index_not_full_scan():
    conn = sqlite3.connect(_SQLITE_DB_PATH)
    try:
        plan = conn.execute(
            "EXPLAIN QUERY PLAN SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC",
            ("someone",),
        ).fetchall()
    finally:
        conn.close()
    plan_text = " ".join(row[-1] for row in plan)
    assert "idx_conversations_user_created" in plan_text
    assert "SCAN" not in plan_text
