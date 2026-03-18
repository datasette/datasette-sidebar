from datasette.app import Datasette
import pytest

ALLOW_CONFIG = {"permissions": {"datasette-sidebar-access": True}}


def _ds(**kwargs):
    return Datasette(memory=True, config=ALLOW_CONFIG, **kwargs)


def _cookies(datasette):
    return {"ds_actor": datasette.sign({"a": {"id": "test-user"}}, "actor")}


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = _ds()
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-sidebar" in installed_plugins


@pytest.mark.asyncio
async def test_stars_api_requires_auth():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/sidebar/api/stars")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_stars_api_returns_empty():
    datasette = _ds()
    response = await datasette.client.get(
        "/-/sidebar/api/stars", cookies=_cookies(datasette)
    )
    assert response.status_code == 200
    assert response.json()["stars"] == []


@pytest.mark.asyncio
async def test_toggle_star_database():
    datasette = _ds()
    cookies = _cookies(datasette)

    # Star a database
    response = await datasette.client.post(
        "/-/sidebar/api/toggle-star",
        json={"star_type": "database", "database_name": "mydb"},
        cookies=cookies,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["starred"] is True
    assert data["star"]["database_name"] == "mydb"
    assert data["star"]["star_type"] == "database"

    # Verify it shows in stars list
    response = await datasette.client.get("/-/sidebar/api/stars", cookies=cookies)
    assert len(response.json()["stars"]) == 1

    # Toggle again to unstar
    response = await datasette.client.post(
        "/-/sidebar/api/toggle-star",
        json={"star_type": "database", "database_name": "mydb"},
        cookies=cookies,
    )
    assert response.status_code == 200
    assert response.json()["starred"] is False

    # Verify empty
    response = await datasette.client.get("/-/sidebar/api/stars", cookies=cookies)
    assert len(response.json()["stars"]) == 0


@pytest.mark.asyncio
async def test_toggle_star_table():
    datasette = _ds()
    cookies = _cookies(datasette)

    response = await datasette.client.post(
        "/-/sidebar/api/toggle-star",
        json={"star_type": "table", "database_name": "mydb", "table_name": "mytable"},
        cookies=cookies,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["starred"] is True
    assert data["star"]["table_name"] == "mytable"


@pytest.mark.asyncio
async def test_stars_filtered_by_database():
    datasette = _ds()
    cookies = _cookies(datasette)

    await datasette.client.post(
        "/-/sidebar/api/toggle-star",
        json={"star_type": "database", "database_name": "db1"},
        cookies=cookies,
    )
    await datasette.client.post(
        "/-/sidebar/api/toggle-star",
        json={"star_type": "table", "database_name": "db2", "table_name": "t1"},
        cookies=cookies,
    )

    # All stars
    response = await datasette.client.get("/-/sidebar/api/stars", cookies=cookies)
    assert len(response.json()["stars"]) == 2

    # Filtered to db1
    response = await datasette.client.get(
        "/-/sidebar/api/stars?database_name=db1", cookies=cookies
    )
    stars = response.json()["stars"]
    assert len(stars) == 1
    assert stars[0]["database_name"] == "db1"


@pytest.mark.asyncio
async def test_remove_star():
    datasette = _ds()
    cookies = _cookies(datasette)

    response = await datasette.client.post(
        "/-/sidebar/api/toggle-star",
        json={"star_type": "database", "database_name": "mydb"},
        cookies=cookies,
    )
    star_id = response.json()["star"]["id"]

    response = await datasette.client.post(
        f"/-/sidebar/api/stars/{star_id}/remove",
        json={},
        cookies=cookies,
    )
    assert response.status_code == 200
    assert response.json()["removed"] is True

    response = await datasette.client.get("/-/sidebar/api/stars", cookies=cookies)
    assert len(response.json()["stars"]) == 0
