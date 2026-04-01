"""Unit tests for tasks/append_config_include.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT_DIR / "tasks" / "append_config_include.py"

spec = importlib.util.spec_from_file_location("append_config_include", SCRIPT_PATH)
mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules["append_config_include"] = mod
assert spec.loader
spec.loader.exec_module(mod)  # type: ignore[attr-defined]


def test_main_preserves_indented_sequence_style(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "__use_yte__: true",
                "__definitions__:",
                "  - from pathlib import Path",
                "  - |",
                "    def existing_configfiles(candidates):",
                "        return [candidate for candidate in candidates if Path(candidate).is_file()]",
                "__variables__:",
                "  configfile_candidates:",
                '    - "config/config.yaml"',
                '    - "config/config.local.yaml"',
                "",
                "?if existing_configfiles(configfile_candidates):",
                "  configfile: ?existing_configfiles(configfile_candidates)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    mod.main(
        config_file="config/new_module/example/config.yaml",
        config_path=config_path,
    )

    rendered = config_path.read_text(encoding="utf-8")

    assert "__definitions__:\n  - from pathlib import Path\n" in rendered
    assert "configfile_candidates:\n" in rendered
    assert '    - "config/config.yaml"\n' in rendered
    assert '    - "config/config.local.yaml"\n' in rendered
    assert "    - config/new_module/example/config.yaml\n" in rendered
    assert "configfile: ?existing_configfiles(configfile_candidates)\n" in rendered
    assert "\nconfigfile:\n  - config/new_module/example/config.yaml\n" not in rendered


def test_main_falls_back_to_legacy_configfile_list(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                "configfile:",
                '  - "config/config.yaml"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    mod.main(
        config_file="config/new_module/example/config.yaml",
        config_path=config_path,
    )

    rendered = config_path.read_text(encoding="utf-8")

    assert 'configfile:\n  - "config/config.yaml"\n' in rendered
    assert "  - config/new_module/example/config.yaml\n" in rendered
