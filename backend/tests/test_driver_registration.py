def test_driver_registration_requires_profile_fields(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "driver@test.com",
        "password": "testpass123",
        "role": "driver",
    })
    assert res.status_code == 400
    assert "required" in res.json()["detail"].lower()


def test_driver_registration_rejects_partial_profile(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "driver@test.com",
        "password": "testpass123",
        "role": "driver",
        "full_name": "Ramesh Das",
        "phone": "9800000000",
        # license_number and vehicle_number missing
    })
    assert res.status_code == 400


def test_user_registration_does_not_require_driver_profile_fields(client):
    # role="user" (the default) must not be affected by the driver-only check
    res = client.post("/api/v1/auth/register", json={
        "email": "user@test.com",
        "password": "testpass123",
    })
    # No Supabase credentials configured in the test environment -- the
    # driver-profile validation must NOT be what fails this request.
    assert res.status_code == 503
    assert "service role key" in res.json()["detail"].lower()
