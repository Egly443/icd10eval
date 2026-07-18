from __future__ import annotations

import json
import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from synthetic_episode_studio.benchmark import public_report
from synthetic_episode_studio.generator import DeterministicTemplateProvider
from synthetic_episode_studio.scenarios import scenario_catalogue


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "src" / "synthetic_episode_studio"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "site"


def _environment(static_prefix: str) -> Environment:
    environment = Environment(
        loader=FileSystemLoader(PACKAGE_ROOT / "templates"),
        autoescape=select_autoescape(("html", "xml")),
    )
    environment.globals["url_for"] = lambda _name, path: f"{static_prefix}static/{path.lstrip('/')}"
    return environment


def _public_samples() -> dict[str, dict]:
    provider = DeterministicTemplateProvider()
    return {
        scenario["id"]: provider.generate(scenario["id"], 2026).model_dump(mode="json")
        for scenario in scenario_catalogue()
    }


def build(output_root: Path = DEFAULT_OUTPUT_ROOT) -> Path:
    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    catalogue = scenario_catalogue()
    home = _environment("").get_template("index.html").render(
        scenarios=catalogue,
        general_surgery=[item for item in catalogue if item["track"] == "general-surgery"],
        well_baby=[item for item in catalogue if item["track"] == "well-baby"],
        recent=[],
    )
    home = (
        home.replace('href="/epicode-bench"', 'href="epicode-bench/"')
        .replace('href="/docs"', 'href="https://github.com/Egly443/icd10eval#api"')
        .replace('href="/"', 'href="./"')
    )
    studio_script = '<script src="static/studio.js" defer></script>'
    public_config = (
        "<script>window.STATIC_SITE=true;window.STATIC_EPISODES="
        + json.dumps(_public_samples(), separators=(",", ":"))
        + ";</script>"
    )
    home = home.replace(studio_script, public_config + studio_script)
    (output_root / "index.html").write_text(home, encoding="utf-8")

    benchmark_root = output_root / "epicode-bench"
    benchmark_root.mkdir()
    report = public_report()
    benchmark = _environment("../").get_template("benchmark.html").render(report=report)
    benchmark = benchmark.replace('href="/"', 'href="../"').replace(
        'href="/api/benchmark"', 'href="../data/benchmark.json"'
    )
    (benchmark_root / "index.html").write_text(benchmark, encoding="utf-8")

    shutil.copytree(PACKAGE_ROOT / "static", output_root / "static")
    data_root = output_root / "data"
    data_root.mkdir()
    (data_root / "benchmark.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (output_root / ".nojekyll").touch()
    return output_root


if __name__ == "__main__":
    built = build()
    print(f"Built GitHub Pages site at {built}")
