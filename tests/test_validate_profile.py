# SPDX-License-Identifier: Apache-2.0
"""Tests for the satellite-profile validator.

Run from the repository root:

    python3 -m pytest tests/ -v
"""

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

from validate_profile import validate_profile  # noqa: E402

EXAMPLE_PROFILE = REPO_ROOT / "profiles" / "examples" / "iss-ariss.yaml"


def load_example() -> dict:
    with open(EXAMPLE_PROFILE) as fh:
        return yaml.safe_load(fh)


def write_profile(tmp_path: Path, data: dict) -> str:
    path = tmp_path / "profile.yaml"
    with open(path, "w") as fh:
        yaml.safe_dump(data, fh)
    return str(path)


def test_valid_example_passes():
    """The shipped public example profile validates cleanly."""
    assert validate_profile(str(EXAMPLE_PROFILE)) == []


def test_missing_links_fails(tmp_path):
    """A profile without a links section is invalid, and the error says so."""
    data = load_example()
    del data["links"]
    errors = validate_profile(write_profile(tmp_path, data))
    assert errors, "expected validation errors for a profile with no links"
    assert any("links" in err for err in errors)


def test_bad_direction_fails(tmp_path):
    """direction must be one of uplink | downlink | duplex."""
    data = load_example()
    data["links"][0]["direction"] = "sideways"
    errors = validate_profile(write_profile(tmp_path, data))
    assert errors, "expected validation errors for an invalid link direction"


def test_freq_min_greater_than_max_fails(tmp_path):
    """A link whose freq_mhz_min exceeds freq_mhz_max is semantically invalid."""
    data = load_example()
    data["links"][0]["freq_mhz_min"] = 500.0
    data["links"][0]["freq_mhz_max"] = 100.0
    errors = validate_profile(write_profile(tmp_path, data))
    assert errors, "expected validation errors when freq_mhz_min > freq_mhz_max"
