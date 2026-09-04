from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from .models import Metadata

BASE_URL = "https://start.spring.io"
METADATA_URL = f"{BASE_URL}/metadata/client"
PROJECT_URL = f"{BASE_URL}/starter.zip"
CACHE_DIR = Path.home() / ".cache" / "spring-init"
CACHE_FILE = CACHE_DIR / "metadata.json"
CACHE_TTL = 3600

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "spring-init-cli/0.1.0"})


def _fetch_metadata_live() -> dict:
    resp = SESSION.get(METADATA_URL, headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()


def _read_cache() -> dict | None:
    if not CACHE_FILE.exists():
        return None
    try:
        data = json.loads(CACHE_FILE.read_text())
        if time.time() - data.get("_cached_at", 0) > CACHE_TTL:
            return None
        return data.get("payload")
    except (json.JSONDecodeError, KeyError):
        return None


def _write_cache(payload: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps({"_cached_at": time.time(), "payload": payload}))


def fetch_metadata() -> Metadata:
    from .models import Dependency, DependencyGroup, ProjectType, SpringBootVersion

    cached = _read_cache()
    if cached is not None:
        raw = cached
    else:
        try:
            raw = _fetch_metadata_live()
            _write_cache(raw)
        except requests.RequestException as e:
            print(f"Error: Could not fetch metadata from Spring Initializr: {e}", file=sys.stderr)
            sys.exit(1)

    project_types = []
    for v in raw["type"]["values"]:
        if v["tags"].get("format") == "project":
            project_types.append(ProjectType(id=v["id"], name=v["name"]))

    languages = [v["id"] for v in raw["language"]["values"]]

    boot_versions = []
    for v in raw["bootVersion"]["values"]:
        vid = v["id"]
        api_value = (
            vid.replace(".BUILD-SNAPSHOT", "-SNAPSHOT")
               .replace(".M", "-M")
               .replace(".RELEASE", "")
        )
        boot_versions.append(SpringBootVersion(id=vid, name=v["name"], api_value=api_value))

    java_versions = [v["id"] for v in raw["javaVersion"]["values"]]

    packaging_options = [v["id"] for v in raw["packaging"]["values"]]

    dependency_groups = []
    for group in raw["dependencies"]["values"]:
        deps = []
        for dep in group["values"]:
            deps.append(Dependency(
                id=dep["id"],
                name=dep["name"],
                description=dep.get("description", ""),
            ))
        dependency_groups.append(DependencyGroup(name=group["name"], values=deps))

    from .models import Metadata

    return Metadata(
        project_types=project_types,
        languages=languages,
        boot_versions=boot_versions,
        java_versions=java_versions,
        packaging_options=packaging_options,
        dependency_groups=dependency_groups,
    )


def generate_project(params: dict[str, str], output_path: Path) -> None:
    resp = SESSION.get(PROJECT_URL, params=params, stream=True)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
