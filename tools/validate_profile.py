#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Validate a satellite contact profile against the profile schema.

Checks a YAML profile against ``profiles/schema/satellite-profile.schema.json``
plus semantic rules the schema cannot express (per-link ``freq_mhz_min <=
freq_mhz_max``). Profiles may carry additional keys anywhere; only the
declared structure is enforced.

Usage:

    python tools/validate_profile.py <profile.yaml>

Exit status 0 when the profile is valid, 1 otherwise (errors on stderr).

Library use:

    from validate_profile import validate_profile
    errors = validate_profile("profiles/examples/iss-ariss.yaml")
    # empty list means valid; otherwise a list of error messages
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
import yaml

SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent
    / "profiles"
    / "schema"
    / "satellite-profile.schema.json"
)


def _load_schema() -> dict:
    with open(SCHEMA_PATH) as fh:
        return json.load(fh)


def _format_path(error: jsonschema.ValidationError) -> str:
    parts = []
    for element in error.absolute_path:
        if isinstance(element, int):
            parts.append(f"[{element}]")
        else:
            parts.append(f".{element}" if parts else str(element))
    return "".join(parts) or "(root)"


def validate_profile(path: str) -> list[str]:
    """Validate the profile at *path*. Return a list of error messages.

    An empty list means the profile is valid.
    """
    try:
        with open(path) as fh:
            profile = yaml.safe_load(fh)
    except OSError as exc:
        return [f"cannot read profile: {exc}"]
    except yaml.YAMLError as exc:
        return [f"invalid YAML: {exc}"]

    if not isinstance(profile, dict):
        return ["profile must be a YAML mapping at the top level"]

    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors = [
        f"{_format_path(error)}: {error.message}"
        for error in sorted(validator.iter_errors(profile), key=str)
    ]

    # Semantic checks beyond JSON Schema: frequency range sanity per link.
    links = profile.get("links")
    if isinstance(links, list):
        for index, link in enumerate(links):
            if not isinstance(link, dict):
                continue
            fmin = link.get("freq_mhz_min")
            fmax = link.get("freq_mhz_max")
            if (
                isinstance(fmin, (int, float))
                and isinstance(fmax, (int, float))
                and fmin > fmax
            ):
                name = link.get("name", f"links[{index}]")
                errors.append(
                    f"links[{index}] ({name}): freq_mhz_min ({fmin}) "
                    f"must be <= freq_mhz_max ({fmax})"
                )

    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(
            "usage: python tools/validate_profile.py <profile.yaml>",
            file=sys.stderr,
        )
        return 1

    errors = validate_profile(argv[1])
    if errors:
        print(f"{argv[1]}: INVALID", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"{argv[1]}: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
