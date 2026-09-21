from demo_app.app import create_app


def test_health_endpoint_reports_ok() -> None:
    client = create_app().test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_index_identifies_service() -> None:
    client = create_app().test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json["service"] == "devsecops-demo"
