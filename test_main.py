import os

os.environ["DB_PATH"] = "test_tasks.db"

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    assert client.get("/").json() == {"status": "ok"}


def test_crud_flow():
    r = client.post("/tasks", json={"title": "Learn cloud"})
    assert r.status_code == 201
    task_id = r.json()["id"]

    assert client.get(f"/tasks/{task_id}").json()["title"] == "Learn cloud"

    r = client.put(f"/tasks/{task_id}", json={"title": "Learn cloud", "done": True})
    assert r.json()["done"] is True

    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404
