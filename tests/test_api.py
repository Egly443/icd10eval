from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from synthetic_episode_studio import main
from synthetic_episode_studio.repository import EpisodeRepository
from synthetic_episode_studio.scenarios import SCENARIOS


@pytest.fixture()
async def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(main, "repository", EpisodeRepository(tmp_path / "generated"))
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url="http://test") as test_client:
        yield test_client


@pytest.fixture()
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_home_and_health(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert "Create consistent, traceable, export-ready" in response.text
    assert "Not clinically validated" in response.text
    assert (await client.get("/health")).json()["status"] == "ok"


@pytest.mark.anyio
async def test_catalogue_has_two_tracks_and_ten_scenarios(client: AsyncClient) -> None:
    response = await client.get("/api/scenarios")
    assert response.status_code == 200
    catalogue = response.json()
    assert len(catalogue) == 10
    assert {item["track"] for item in catalogue} == {"general-surgery", "well-baby"}


@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda scenario: scenario.id)
@pytest.mark.anyio
async def test_generate_persist_fetch_and_export(scenario, client: AsyncClient) -> None:
    response = await client.post("/api/episodes", json={"scenario_id": scenario.id, "seed": 42})
    assert response.status_code == 201
    episode = response.json()
    episode_id = episode["metadata"]["episode_id"]
    assert episode["validation"]["valid"] is True
    assert (await client.get(f"/api/episodes/{episode_id}")).json() == episode
    download = await client.get(f"/api/episodes/{episode_id}/download")
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/json")


@pytest.mark.anyio
async def test_unknown_scenario_and_unsafe_id_are_not_exposed(client: AsyncClient) -> None:
    assert (await client.post("/api/episodes", json={"scenario_id": "unknown", "seed": 1})).status_code == 404
    assert (await client.get("/api/episodes/../../etc/passwd")).status_code == 404
