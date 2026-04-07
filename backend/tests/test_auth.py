"""
TC-01: Registration validation
TC-02: Unauthorized access (no token)
TC-03: Forbidden (wrong role)
"""
import pytest


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    """TC-01: Email sai format → 422."""
    res = await client.post("/auth/register", json={
        "email": "patient@.com",
        "password": "Password123",
        "full_name": "Test Patient",
    })
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_weak_password(client):
    """TC-01: Mật khẩu thiếu chữ hoa → 422."""
    res = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "abc12345",
        "full_name": "Test Patient",
    })
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_register_and_login_success(client):
    """Register then login returns token pair."""
    payload = {
        "email": "patient@example.com",
        "password": "Password123",
        "full_name": "Nguyen Van A",
        "role": "patient",
    }
    reg = await client.post("/auth/register", json=payload)
    assert reg.status_code == 201

    login = await client.post("/auth/login", json={
        "email": payload["email"],
        "password": payload["password"],
    })
    assert login.status_code == 200
    data = login.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    """TC-02: No token → 403 (HTTPBearer returns 403 on missing token)."""
    res = await client.get("/auth/me")
    assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_confirm_appointment_forbidden_for_patient(client):
    """TC-03: Patient JWT cannot access doctor-only endpoints → 403."""
    import uuid
    # Register and login as patient
    payload = {
        "email": "p@example.com",
        "password": "Password123",
        "full_name": "Patient One",
        "role": "patient",
    }
    await client.post("/auth/register", json=payload)
    login = await client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    token = login.json()["access_token"]

    fake_id = str(uuid.uuid4())
    res = await client.patch(
        f"/appointments/{fake_id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403
