import subprocess


def test_mkdocs_build(tmp_path):
    site_dir = tmp_path / "site"
    result = subprocess.run(
        [
            "mkdocs",
            "build",
            "--strict",
            "--config-file",
            "docs/mkdocs.yml",
            "--site-dir",
            str(site_dir),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
