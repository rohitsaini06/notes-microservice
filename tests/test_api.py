import pytest
from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_state():
    main.notes.clear()
    main._next_id = 1


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_get_note():
    r = client.post("/notes", json={"title": "Hello", "content": "World"})
    assert r.status_code == 201
    note_id = r.json()["id"]
    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200
    assert r.json()["title"] == "Hello"


def test_list_notes():
    client.post("/notes", json={"title": "A"})
    client.post("/notes", json={"title": "B"})
    r = client.get("/notes")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_get_missing_note_returns_404():
    assert client.get("/notes/999").status_code == 404


def test_create_note_validation_error():
    r = client.post("/notes", json={"title": ""})
    assert r.status_code == 422


def test_delete_note():
    note_id = client.post("/notes", json={"title": "temp"}).json()["id"]
    assert client.delete(f"/notes/{note_id}").status_code == 204
    assert client.get(f"/notes/{note_id}").status_code == 404


def test_whoami_has_hostname():
    r = client.get("/whoami")
    assert r.status_code == 200
    assert "hostname" in r.json()
