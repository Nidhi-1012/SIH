def test_incident_with_photo_url_is_stored(client):
    small_base64_photo = "data:image/png;base64," + ("A" * 100)
    res = client.post("/api/v1/incidents", json={
        "incident_type": "Landslide",
        "severity": "High",
        "lat": 25.9, "lon": 91.88,
        "photo_url": small_base64_photo,
        "notes": "test",
    })
    assert res.status_code == 200
    assert res.json()["photo_url"] == small_base64_photo


def test_oversized_photo_is_rejected(client):
    oversized_base64_photo = "data:image/png;base64," + ("A" * 8_000_000)
    res = client.post("/api/v1/incidents", json={
        "incident_type": "Landslide",
        "severity": "High",
        "lat": 25.9, "lon": 91.88,
        "photo_url": oversized_base64_photo,
    })
    assert res.status_code == 413


def test_duplicate_client_report_id_does_not_create_a_second_incident(client):
    payload = {
        "incident_type": "Landslide", "severity": "High",
        "lat": 25.9, "lon": 91.88, "client_report_id": "client-uuid-123",
    }
    first = client.post("/api/v1/incidents", json=payload)
    second = client.post("/api/v1/incidents", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["incident_id"] == second.json()["incident_id"]

    all_incidents = client.get("/api/v1/incidents").json()
    matching = [i for i in all_incidents if i.get("client_report_id") == "client-uuid-123"]
    assert len(matching) == 1
