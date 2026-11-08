<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Architecture

comms-station turns a vehicle — or any suitably equipped fixed site — into an AI-managed communications hub for disasters and off-grid operation, usable by people without radio skills. The onboard AI acts as the radio operator; a deterministic orchestrator validates and executes within legal and safety interlocks.

The design rule that everything else follows from:

> **The AI proposes; deterministic services validate and execute.**

The model never touches hardware directly. Every action flows through a typed request that a conventional, auditable service checks against policy, state, legality, power, and antenna constraints before anything keys up, rotates, or draws current.

A second rule shapes the RF front end specifically:

> **The baseline station is an SDR and parts; proprietary transceivers are optional upgrades.**

The reproducible design requires only a software-defined radio plus supporting components — never a particular manufacturer's transceiver — so the station can be built cheaply and reproduced anywhere. An SDR paired with a transmit chain (amplification, band-pass and low-pass filtering, T/R sequencing, and SWR/power protection — see [sdr-transmit-chain.md](sdr-transmit-chain.md)) covers all receive, scan, and decode work, and can even cover full-duplex satellite transmit, since full-duplex is native to an SDR. A station **MAY** add a proven proprietary appliance where transmit power, reliability, or legality make it worth the cost — the reference build, for example, keeps a 100 W HF radio and an always-on FM radio — but the open design never *requires* one. Where this document names an example model, read it as one way to fill a role, not a dependency.

This document is the **map**. It describes the system in four parts — the tiered power-and-control architecture, the communications topology, the canonical-state command flow, and how the project's four pillars map onto subsystems — and points to the sibling documents that treat each subsystem in depth. Read it to understand how the pieces fit; follow the links in [See also](#see-also) for the detail behind any one of them.

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

Two things this section deliberately leaves as roles are treated in full elsewhere: the electrical layer beneath the tiers — Tier 0 supervision, per-domain switching, budgeting, and load-shedding — is detailed in [power.md](power.md), and the conventional-radio and SDR subsystems that populate Tiers 2 and 3 are detailed in [radios.md](radios.md).

### Physical zoning — where things live

The tiers order components by *criticality*. A second, complementary partition orders them by *physical placement*, driven by two questions: **is this component available while the station is mobile, and does its job benefit from height or a short RF path?** A station **MAY** organize its build into three physical zones:

```text
ZONE A — CABIN / ALWAYS-ON  (works while moving; small permanent antennas only)
  mission controller (canonical state, orchestrator, operator UI)
  always-on FM / APRS radio on a small permanent antenna
  a scanning SDR for listen-while-driving wideband receive
  edge router + WAN
  an always-on low-rate mesh node (LoRa-class)
          ┆  Ethernet + fused 12 V
ZONE B — MAST-DEPLOY ENCLOSURE  (raised only when parked; stows for transit)
  a dedicated compute node owning the dish / rotator
  the satellite SDR(s), digitizing at the feed
  the high-throughput mesh anchor (benefits from height)
  feed LNA / bias-tee; optional SDR transmit chain
          ┆  power-gated
ZONE C — AI / DSP COMPUTE NODE  (shut-down-able)
  local models, voice agent, retrieval
  heavy DSP: wideband survey, GNU Radio, classification, I/Q recording
  higher-capability / experimental SDRs attached directly here
```

- **Zone A — cabin / always-on.** Everything that must work while the vehicle is moving, with no deployment step: the mission controller, an always-on low-power FM/APRS radio on a small permanent antenna, a scanning SDR for wideband receive on the road, the edge router and WAN, and an always-on low-rate mesh node. Small, permanently mounted antennas only.

- **Zone B — mast-deploy enclosure.** A self-contained outdoor module, raised on the mast **only when parked** and stowed inside the vehicle when mobile. It houses a dedicated compute node that owns the dish and rotator, the satellite SDR(s), and the high-throughput mesh anchor that benefits from height. The RF design principle is **digitize at the feed**: mounting the SDR inches from the dish feed keeps the lossy high-band coax run to a few centimetres, so the long cables back to the cabin carry only Ethernet (data) and a **fused 12 V power branch** — no RF loss, and Ethernet is indifferent to length. Power comes from that fused 12 V branch plus Ethernet, **not necessarily PoE**: a compute node with several SDRs (and possibly a transmit amplifier) can exceed a PoE budget, so a direct 12 V feed gives headroom. Deploy with the dish and antennas up when parked; unplug and pack the whole module when moving.

- **Zone C — AI / DSP compute node.** The power-gated heavy-compute node: local models and voice agent, plus heavy DSP — wideband survey, GNU Radio, signal classification, large I/Q recording. It is shut down cleanly when its capabilities are not wanted, and nothing always-on depends on it.

**SDR-to-compute placement is flexible and per-task.** There is no single boundary: put each SDR where its processing runs. The mast/dish SDRs live on the mast enclosure's compute node (digitize at the feed, decode locally, forward products). Heavy-DSP or experimental SDRs attach **directly to the AI/DSP compute node** over USB, where the horsepower lives. Both topologies coexist; the only caveat is not streaming raw wideband I/Q over the network when it can be decoded locally and forwarded as products.

The three physical zones map loosely onto the tiers — Zone A is Tier 1 (plus its always-on Tier 3 FM radio), Zone C is Tier 2 — but the mast enclosure deliberately crosses tiers: it carries an always-on-when-deployed control role *and* power-gated receivers in one weatherproof box, because RF logic (short feed, height) dictates the packaging more than criticality does.

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

The diagram above is the shape, not the wiring. The full network design — edge routing and WAN-failover policy, LAN/VLAN segmentation, and the mesh tier (HaLow/OpenMANET, Meshtastic, Reticulum) with its control/data-plane separation — lives in [networking.md](networking.md).

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

A **station profile** binds these interfaces to a concrete build — which SBC, which radios, which SDRs, which mesh hardware, which power controller. The repository ships example profile shapes (vehicle station, portable station, home ground station); the Good Ancestor VW bus is maintained as the reference profile. Satellite contact parameters are likewise data, not code: public example satellite profiles ship in-repo (amateur and weather; Inmarsat planned), and operators load private profiles for spacecraft they are authorized to work.

This is what makes the project reproducible: none of the core software requires the reference implementation's hardware, and supporting a new device means writing an adapter against a small interface, not forking the system.

## See also

This document is the map; each subsystem it names has its own detailed treatment. Nothing below is duplicated here — follow the link for depth.

- [networking.md](networking.md) — the communications topology in full: edge routing and WAN-failover policy, LAN/VLAN segmentation, the mesh tier (HaLow/OpenMANET, Meshtastic, Reticulum), and the control/data-plane firewall boundary.
- [radios.md](radios.md) — the conventional-radio and SDR subsystems behind Tiers 2 and 3: role assignments, control paths (CAT/CI-V/Hamlib, USB, LAN), and the receive and transmit chains.
- [sdr-transmit-chain.md](sdr-transmit-chain.md) — how an SDR becomes a real transmitter: the amplification, band-pass/low-pass filtering, T/R sequencing, and SWR/power-protection stages that turn SDR baseband into a filtered, legal, protected emission.
- [power.md](power.md) — the electrical architecture beneath the tiers: Tier 0 supervision, per-domain switching and budgeting, and graceful load-shedding.
- [safety-model.md](safety-model.md) — the deployment state machine, the stacked transmit-authorization gates, and the prompt-injection stance that keeps received content from becoming instructions.
- [ai-agent.md](ai-agent.md) — what the model does and does not do, and the typed mission-request interface it uses to reach the orchestrator.
- [satellite-profiles.md](satellite-profiles.md) — the profile type system, the satellite-hunt mission type, and the local-sky map.
- [roadmap.md](roadmap.md) — the build phases, ordered by dependency, and where the project currently stands.
- [reference-build/bom.md](reference-build/bom.md) — the reference-station bill of materials, organized by subsystem, with indicative cost bands.
