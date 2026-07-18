# Contributing to comms-station

Thanks for helping build this. The project is pre-alpha and docs-first, so contributions to the architecture, safety model, and profile system are as valuable as code right now.

## Ground rules

1. **Safety architecture is non-negotiable.** "The AI proposes; deterministic services validate and execute" is the design invariant. PRs that let AI-originated output reach a transmitter, or any other actuator, without passing through deterministic validation will not be merged.
2. **Public examples only.** This repo ships profiles and documentation for openly documented systems (weather satellites, amateur satellites, public services). Do not contribute private contact profiles, coordination details for specific deployments, or anything you are not certain is public information.
3. **Small, reviewable PRs.** One concern per PR. Docs changes and code changes are both welcome; mixed PRs are fine when the docs describe the code.

## Publication checklist

This project practices default-deny disclosure. Contributors are expected to self-gate their own PRs against this checklist before opening them, and reviewers apply it again before merge:

> Before publishing anything in this project (docs, examples, issues, PRs): does it name (1) a person, (2) a place or deployment, (3) a partner who could be put at risk, (4) a capability timeline, (5) a frequency, schedule, or procedure for a specific non-public spacecraft or deployment, or (6) anyone's current operational posture? If any answer is yes, do not publish without maintainer review. Default deny.

For external contributors the practical reading is: if your contribution names people, places, deployments, at-risk partners, timelines, operational frequencies/schedules/procedures, or the current posture of any real deployment, stop and raise it in an issue first instead of putting it in a PR. Generic parameters, public spectrum data, and architecture concepts are fine — that's what the profile type system is for.

## Licensing

Everything in this repo is licensed as follows:

| Content | License | SPDX identifier |
|---|---|---|
| Code (tools, tests, scripts) | Apache License 2.0 | `Apache-2.0` |
| Documentation (docs/, Markdown) | Creative Commons Attribution 4.0 | `CC-BY-4.0` |
| Hardware designs (when added) | CERN Open Hardware Licence v2 — Strongly Reciprocal | `CERN-OHL-S-2.0` |

Rules:

- **Every code file carries an SPDX header** as its first comment line, e.g. `# SPDX-License-Identifier: Apache-2.0` for Python or `// SPDX-License-Identifier: Apache-2.0` for C-family languages.
- Hardware design files (schematics, PCB, CAD) carry `SPDX-License-Identifier: CERN-OHL-S-2.0` in a header or accompanying file when the format doesn't support comments.
- Documentation files may carry `SPDX-License-Identifier: CC-BY-4.0` in front matter or a footer; the repo-level default in this file applies where they don't.
- License texts live in `LICENSE` (Apache-2.0) and `LICENSES/`.
- By contributing, you agree your contribution is licensed under the license applicable to its content type above. Only contribute material you have the right to license this way.

## Developer Certificate of Origin

This project uses the [Developer Certificate of Origin](https://developercertificate.org/) (DCO). By signing off a commit you certify that you wrote the contribution or otherwise have the right to submit it under the project's licenses, per the DCO text.

- Sign off every commit with a `Signed-off-by` line matching your identity: `git commit -s`, which appends e.g. `Signed-off-by: Your Name <you@example.com>`.
- Licensing is **inbound = outbound**: your contribution is accepted under the same license that applies to the content type you are contributing to (see the table above), with no additional terms in either direction.

## Development

- Python tooling targets Python 3.11+; dependencies are minimal (`jsonschema`, `pyyaml`, `pytest`).
- Run tests with `pytest tests/ -v` from the repo root. PRs that touch `tools/` should include or update tests.
- Validate profile files with `python tools/validate_profile.py <profile.yaml>` — exit 0 means valid.

## Reporting issues

- Architecture or safety-model gaps: open an issue describing the failure scenario. These are the highest-value reports right now.
- Schema shortcomings: include the (public) profile you were trying to express.
- Security-relevant issues in the validation/interlock path: please flag the issue as security-related so it gets prioritized review.
