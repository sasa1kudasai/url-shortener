import pytest


@pytest.mark.asyncio
async def test_create_short_url(client):
    response = await client.post("/shorten", json={"long_url": "https://example.com"})

    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert data["long_url"] == "https://example.com/"
    assert data["click_count"] == 0


@pytest.mark.asyncio
async def test_deduplication(client):
    response1 = await client.post("/shorten", json={"long_url": "https://example.com"})
    response2 = await client.post("/shorten", json={"long_url": "https://example.com"})

    assert response1.json()["short_code"] == response2.json()["short_code"]


@pytest.mark.asyncio
async def test_redirect_to_long_url(client):
    create_response = await client.post("/shorten", json={"long_url": "https://example.com"})
    code = create_response.json()["short_code"]

    redirect_response = await client.get(f"/{code}", follow_redirects=False)

    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/"


@pytest.mark.asyncio
async def test_redirect_nonexistent_code_returns_404(client):
    response = await client.get("/doesnotexist")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_shorten_invalid_url_returns_422(client):
    response = await client.post("/shorten", json={"long_url": "not-a-valid-url"})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_short_url_with_authenticated_user(client):
    register_response = await client.post("/auth/register", json={
        "email": "owner@example.com",
        "password": "strongpassword123"
    })
    user_id = register_response.json()["id"]

    login_response = await client.post("/auth/login", json={
        "email": "owner@example.com",
        "password": "strongpassword123"
    })
    token = login_response.json()["access_token"]

    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/owned"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["owner_id"] == user_id


@pytest.mark.asyncio
async def test_deduplication_scoped_per_owner(client):
    register_response = await client.post("/auth/register", json={
        "email": "owner2@example.com",
        "password": "strongpassword123"
    })
    user_id = register_response.json()["id"]

    login_response = await client.post("/auth/login", json={
        "email": "owner2@example.com",
        "password": "strongpassword123"
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    anon_response = await client.post("/shorten", json={"long_url": "https://example.com/shared"})
    owned_response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/shared"},
        headers=headers,
    )
    owned_response_again = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/shared"},
        headers=headers,
    )

    assert anon_response.json()["owner_id"] is None
    assert owned_response.json()["owner_id"] == user_id
    assert owned_response.json()["short_code"] != anon_response.json()["short_code"]
    assert owned_response.json()["short_code"] == owned_response_again.json()["short_code"]