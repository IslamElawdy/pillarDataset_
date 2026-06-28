from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    config_dir: Path
    output_dir: Path
    coco_dataset_dir: Path
    previews_dir: Path


def load_yaml(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping: {path}")
    return data


def load_classes(path: str | Path = "config/classes.yaml") -> list[dict[str, Any]]:
    data = load_yaml(path)
    classes = data.get("classes", [])
    if not isinstance(classes, list):
        raise ValueError("classes.yaml must contain a list under key 'classes'")
    return [item for item in classes if item.get("enabled", True)]


def get_project_paths() -> ProjectPaths:
    paths_config = load_yaml("config/paths.yaml")
    output_root = PROJECT_ROOT / paths_config.get("output", {}).get("root", "output")
    return ProjectPaths(
        root=PROJECT_ROOT,
        config_dir=PROJECT_ROOT / "config",
        output_dir=output_root,
        coco_dataset_dir=PROJECT_ROOT / paths_config.get("output", {}).get("coco_dataset", "output/coco_dataset"),
        previews_dir=PROJECT_ROOT / paths_config.get("output", {}).get("previews", "output/previews"),
    )


def ensure_dirs(*dirs: str | Path) -> None:
    for directory in dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
