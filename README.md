# comms-station

Open-source tooling that turns a vehicle — or any suitably equipped site — into an AI-managed communications hub for disasters and off-grid operation, usable by people without radio skills.

Most of the time, the hardest part of emergency communications isn't the radio. It's the operator: knowing which band to use, which mode will get through, which antenna to point where, and what's legal to transmit. This project puts an AI in that seat, with strict guardrails, so the station is useful to whoever happens to be standing next to it.

The core rule of the architecture:

> **The AI proposes; deterministic services validate and execute.**

The AI never touches a transmitter directly. It plans, drafts, and recommends. A deterministic orchestrator checks every request against legal, safety, and policy interlocks before anything keys up. If the checks fail, nothing transmits.

## What the station does

Four pillars, each useful on an ordinary Tuesday and essential when infrastructure fails:

1. **Communicate** — multi-bearer messaging across mesh, LoRa, amateur bands, satellite, and WAN links, with the AI selecting the best available bearer for each message.
2. **Form networks** — stand up HaLow/OpenMANET, Meshtastic, and Reticulum meshes; deploy relays; give neighbors local access. When the internet is down or sparse, the station is the community's connectivity anchor.
3. **Observe** — SDR spectrum survey, signal identification, and satellite reception, including **satellite hunt**: a first-class mission type that combines pass prediction with blind beacon search for spacecraft whose state is uncertain. A TinyGS/SatNOGS-style "local sky" dashboard shows what's overhead — useful before any RF hardware is even connected.
4. **Serve** — local content and services over the mesh: maps, offline reference libraries, and an emergency-dispatcher pattern. The station is a mobile archive node, not just a pipe.

## Satellite profiles

The station works satellites through a profile type system: the repo defines profile *types* (frequency ranges as parameters, waveform plugins, receiver interfaces) and ships public example profiles for openly documented spacecraft — weather satellites, amateur satellites, and similar. Operators load additional private profiles for spacecraft they are authorized to work; this repo ships only public examples.

## Status

**Pre-alpha, docs-first.** We are writing the architecture, safety model, and interfaces down before the software. The profile schema and validator are the first working code; the local-sky dashboard and orchestrator skeleton come next. See `docs/roadmap.md`.

## Reference implementation

The reference implementation is the [Good Ancestor VW bus](https://ev.goodancestor.com) — an electric vehicle conversion carrying the full station stack. The bus's own story lives at ev.goodancestor.com; this repo documents the generic station design it validates. A generic bill of materials is in `docs/reference-build/`.

## Repository layout

- `docs/` — architecture, safety model, AI agent design, satellite profile system, roadmap
- `profiles/` — profile schema and public example profiles
- `tools/` — validation and utility tooling
- `tests/` — tests for the tooling

## How to help

- **Read the docs and file issues.** At this stage, holes in the architecture and safety model are the most valuable thing to find.
- **Radio and SDR experience welcome** — especially around bearer selection, mesh deployment, and satellite reception. You don't need to be a licensed operator to contribute to the tooling, though transmit-side features assume licensed operation.
- **Software contributions** — see `CONTRIBUTING.md` for licensing, DCO-style expectations, and the publication checklist that gates everything in this repo.
- **Try the profile validator** against public satellite data and tell us where the schema falls short.

comms-station is a [Good Ancestor Foundation](https://goodancestor.com) project.

## Licensing

- Code: Apache-2.0
- Documentation: CC BY 4.0
- Hardware designs: CERN-OHL-S-2.0

See `CONTRIBUTING.md` for details and SPDX conventions.
