import pytest



@pytest.mark.asyncio
async def test_register_user(client):
    responce = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword123"})

    assert responce.status_code == 200
    data = responce.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client):
    await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword123"
    })

    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "anotherpassword456"
    })

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword123"
    })

    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "strongpassword123"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_fails(client):
    await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "strongpassword123"
    })

    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_email_fails(client):
    response = await client.post("/auth/login", json={
        "email": "doesnotexist@example.com",
        "password": "whatever123"
    })

    assert response.status_code == 401

