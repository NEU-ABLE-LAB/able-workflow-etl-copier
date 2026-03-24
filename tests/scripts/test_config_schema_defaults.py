"""Ensure config templates include schema-declared default values."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

ROOT_DIR = Path(__file__).resolve().parents[2]
JINJA_EXPR_RE = re.compile(r"{{\s*[^}]+\s*}}")
SCHEMAS_DIR = ROOT_DIR / "template" / "workflow" / "schemas"
CONFIG_DIR = ROOT_DIR / "template" / "config"


def _discover_template_pairs() -> list[tuple[Path, Path]]:
    """Discover schema/config pairs under this repository's template dirs."""
    pairs: list[tuple[Path, Path]] = []

    for schema_path in sorted(SCHEMAS_DIR.rglob("config.schema.yaml.jinja")):
        relative_parent = schema_path.relative_to(SCHEMAS_DIR).parent
        config_path = CONFIG_DIR / relative_parent / "config.yaml.jinja"
        if config_path.is_file():
            pairs.append((schema_path, config_path))

    return pairs


TEMPLATE_PAIRS = _discover_template_pairs()
if not TEMPLATE_PAIRS:
    msg = (
        "No schema/config template pairs discovered; expected files matching "
        f"{SCHEMAS_DIR}/**/config.schema.yaml.jinja with corresponding "
        f"{CONFIG_DIR}/**/config.yaml.jinja."
    )
    raise AssertionError(msg)


def _load_jinja_yaml(path: Path) -> dict[str, Any]:
    """Load a Jinja-templated YAML file as plain YAML data."""
    text = path.read_text(encoding="utf-8")
    sanitized = JINJA_EXPR_RE.sub("JINJA_TOKEN", text)
    loaded = YAML(typ="safe").load(sanitized) or {}
    if not isinstance(loaded, dict):
        msg = f"Expected top-level mapping in {path}, got {type(loaded).__name__}"
        raise TypeError(msg)
    return loaded


def _collect_schema_defaults(
    node: dict[str, Any],
    path: tuple[str, ...] = (),
) -> dict[tuple[str, ...], Any]:
    """Collect schema `default` values keyed by their property path."""
    defaults: dict[tuple[str, ...], Any] = {}

    if "default" in node and path:
        defaults[path] = node["default"]

    properties = node.get("properties")
    if not isinstance(properties, dict):
        return defaults

    for key, child in properties.items():
        if not isinstance(key, str) or not isinstance(child, dict):
            continue
        defaults.update(_collect_schema_defaults(child, path + (key,)))

    return defaults


def _get_config_value(config: dict[str, Any], path: tuple[str, ...]) -> Any:
    """Read a nested config value by tuple path."""
    current: Any = config
    for key in path:
        if not isinstance(current, dict):
            msg = f"Path {' -> '.join(path)} does not resolve to a mapping"
            raise AssertionError(msg)
        if key not in current:
            msg = f"Missing config key {' -> '.join(path)}"
            raise AssertionError(msg)
        current = current[key]
    return current


@pytest.mark.parametrize(
    ("schema_path", "config_path"),
    TEMPLATE_PAIRS,
    ids=[
        str(schema_path.relative_to(SCHEMAS_DIR)) for schema_path, _ in TEMPLATE_PAIRS
    ],
)
def test_config_yaml_contains_schema_defaults(
    schema_path: Path,
    config_path: Path,
) -> None:
    """Validate config values match each default declared in the schema."""
    schema = _load_jinja_yaml(schema_path)
    config = _load_jinja_yaml(config_path)

    defaults = _collect_schema_defaults(schema)
    for path, expected_default in defaults.items():
        actual_value = _get_config_value(config, path)
        assert actual_value == expected_default
