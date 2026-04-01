#!/usr/bin/env python3
"""
Post-copy task for a Copier template.

After the template is rendered, this script appends a line of the form

```
config/<module_type>/<module_name>/<etl_name>/config.yaml
```

to the `configfile:` list in `workflow/profiles/default/config.yaml`,
ensuring that comments and manual edits to the YAML file are preserved.

Usage (executed automatically by Copier as a post-copy task, but can be
run manually as well):

    python tasks/append_config_include.py <module_type> <module_name>

Options:
    --config-path/-c  Path to the profile config.yaml (defaults to
                      workflow/profiles/default/config.yaml)

When the profile uses the YTE-based `__variables__.configfile_candidates`
structure introduced in able-workflow-copier, the new include is appended there.
Otherwise, the legacy top-level `configfile:` list is updated for backwards
compatibility.
"""
from __future__ import annotations

from pathlib import Path

import typer
from ruamel.yaml import YAML

app = typer.Typer(
    add_completion=False,
    help="""
        Append a module config include to the default Snakemake profile config.
    """,
)

# Default location of the profile configuration file – relative to the
# project root after rendering.
DEFAULT_CONFIG_PATH = Path("workflow/profiles/default/config.yaml")


def _load_yaml(path: Path) -> tuple[dict[str, object], YAML]:
    """Load YAML preserving comments and quoting style."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.load(fp)
    return data, yaml


def _normalize_sequence(container: dict[str, object], key: str) -> list[object]:
    """Normalize a YAML scalar/list field to a mutable list."""
    value = container.get(key)
    if value in (None, ""):
        container[key] = []
    elif isinstance(value, str):
        container[key] = [value]
    elif not isinstance(value, list):
        container[key] = [str(value)]
    return container[key]  # type: ignore[return-value]


def _get_config_target(data: dict[str, object]) -> list[object]:
    """Return the list to which config includes should be appended."""
    variables = data.get("__variables__")

    if isinstance(variables, dict) and "configfile_candidates" in variables:
        return _normalize_sequence(variables, "configfile_candidates")

    if "configfile" in data:
        return _normalize_sequence(data, "configfile")

    if data.get("__use_yte__") is True or "__variables__" in data:
        if not isinstance(variables, dict):
            variables = {}
            data["__variables__"] = variables
        return _normalize_sequence(variables, "configfile_candidates")

    return _normalize_sequence(data, "configfile")


@app.command()
def main(
    config_file: str = typer.Argument(
        ...,
        help="Path to config.yaml file for the module to append.",
    ),
    config_path: Path = typer.Option(
        DEFAULT_CONFIG_PATH,
        "--config-path",
        "-c",
        help="Path to the profile config.yaml to update.",
        exists=True,
        dir_okay=False,
        file_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    ),
) -> None:
    """Append the ETL config include to the profile config include list."""
    include_line = f"{config_file}"

    # Ensure the profile config exists
    if not config_path.exists():
        typer.echo(f"Error: {config_path} does not exist.", err=True)
        raise typer.Exit(code=1)

    data, yaml = _load_yaml(config_path)

    cfg = _get_config_target(data)

    # Append only when not already present
    if include_line not in cfg:
        cfg.append(include_line)

    # Write the modified YAML back, preserving formatting and comments
    with config_path.open("w", encoding="utf-8") as fp:
        yaml.dump(data, fp)

    typer.echo(f"Added '{include_line}' to {config_path}")


if __name__ == "__main__":
    # When invoked directly, forward control to Typer CLI
    app()
