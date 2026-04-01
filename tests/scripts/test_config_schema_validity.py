"""Validate config templates against matching schema templates."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import jsonschema
import pytest
from ruamel.yaml import YAML

ROOT_DIR = Path(__file__).resolve().parents[2]
JINJA_EXPR_RE = re.compile(r"{{\s*[^}]+\s*}}")
SCHEMAS_DIR = ROOT_DIR / "template" / "workflow" / "schemas"
CONFIG_DIR = ROOT_DIR / "template" / "config"


def _discover_template_pairs() -> list[tuple[Path, Path]]:
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
    text = path.read_text(encoding="utf-8")
    sanitized = JINJA_EXPR_RE.sub("JINJA_TOKEN", text)
    loaded = _normalize_jinja_placeholders(YAML(typ="safe").load(sanitized) or {})
    if not isinstance(loaded, dict):
        msg = f"Expected top-level mapping in {path}, got {type(loaded).__name__}"
        raise TypeError(msg)
    return loaded


def _normalize_jinja_placeholders(value: Any) -> Any:
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, item in value.items():
            normalized_item = _normalize_jinja_placeholders(item)
            if key == "JINJA_TOKEN" and normalized_item is None:
                normalized[key] = {}
            else:
                normalized[key] = normalized_item
        return normalized

    if isinstance(value, list):
        return [_normalize_jinja_placeholders(item) for item in value]

    return value


@pytest.mark.parametrize(
    ("schema_path", "config_path"),
    TEMPLATE_PAIRS,
    ids=[
        str(schema_path.relative_to(SCHEMAS_DIR)) for schema_path, _ in TEMPLATE_PAIRS
    ],
)
def test_config_template_validates_against_schema(
    schema_path: Path,
    config_path: Path,
) -> None:
    schema = _load_jinja_yaml(schema_path)
    config = _load_jinja_yaml(config_path)

    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    validator = validator_cls(schema)
    validator.validate(config)
