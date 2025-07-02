#!/usr/bin/env python3
"""
Post-copy task for a Copier template.

After the template is rendered, this script appends a line of the form

```
config/<module_type>/<module_name>/<etl_name>config.yaml
```

to the `configfile:` list in `workflow/profiles/default/config.yaml`,
ensuring that comments and manual edits to the YAML file are preserved.

Usage (executed automatically by Copier as a post-copy task, but can be
run manually as well):

    python tasks/append_config_include.py <module_type> <module_name>

Options:
    --config-path/-c  Path to the profile config.yaml (defaults to
                      workflow/profiles/default/config.yaml)
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
    with path.open("r", encoding="utf-8") as fp:
        data = yaml.load(fp)
    return data, yaml


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
    """Append the module config include to the `configfile` list if absent."""
    include_line = f"{config_file}"

    # Ensure the profile config exists
    if not config_path.exists():
        typer.echo(f"Error: {config_path} does not exist.", err=True)
        raise typer.Exit(code=1)

    data, yaml = _load_yaml(config_path)

    # If `configfile` is missing or null, start a new list
    if "configfile" not in data or data["configfile"] in (None, ""):
        data["configfile"] = [include_line]
    else:
        cfg = data["configfile"]

        # Normalize to list if the field is a scalar string
        if isinstance(cfg, str):
            cfg = [cfg]
            data["configfile"] = cfg
        elif not isinstance(cfg, list):
            cfg = [str(cfg)]
            data["configfile"] = cfg

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
