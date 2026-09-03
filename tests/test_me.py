import pytest


async def register_and_login(client, email: str, password: str = "strongpassword123") -> dict:
    await client.post("/auth/register", json={"email": email, "password": password})
    response = await client.post("/auth/login", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_dashboard_requires_auth(client):
    response = await client.get("/me/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_dashboard_empty_for_new_user(client):
    headers = await register_and_login(client, "dash@example.com")

    response = await client.get("/me/dashboard", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["total_clicks"] == 0
    assert data["active_links"] == 0
    assert data["recent_links"] == []


@pytest.mark.asyncio
async def test_dashboard_counts_own_links(client):
    headers = await register_and_login(client, "dash2@example.com")

    await client.post("/shorten", json={"long_url": "https://example.com/one"}, headers=headers)
    await client.post("/shorten", json={"long_url": "https://example.com/two"}, headers=headers)

    response = await client.get("/me/dashboard", headers=headers)

    data = response.json()
    assert data["active_links"] == 2
    assert len(data["recent_links"]) == 2


@pytest.mark.asyncio
async def test_links_requires_auth(client):
    response = await client.get("/me/links")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_links_only_shows_own_links(client):
    headers_a = await register_and_login(client, "usera@example.com")
    headers_b = await register_and_login(client, "userb@example.com")

    await client.post("/shorten", json={"long_url": "https://example.com/mine"}, headers=headers_a)

    response = await client.get("/me/links", headers=headers_b)

    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_links_search_filters_by_url(client):
    headers = await register_and_login(client, "search@example.com")

    await client.post("/shorten", json={"long_url": "https://github.com/example"}, headers=headers)
    await client.post("/shorten", json={"long_url": "https://youtube.com/watch"}, headers=headers)

    response = await client.get("/me/links?search=github", headers=headers)

    data = response.json()
    assert data["total"] == 1
    assert "github.com" in data["items"][0]["long_url"]


@pytest.mark.asyncio
async def test_links_pagination(client):
    headers = await register_and_login(client, "pagination@example.com")

    for i in range(15):
        await client.post("/shorten", json={"long_url": f"https://example.com/page{i}"}, headers=headers)

    page1 = await client.get("/me/links?page=1&page_size=10", headers=headers)
    page2 = await client.get("/me/links?page=2&page_size=10", headers=headers)

    assert page1.json()["total"] == 15
    assert len(page1.json()["items"]) == 10
    assert page1.json()["total_pages"] == 2
    assert len(page2.json()["items"]) == 5