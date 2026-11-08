<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Roadmap

comms-station is docs-first and pre-alpha. This roadmap describes the phases a station build moves through — from bare inventory to a reproducible, AI-managed communications hub — and where the project itself currently stands. Phases are ordered by dependency, not by calendar: each one produces something usable on its own, and each later phase assumes the earlier ones hold. Builders adapting the project to their own hardware should expect to walk the same sequence.

The phase structure follows the reference implementation's engineering plan (the Good Ancestor VW bus, [ev.goodancestor.com](https://ev.goodancestor.com)), generalized to any station.

## Current status

First deliverables, in order:

1. **Profile validator** — done. Schema and validator for satellite profiles (`profiles/schema/`, `tools/validate_profile.py`), with two public example profiles (ISS ARISS amateur, Meteor-M N2-4 weather) and more planned (Inmarsat). See [satellite-profiles.md](satellite-profiles.md).
2. **Local-sky map** — next. A TinyGS/SatNOGS-style dashboard of what is overhead and upcoming, driven by a local TLE cache and community networks. Deliberately chosen because it is useful before any RF hardware is connected: it needs only the profile system, a TLE fetcher, and a pass predictor, and it exercises the scheduler code every later phase depends on.
3. **Orchestrator skeleton** — after that. The deterministic core service: canonical state store, event bus, typed mission-request API, and policy checks, initially with simulated adapters only. This is the piece everything else plugs into, per [architecture.md](architecture.md).

## Phase 0 — inventory and baseline

Know exactly what you have before automating any of it.

Deliverables:

- Photograph every device and connector; label all cables.
- Record serial numbers, firmware versions, USB IDs, MAC addresses, power requirements, and antenna assignments.
- Back up all existing device configurations.
- Produce a machine-readable asset inventory (YAML) — the seed of the station profile.
- Freeze a known-good network diagram.

Exit criteria: every device is uniquely identifiable; no unknown power requirement remains for connected equipment.

## Phase 1 — deterministic control plane

The Tier 1 mission controller becomes the station's always-available brain — no AI involved yet.

Deliverables:

- Event bus and canonical state store.
- Initial orchestrator API.
- Power telemetry from the Tier 0 supervisors.
- Graceful wake/shutdown of the Tier 2 compute node.
- Rotator control including safe stow.
- GNSS/time service.
- Operator dashboard.

Exit criteria: the mission controller runs fully without the AI tier; the rotator stows safely after an AI-tier failure; power domains can be controlled and audited.

## Phase 2 — receive-only satellite and SDR

Everything in this phase is receive-only, so it can be built and tested with no transmit authorization and no risk.

Deliverables:

- SDR receive path with decoder profiles for public satellites (weather-satellite imagery is the canonical first target).
- Automatic pass scheduler driven by the local TLE cache.
- Signal archive with standard metadata (SigMF-class).
- Higher-capability SDR drivers on the Tier 2 node.
- Spectrum-survey mission type.

Exit criteria: at least three scheduled passes complete automatically end-to-end; unknown-signal captures produce valid metadata; no receiver is damaged during nearby low-power transmitter tests.

## Phase 3 — offline messaging bearers

The Communicate pillar: move messages with no infrastructure.

Deliverables:

- Mesh messaging gateways (Meshtastic; Reticulum on the mission controller and endpoints).
- Packet-radio gateway integration.
- Message-routing API with best-bearer selection.
- Local voice service over the station network.

Exit criteria: a message routes through at least two fully offline bearers; services recover cleanly after a mission-controller reboot; untrusted received content cannot invoke tools (see [safety-model.md](safety-model.md)).

## Phase 4 — field mesh network

The Form-networks pillar: the station becomes a connectivity anchor for other people.

Deliverables:

- Vehicle/site mesh anchor (HaLow/OpenMANET-class).
- At least two deployable field-relay profiles.
- Compatibility test matrix for candidate mesh hardware.
- Situational-awareness integration (CoT/ATAK-class).
- Remote-sensor pilot over the mesh (e.g. remote SDR or ADS-B).

Exit criteria: a multi-hop field test passes; the mesh survives the loss of one node; core station services remain isolated from mesh clients.

## Phase 5 — transceiver integration and interlocks

Transmit capability arrives last among the radio phases, and only behind the full interlock stack.

Deliverables:

- Dedicated power branches for each transceiver.
- Transceiver control adapters (Hamlib/CAT).
- RF interlocks wired and enforced.
- Dummy-load commissioning, then low-power live tests.
- Automated antenna and SWR checks.
- Satellite and HF mission profiles.

Exit criteria: the AI can configure radios but cannot bypass authorization; PTT is blocked with the wrong antenna payload, a moving vehicle, or poor SWR; radios recover to a safe state after any process failure.

## Phase 6 — AI agent

The AI becomes the operator's interface — proposing, never executing.

Deliverables:

- Local model gateway (pluggable model selection).
- Voice UI.
- Typed tool schemas for mission requests.
- Retrieval index over manuals, band plans, logs, and local data.
- Evaluation suite, including adversarial prompts.
- Confidence and evidence display in the UI.
- Small fallback model on the mission controller.

Exit criteria: benchmarked tool-call accuracy; no unsafe action in adversarial prompt tests; every mission plan and abort reason is clear and human-readable.

## Phase 7 — reproducible release

The project stands on its own, without the reference implementation.

Deliverables:

- Reproducible install.
- Sample station profiles (vehicle, portable, home ground station).
- Emulator/simulator so contributors can develop with no hardware.
- Complete public documentation and contribution guide.
- Security policy.
- Reference-build page documenting the Good Ancestor VW bus profile.

Exit criteria: a contributor with none of the reference hardware can install the stack, run the simulator, pass the test suite, and add an adapter for their own equipment.
