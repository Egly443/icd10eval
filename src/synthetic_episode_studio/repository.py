from __future__ import annotations

import json
import re
from pathlib import Path

from .models import Episode


SAFE_ID = re.compile(r"^[A-Z0-9-]+$")


class EpisodeRepository:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, episode: Episode) -> Path:
        path = self._path(episode.metadata.episode_id)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(episode.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(path)
        return path

    def load(self, episode_id: str) -> Episode:
        path = self._path(episode_id)
        return Episode.model_validate_json(path.read_text(encoding="utf-8"))

    def list_recent(self, limit: int = 6) -> list[dict[str, str | int]]:
        records: list[dict[str, str | int]] = []
        for path in sorted(self.root.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)[:limit]:
            data = json.loads(path.read_text(encoding="utf-8"))
            records.append(
                {
                    "episode_id": data["metadata"]["episode_id"],
                    "scenario_id": data["metadata"]["scenario_id"],
                    "seed": data["metadata"]["seed"],
                    "generated_at": data["metadata"]["generated_at"],
                }
            )
        return records

    def _path(self, episode_id: str) -> Path:
        if not SAFE_ID.fullmatch(episode_id):
            raise ValueError("Invalid episode identifier")
        return self.root / f"{episode_id}.json"
