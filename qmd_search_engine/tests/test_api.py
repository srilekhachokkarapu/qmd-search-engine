
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "Running successfully"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_documents():
    response = client.get("/documents")

    assert response.status_code == 200

    data = response.json()

    assert "documents" in data
    assert len(data["documents"]) == 3


def test_collections():
    response = client.get("/collections")

    assert response.status_code == 200

    data = response.json()

    assert data["total_collections"] == 3


def test_keyword_search():
    response = client.post(
        "/search",
        json={
            "query": "supervised learning",
            "mode": "keyword",
            "top_k": 5
        }
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "keyword"


def test_semantic_search():
    response = client.post(
        "/search",
        json={
            "query": "How does supervised learning work?",
            "mode": "semantic",
            "top_k": 5
        }
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "semantic"


def test_hybrid_search():
    response = client.post(
        "/search",
        json={
            "query": "How does supervised learning work?",
            "mode": "hybrid",
            "top_k": 5
        }
    )

    assert response.status_code == 200
    assert response.json()["mode"] == "hybrid"


def test_collection_filter():
    response = client.post(
        "/search",
        json={
            "query": "drug information",
            "mode": "hybrid",
            "top_k": 5,
            "collection": "medical"
        }
    )

    assert response.status_code == 200

    results = response.json()["results"]

    assert all(
        result["collection"] == "medical"
        for result in results
    )


def test_invalid_search_mode():
    response = client.post(
        "/search",
        json={
            "query": "Python",
            "mode": "invalid",
            "top_k": 5
        }
    )

    assert response.status_code == 422


def test_missing_document():
    response = client.get(
        "/documents/not-a-real-document-id"
    )

    assert response.status_code == 404
