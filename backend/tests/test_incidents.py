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
