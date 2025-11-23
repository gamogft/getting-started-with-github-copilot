import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

import src.app as app_module


client = TestClient(app_module.app)
ORIGINAL = copy.deepcopy(app_module.activities)


def reset_activities():
    # Helper to reset in-memory data between tests
    app_module.activities = copy.deepcopy(ORIGINAL)


def test_get_activities():
    reset_activities()
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert set(data.keys()) == set(ORIGINAL.keys())


def test_signup_and_unregister_flow():
    reset_activities()
    activity = next(iter(ORIGINAL.keys()))
    email = "testuser@example.com"

    # Signup
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 200

    data = client.get("/activities").json()
    assert email in data[activity]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 200

    data = client.get("/activities").json()
    assert email not in data[activity]["participants"]


def test_double_signup_raises_400():
    reset_activities()
    activity = next(iter(ORIGINAL.keys()))
    email = "dup@example.com"

    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 200

    resp2 = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp2.status_code == 400


def test_unregister_not_signed_returns_400():
    reset_activities()
    activity = next(iter(ORIGINAL.keys()))
    email = "not-signed@example.com"

    resp = client.delete(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 400
