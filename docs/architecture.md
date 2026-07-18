<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Architecture

comms-station turns a vehicle — or any suitably equipped fixed site — into an AI-managed communications hub for disasters and off-grid operation, usable by people without radio skills. The onboard AI acts as the radio operator; a deterministic orchestrator validates and executes within legal and safety interlocks.

The design rule that everything else follows from:

> **The AI proposes; deterministic services validate and execute.**

The model never touches hardware directly. Every action flows through a typed request that a conventional, auditable service checks against policy, state, legality, power, and antenna constraints before anything keys up, rotates, or draws current.

This document describes the system in four parts: the tiered power-and-control architecture, the communications topology, the canonical-state command flow, and how the project's four pillars map onto subsystems. Companion documents cover the [safety model](safety-model.md), the [AI agent](ai-agent.md), and the [satellite profile system](satellite-profiles.md).

## 1. Tiered power and control architecture

A station has to keep working — and keep being safe — as components fail, batteries sag, and expensive equipment is powered down to save energy. The architecture is therefore split into four tiers, ordered by criticality. Lower tiers never depend on higher tiers.

```text
TIER 0 — ALWAYS ON / HARD SAFETY
  microcontroller power supervisors
  battery-voltage and temperature rules
  ignition / park / deployment sensors
  converter enable lines and relay drivers
  watchdog and hard timeout
          │
          ▼
TIER 1 — MISSION CONTROLLER
  low-power single-board computer + operator display
  canonical state store and event bus (MQTT-class)
  communications orchestrator
  radio/rotator control daemons
  GNSS / time / pass scheduler
  messaging-bearer gateways (mesh, packet, Reticulum)
  low-power SDR receive
          │
          ▼
TIER 2 — AI AND DSP
  GPU compute node
  local multimodal model, voice agent, retrieval
  DSP toolchain (SatDump / GNU Radio / SDRangel-class)
  higher-capability SDRs
  signal classification and I/Q archive
          │
          ▼
TIER 3 — POWER-GATED PERIPHERALS
  conventional transceivers (VHF/UHF, HF)
  antenna rotator and active feeds
  satellite internet terminal
  secondary displays
  amplifiers, LNAs, filters, antenna relays
```

**Tier 0** is deliberately simple: microcontrollers running fixed rules, with no AI, no general-purpose OS, and no network dependencies. It enforces battery protection, thermal limits, deployment-state sensing, and hard timeouts, and it can cut power to everything above it. It is the layer that must be correct.

**Tier 1** is the always-available brain. A low-power single-board computer runs the canonical state store, the event bus, and the communications orchestrator — the deterministic service that owns every decision about what the station actually does. Basic receive, messaging, scheduling, and the operator UI all work at this tier alone, so the station degrades gracefully rather than failing outright when the AI tier is off.

**Tier 2** is the expensive brain: a GPU node hosting the local model, voice interaction, retrieval, and the heavier DSP toolchain. It is powered up when its capabilities are wanted and shut down cleanly when they are not. Nothing at Tier 1 breaks when Tier 2 is absent.

**Tier 3** is individually switched heavy peripherals: transceivers, the rotator, the satellite internet terminal, amplifiers. Each has its own power domain so the orchestrator can budget energy per mission and Tier 0 can shed load safely.

The tiers are roles, not shopping lists. Any hardware that fills a role works; the profile system (see §5 and [satellite-profiles.md](satellite-profiles.md)) binds roles to concrete devices per station. The Good Ancestor VW bus ([ev.goodancestor.com](https://ev.goodancestor.com)) is the reference profile — the build the project's requirements are drawn from and tested against.

## 2. Communications topology

```text
                          WIDE-AREA NETWORKS
              satellite internet / cellular / public Wi-Fi
                                 │
                          edge router
                 VPN / firewall / DNS / multi-WAN
                                 │
                        core Ethernet switch
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
  mission controller       AI/DSP compute node      mesh gateway
  (Tier 1)                 (Tier 2)                 HaLow / OpenMANET
         │                       │                       │
         │                       ├── SDR transceivers    ├── field relay nodes
         ├── antenna rotator     └── DSP pipelines       ├── Meshtastic mesh
         ├── low-power SDR receive                       └── client devices
         ├── VHF/UHF radio links
         ├── messaging gateways (Reticulum, packet)
         ├── Tier 0 power/control network
         └── transceiver control (LAN/USB/CAT)
```

Three properties matter more than the specific boxes:

1. **The WAN is optional.** Internet uplinks (satellite terminal, cellular, borrowed Wi-Fi) are treated as one more bearer — useful when present, never assumed. Every core function, including the AI, runs fully offline.
2. **The station is a network anchor, not just a terminal.** The mesh gateway side (HaLow/OpenMANET, Meshtastic, Reticulum) exists to give *other people* connectivity: field relays are deployed outward from the station, and local services are published to mesh clients.
3. **Control and RF are segregated.** Radios and SDRs hang off the mission controller and the AI node through explicit control paths (CAT/serial, LAN, USB), and mesh clients are firewalled from the control plane. A device on the mesh can use the station's services; it cannot command the station.

## 3. Canonical state and command flow

All station state — device inventory, power domains, deployment status, active missions, position, time — lives in one canonical store owned by the orchestrator at Tier 1. Every component reads from it and every change is an audited event. There are no side channels: the voice agent, the touchscreen, a CLI, and an authorized remote client are all the same kind of client making the same kind of request.

```text
   operator: voice / touchscreen / CLI / authorized remote client
                              │
                              ▼
                        local AI agent
                 intent, planning, explanation
                              │
                    typed mission request
                              ▼
                 communications orchestrator
       policy + state + legality + power + antenna checks
                              │
            ┌─────────────────┼────────────────────┐
            ▼                 ▼                    ▼
      radio adapters      SDR adapters        network adapters
      Hamlib / CAT /      DSP pipelines /     Reticulum /
      packet gateways     pass decoders       Meshtastic / mesh
            │                 │                    │
            └──────────── audited event bus ───────┘
```

The AI's output is a **typed mission request** — a JSON document against a fixed schema, not freeform commands (examples in [ai-agent.md](ai-agent.md)). The orchestrator is a normal deterministic service that validates each request against:

- **Policy** — band/mode/power allowlists, the configured operator license profile, transmit authorization state.
- **State** — device health, mission leases, rotator and TX arbitration, deployment status.
- **Legality** — is this emission permitted for this operator, here, now. Protected services are receive-only without specific authorization.
- **Power** — per-domain budget, battery state, what Tier 0 will allow.
- **Antennas** — is a compatible antenna connected, deployed, and safe to use (SWR, motion, payload identification).

Requests that pass are executed through hardware adapters; requests that fail are rejected with a machine-readable reason the AI can relay in plain language. Every request, decision, and hardware action lands on the audited event bus, so a mission can be reconstructed after the fact and the system can roll back to a safe state on any failure. The transmit-authorization gates themselves are specified in [safety-model.md](safety-model.md).

## 4. Four pillars mapped to subsystems

| Pillar | What it means | Primary subsystems |
|---|---|---|
| **Communicate** | Move a message for a person who doesn't know or care which radio does it. Multi-bearer messaging with AI-selected best bearer. | Messaging gateways (Meshtastic, Reticulum, packet/Winlink-class HF), VHF/UHF and HF transceivers (Tier 3), orchestrator best-bearer routing, message store-and-forward at Tier 1. |
| **Form networks** | Stand up connectivity for a group or a neighborhood when infrastructure is down or sparse. | Mesh gateway (HaLow/OpenMANET), deployable field relays, Meshtastic and Reticulum meshes, edge router segmentation, services published to mesh clients. |
| **Observe** | Understand the local RF environment: spectrum survey, signal identification, satellite reception, and satellite hunt for spacecraft whose state is uncertain. | SDR receive chain (Tier 1 low-power + Tier 2 high-capability), DSP toolchain, pass scheduler + TLE cache, local-sky map, signal classification and I/Q archive, profile-driven hunt missions ([satellite-profiles.md](satellite-profiles.md)). |
| **Serve** | Offer local content and services to whoever can reach the station: maps, an offline library, coordination tools. | Tier 1 service host + storage, mesh-facing service publication, offline content stores, local applications exposed through the mesh gateway. |

Each pillar is dual-use by design: the same station is a good everyday SDR/mesh/amateur-radio setup and an essential asset when infrastructure fails. Nothing in the architecture is emergency-only.

## 5. Hardware-neutral abstractions

Core code depends on interfaces, never on device models:

- `Receiver`, `Transmitter`, `DuplexRadio`
- `Rotator`, `AntennaPayload`
- `NetworkBearer`, `MessageTransport`
- `PowerDomain`
- `Decoder`
- `PositionSource`, `TimeSource`

A **station profile** binds these interfaces to a concrete build — which SBC, which radios, which SDRs, which mesh hardware, which power controller. The repository ships example profile shapes (vehicle station, portable station, home ground station); the Good Ancestor VW bus is maintained as the reference profile. Satellite contact parameters are likewise data, not code: a public example satellite profile ships in-repo (with more planned — weather, Inmarsat), and operators load private profiles for spacecraft they are authorized to work.

This is what makes the project reproducible: none of the core software requires the reference implementation's hardware, and supporting a new device means writing an adapter against a small interface, not forking the system.
