"""
Render every SUMMARY.md under docs/docs/ with Jinja, using variables
from docs/mkdocs.yml::extra.  The rendered content is written back to
the same relative path *inside* MkDocs' virtual file system.

Requires:
  - mkdocs-gen-files
  - ruamel.yaml >= 0.18
  - jinja2
"""

from pathlib import Path

import jinja2
import mkdocs_gen_files as gen_files
from mkdocs.config import load_config as load_mkdocs_config

# ---------------------------------------------------------------------
# 1.  Load mkdocs.yml with ruamel.yaml
# ---------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]  # repo root
MKDOCS_YML = ROOT / "docs" / "mkdocs.yml"

mkdocs_cfg = load_mkdocs_config(str(MKDOCS_YML))
ctx = mkdocs_cfg.get("extra", {})  # variables for Jinja


# ---------------------------------------------------------------------
# 2.  Prepare the Jinja environment
# ---------------------------------------------------------------------
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(ROOT)),
    undefined=jinja2.StrictUndefined,
    autoescape=False,
)


# ---------------------------------------------------------------------
# 3.  Walk docs/docs/**/SUMMARY.md, render, and emit via gen-files
# ---------------------------------------------------------------------
DOCS_SRC = ROOT / "docs" / "docs"

for path in DOCS_SRC.rglob("SUMMARY.md"):
    raw = path.read_text(encoding="utf-8")

    rendered = jinja_env.from_string(raw).render(**ctx)

    # keep same path *inside* MkDocs' virtual file tree:
    #   docs/…/SUMMARY.md
    rel_path = path.relative_to(ROOT / "docs" / "docs")

    with gen_files.open(rel_path, "w") as fp:
        fp.write(rendered)
