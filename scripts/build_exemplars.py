#!/usr/bin/env python3
"""Build the ten deterministic, schema-valid demonstration exemplars."""

from pathlib import Path

from synthetic_episode_studio.generator import DeterministicTemplateProvider
from synthetic_episode_studio.main import export_schema
from synthetic_episode_studio.scenarios import SCENARIOS


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "episodes" / "exemplars"


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    provider = DeterministicTemplateProvider()
    for index, scenario in enumerate(SCENARIOS):
        episode = provider.generate(scenario.id, 2026 + index)
        (OUTPUT / f"{scenario.id}.json").write_text(
            episode.model_dump_json(indent=2),
            encoding="utf-8",
        )
    export_schema()
    print(f"Built {len(SCENARIOS)} validated exemplars in {OUTPUT}")


if __name__ == "__main__":
    main()
