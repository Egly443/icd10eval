from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .generator import DeterministicTemplateProvider
from .models import Episode, GenerateRequest
from .repository import EpisodeRepository
from .scenarios import SCENARIO_BY_ID, scenario_catalogue


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(__file__).resolve().parent
GENERATED_ROOT = PROJECT_ROOT / "episodes" / "generated"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "episode.schema.json"


def export_schema() -> None:
    SCHEMA_PATH.parent.mkdir(parents=True, exist_ok=True)
    SCHEMA_PATH.write_text(
        __import__("json").dumps(Episode.model_json_schema(), indent=2),
        encoding="utf-8",
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    GENERATED_ROOT.mkdir(parents=True, exist_ok=True)
    export_schema()
    yield


app = FastAPI(
    title="Synthetic Episode Studio",
    summary="Evidence-linked synthetic NHS-style episodes for product evaluation.",
    version="0.1.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=PACKAGE_ROOT / "static"), name="static")
templates = Jinja2Templates(directory=PACKAGE_ROOT / "templates")
provider = DeterministicTemplateProvider()
repository = EpisodeRepository(GENERATED_ROOT)


@app.get("/", include_in_schema=False)
async def index(request: Request):
    catalogue = scenario_catalogue()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "scenarios": catalogue,
            "general_surgery": [item for item in catalogue if item["track"] == "general-surgery"],
            "well_baby": [item for item in catalogue if item["track"] == "well-baby"],
            "recent": repository.list_recent(),
        },
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "synthetic-episode-studio"}


@app.get("/api/scenarios")
async def scenarios() -> list[dict[str, str]]:
    return scenario_catalogue()


@app.post("/api/episodes", response_model=Episode, status_code=201)
async def generate_episode(request: GenerateRequest) -> Episode:
    if request.scenario_id not in SCENARIO_BY_ID:
        raise HTTPException(status_code=404, detail="Scenario not found")
    episode = provider.generate(request.scenario_id, request.seed)
    if not episode.validation or not episode.validation.valid:
        raise HTTPException(status_code=422, detail="Generated episode did not pass validation")
    repository.save(episode)
    return episode


@app.get("/api/episodes/{episode_id}", response_model=Episode)
async def get_episode(episode_id: str) -> Episode:
    try:
        return repository.load(episode_id)
    except (FileNotFoundError, ValueError):
        raise HTTPException(status_code=404, detail="Episode not found") from None


@app.get("/api/episodes/{episode_id}/download")
async def download_episode(episode_id: str) -> Response:
    try:
        path = repository._path(episode_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Episode not found") from None
    if not path.exists():
        raise HTTPException(status_code=404, detail="Episode not found")
    return Response(
        content=path.read_bytes(),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{episode_id}.json"'},
    )
