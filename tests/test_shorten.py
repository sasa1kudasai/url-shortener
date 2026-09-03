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


@pytest.mark.asyncio
async def test_qr_code_returns_png(client):
    create_response = await client.post("/shorten", json={"long_url": "https://example.com"})
    code = create_response.json()["short_code"]

    response = await client.get(f"/{code}/qr")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_qr_code_nonexistent_code_returns_404(client):
    response = await client.get("/doesnotexist/qr")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_short_url_with_empty_alias_is_random(client):
    response = await client.post("/shorten", json={"long_url": "https://example.com", "custom_alias": ""})

    assert response.status_code == 200
    data = response.json()
    assert "short_code" in data
    assert data["short_code"] != ""


@pytest.mark.asyncio
async def test_custom_alias_requires_auth(client):
    response = await client.post("/shorten", json={"long_url": "https://example.com", "custom_alias": "myalias"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_custom_alias_success(client, auth_headers):
    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/custom", "custom_alias": "mycustom"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["short_code"] == "mycustom"


@pytest.mark.asyncio
async def test_custom_alias_reserved_rejected(client, auth_headers):
    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/reserved", "custom_alias": "admin"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_custom_alias_already_taken(client, auth_headers):
    first = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/first", "custom_alias": "taken"},
        headers=auth_headers,
    )
    assert first.status_code == 200

    second = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/second", "custom_alias": "taken"},
        headers=auth_headers,
    )
    assert second.status_code == 400


@pytest.mark.asyncio
async def test_custom_alias_invalid_format_rejected(client, auth_headers):
    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/invalid", "custom_alias": "a"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_custom_alias_limit_reached(client, auth_headers):
    for i in range(5):
        response = await client.post(
            "/shorten",
            json={"long_url": f"https://example.com/{i}", "custom_alias": f"alias{i}"},
            headers=auth_headers,
        )
        assert response.status_code == 200

    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/6", "custom_alias": "alias6"},
        headers=auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_custom_alias_limit_ignores_entries_outside_window(client, auth_headers, db_session, monkeypatch):
    from datetime import datetime, timedelta, UTC
    from sqlalchemy import select
    from app.models import URL
    from app.config import settings

    monkeypatch.setattr(settings, "max_custom_aliases_per_user", 1)
    monkeypatch.setattr(settings, "custom_alias_limit_window_days", 30)

    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/old", "custom_alias": "oldalias"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    result = await db_session.execute(select(URL).where(URL.short_code == "oldalias"))
    url_obj = result.scalar_one()
    url_obj.created_at = datetime.now(UTC) - timedelta(days=40)
    await db_session.commit()

    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/new", "custom_alias": "newalias"},
        headers=auth_headers,
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_custom_alias_limit_without_window_counts_all_time(client, auth_headers, db_session, monkeypatch):
    from datetime import datetime, timedelta, UTC
    from sqlalchemy import select
    from app.models import URL
    from app.config import settings

    monkeypatch.setattr(settings, "max_custom_aliases_per_user", 1)
    monkeypatch.setattr(settings, "custom_alias_limit_window_days", None)

    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/old", "custom_alias": "oldalias2"},
        headers=auth_headers,
    )
    assert response.status_code == 200

    result = await db_session.execute(select(URL).where(URL.short_code == "oldalias2"))
    url_obj = result.scalar_one()
    url_obj.created_at = datetime.now(UTC) - timedelta(days=400)
    await db_session.commit()

    response = await client.post(
        "/shorten",
        json={"long_url": "https://example.com/new", "custom_alias": "newalias2"},
        headers=auth_headers,
    )
    assert response.status_code == 403