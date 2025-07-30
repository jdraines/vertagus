import os
from pathlib import Path
import pytest
from click.testing import CliRunner
from vertagus.cli.commands import bump_cmd
import yaml
from contextlib import contextmanager


_mock_configs_dir = Path(__file__).parent.parent.parent / "mock_docs" / "configs"
_mock_manifests_dir = Path(__file__).parent.parent.parent / "mock_docs" / "manifests"


@contextmanager
def write_temp_file(content, type, name):
    if type == "config":
        dirpath: Path = _mock_configs_dir / type
    elif type == "manifest":
        dirpath: Path = _mock_manifests_dir / type
    else:
        raise ValueError("Invalid type. Use 'config' or 'manifest'.")
    
    os.makedirs(dirpath, exist_ok=True)
    filepath: Path = dirpath / name
    Path(filepath).write_text(content)
    try:
        yield filepath
    finally:
        if filepath.exists():
            filepath.unlink()

_CONFIG = """\
scm:
  type: git
project:
  bumper:
    type: semver
  rules:
    current:
      - not_empty
    increment:
      - any_increment
  manifests:
    - name: bumptest.yaml
      type: yaml
      path: {manifest_path}
      loc: "foo.bar"
"""

_MANIFEST = """\
foo:
  bar: 1.0.0
"""

@contextmanager
def temp_manifest():
    with write_temp_file(_MANIFEST, "manifest", "bumptest.yaml") as manifest_path:
        yield manifest_path


@contextmanager
def temp_config(manifest_path: Path):
    config_content = _CONFIG.format(manifest_path=str(manifest_path))
    with write_temp_file(config_content, "config", "01-simple.yaml") as config_path:
        yield config_path


def load_manifest(manifest_path: Path):
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def set_manifest_version(manifest_path: Path, version: str):
    manifest_data = load_manifest(manifest_path)
    manifest_data["foo"]["bar"] = version
    with open(manifest_path, 'w') as f:
        yaml.dump(manifest_data, f)


def reset_manifest(manifest_path: Path):
    with open(manifest_path, 'w') as f:
        f.write(_MANIFEST)


@pytest.fixture
def runner():
    return CliRunner()


@pytest.mark.parametrize(
    "level, expected_bumped_version, expected_exit_code, test_version",
    [
        ("major", "2.0.0", 0, "1.0.0"), # v0.2.4
        ("minor", "1.1.0", 0, "1.0.0"), # v0.2.4
        ("patch", "1.0.1", 0, "1.0.0"), # v0.2.4
        ("tag", "1.0.0-dev1", 0, "1.0.0-dev0"), # v0.2.4
        ("level=major", "2.0.0", 0, "1.0.0"),
        ("level=minor", "1.1.0", 0, "1.0.0"),
        ("level=patch", "1.0.1", 0, "1.0.0"),
        ("level=tag", "1.0.0-dev1", 0, "1.0.0-dev0"),
    ],
)
def test_bump(
    runner: CliRunner,
    level: str,
    expected_bumped_version: str,
    expected_exit_code: int,
    test_version: str
):
    with temp_manifest() as manifest_path:
        with temp_config(manifest_path) as config_path:
            set_manifest_version(manifest_path, test_version)
            result = runner.invoke(bump_cmd, ["--config", str(config_path), level])
            assert result.exit_code == expected_exit_code
            if expected_exit_code == 0:
                version = load_manifest(manifest_path)["foo"]["bar"]
                assert version == expected_bumped_version, f"Expected {expected_bumped_version}, got {version}"
            reset_manifest(manifest_path)
