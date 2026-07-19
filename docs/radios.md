<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Radios and SDRs

A comms-station's job is to reach people and spacecraft over whatever bearer is
available, so its RF front end is deliberately plural: several transmitters and
receivers, each specialized, coordinated by the deterministic orchestrator
rather than by any one radio's own logic. This document describes that front end
**by role**, not by product. Any hardware that fills a role works; example
models appear only in parentheses to make a role concrete, and are never
requirements. A station picks one device per role, or fills a role with what it
already owns.

The roles divide into four transceiver classes and a set of receive-only
software-defined radios:

1. An always-on, low-power **FM / APRS / packet** radio — the service that stays
   up when everything else is off.
2. An **HF** radio for infrastructure-independent long-haul (Winlink, NVIS,
   DX), fed by a large antenna deployed only while parked.
3. A **VHF/UHF all-mode satellite** radio — full-duplex, for automated satellite
   work.
4. **SDRs** for wideband receive, scanning, I/Q capture, DSP, and
   classification.

Two cross-cutting concerns bind them together: **antennas and receiver
protection** (§5), because the transmitters sit next to sensitive receivers; and
the **control model** (§6), because the whole point of the project is that an AI
proposes and deterministic services execute.

The classes are not redundant. Each is the right tool for a different job, and a
station that has all four can pick the correct bearer — automatically — for the
mission at hand rather than forcing every task through one appliance.

## 1. Always-on FM / APRS / packet radio

The baseline bearer. This is a compact, low-current VHF/UHF FM mobile radio
(such as a VERO VR-N7600) that stays powered when the AI compute, the WAN
uplink, and the high-power radios are all shut down. It is the station's
always-available voice and low-rate data path.

Role:

- Everyday 2 m / 70 cm FM voice and repeater work.
- APRS position, telemetry, and messaging.
- KISS packet — a local packet BBS, Winlink-over-packet, and store-and-forward
  experiments.
- Automated status and notification traffic driven by the mission controller.
- The radio that still works when the AI tier is off.

Because it is always on, it should draw little standby current, connect to the
mission controller over a low-overhead link (USB serial or a supervised
Bluetooth bond with a documented recovery procedure), and expose packet/KISS so
the station's data services can use it without a separate modem. A dedicated,
permanently mounted dual-band antenna (see §5) suits its always-on duty.

Keep one independent handheld (such as a Kenwood TH-D75A) *outside* the
automated system as a portable, self-contained field and backup radio with its
own APRS/GPS. Its value is precisely that it is not tied to the station
computer; do not permanently bind it.

## 2. HF radio — infrastructure-independent long-haul

HF is the bearer that needs no repeater, no cell tower, no satellite, and no
internet. It is how the station reaches beyond line of sight when every local
network is down. A 100 W HF/6 m transceiver fills this role; two packaging
styles both work well in a vehicle:

- A **compact split-body** radio (such as an Icom IC-7100) — a hidden main unit
  with a small detachable control head, well suited to concealed mobile
  installation, typically also covering VHF/UHF all-mode as a backup.
- A **modern single-box HF radio** (such as an Icom IC-7300MK2) — a larger
  rack-style chassis, chosen when a LAN control port, a current-generation
  direct-sampling receiver, and a built-in tuner matter more than minimum
  packaging.

Missions:

- Winlink email over HF.
- Regional NVIS communication on appropriate bands.
- Long-distance SSB / CW / digital contacts and nets.
- HF propagation surveys and beacon monitoring.
- A redundant long-range text path when IP networks fail.

### The HF antenna is large and parked-only

HF's defining constraint is mechanical. An effective HF antenna is physically
large, and it is **deployed only while the vehicle is parked** — it is not a
drive-around antenna. A radio's internal tuner handles modest mismatch but is
not a general random-wire tuner; a proper HF deployment adds a **remote
automatic antenna tuner** (such as an Icom AH-730 or equivalent) at the antenna
feedpoint, plus a real ground/counterpoise system.

Provide at least two deployable configurations so the operator can trade setup
speed against coverage:

1. **Fast vertical** — a telescoping mast or whip with a counterpoise, for rapid
   setup.
2. **NVIS / wire** — a low horizontal or sloping wire for regional coverage
   where terrain and space allow.

The AI may request a band and a physical antenna configuration, but it must not
assume the same wire geometry is safe or efficient on every band: each band
needs tuner and SWR confirmation before transmit. Deployment, verification, and
TX-arming follow the state machine in [safety-model.md](safety-model.md).

## 3. VHF/UHF all-mode satellite radio

Automated satellite work has requirements a general-purpose radio does not meet,
so it earns a dedicated class: a **full-duplex, all-mode VHF/UHF** transceiver
(such as an Icom IC-9700) with separate antenna ports per band and computer
control. Full-duplex — transmitting on one band while receiving your own
downlink on another — is what makes disciplined, automated transponder operation
possible; a radio that cannot hear itself while transmitting cannot close the
loop.

What this class provides that the SDRs do not:

- A filtered, amplified, protected transmit chain on the amateur satellite
  bands.
- Full-duplex cross-band operation with independent 2 m / 70 cm (and, on some
  radios, 23 cm) antenna connectors.
- Built-in satellite tracking helpers — normal/reverse transponder tracking,
  AFC, satellite memories — that the control software can drive.
- Computer control (CI-V and/or a network control port) suitable for automated
  Doppler correction and pass execution.

Treat this radio as a **deterministic RF appliance**, not the primary
spectrum-discovery receiver. It excels at operating known satellites on known
bands; the SDRs (§4) do the wideband searching, arbitrary demodulation, and
classification. During commissioning, run automated-control tests at low power
into a dummy load before any over-the-air transmission, and add receiver
protection and a transmit-inhibit interlock before it shares antenna real estate
with nearby SDRs.

A single all-band portable (such as an Icom IC-705 or Yaesu FTX-1 Field) is a
useful *optional* second-vendor development and field radio — handy for
validating that the open control stack can drive more than one manufacturer's
CAT dialect — but it is not a substitute for a dedicated full-duplex satellite
radio, and need not be permanently installed.

## 4. SDRs — wideband receive, scanning, capture, DSP, classification

Software-defined radios are the station's eyes on the spectrum. Where the
transceivers operate *known* signals on *specific* bands, the SDRs discover,
record, and analyze *anything* — and they feed the AI's signal-identification
and satellite-hunt missions. Rather than one do-everything SDR, split the role
by capability tier so the low-power path can run unattended while the
high-capability path is available only when the AI/DSP tier is powered:

- **Low-power scheduled receiver.** An inexpensive receive-only dongle (such as
  an RTL-SDR Blog V4) attached to the always-on mission controller, running
  scheduled receive missions — satellite passes, ADS-B, AIS, weather, general
  band monitoring — without waking the high-power compute. Plan for **more than
  one** cheap receiver so a single unit is not constantly repurposed between
  missions.
- **High-capability development SDRs.** One or more wider-bandwidth,
  full-duplex-capable SDRs (such as a LimeSDR Mini or a bladeRF micro) on the
  AI/DSP compute tier, for spectrum surveys, arbitrary demodulators, multi-
  channel and coherent reception, higher-rate I/Q capture, and experimental
  waveforms. A dual-receive SDR sharing one local oscillator additionally
  enables phase-coherent work — for example, feeding two orthogonal antenna
  planes to synthesize or select polarization in software.

What the SDRs do better than the transceivers:

- Wideband surveys and blind search across large spans.
- Arbitrary, swappable demodulators and experimental modes.
- I/Q recording for offline and AI-assisted analysis.
- Multiple parallel channels and coherent multi-antenna reception.
- Reception outside the transceivers' amateur bands.
- Feeding a signal-classification and archive pipeline.

Supporting accessories belong to specific chains and should not be inserted
blindly: an **HF upconverter** (such as a NooElec Ham It Up) belongs only in an
HF receive path, never in a satellite path; a **regulated external bias tee** is
preferred over an SDR's internal bias tee for stable, predictable power to an
active antenna feed during unattended operation; and a **signal-generator /
frequency-converter** device (such as an Othernet moRFeus) is valuable for
closed-cable receiver and pipeline self-tests. Any such generator is a
**receive-side test tool only** — never connect a transmitter's output to it;
its input handles a few tens of milliwatts, orders of magnitude below any
amateur transmitter, and always test through fixed attenuators and a DC block
into a closed cable, never over the air.

An SDR's raw transmit capability is **not** a production transmit path. Turning
an SDR into a transmitter that leaves an antenna requires band-specific
filtering, amplification, sequencing, power/SWR monitoring, and receiver
protection — the very subsystem the dedicated transceivers already provide. In
this architecture SDRs are receive-and-analyze instruments; the licensed
transceivers do the transmitting.

## 5. Antennas and receiver protection

Because several transmitters share a vehicle with sensitive receivers, antennas
are a coexistence problem, not an afterthought. Two ideas govern the design:
**co-siting** (transmitters and receivers packed close together will desensitize
and can damage each other) and **one high-power transmitter at a time**.

Divide antennas by whether the vehicle can move with them:

- **Permanently mounted, small antennas** — appropriate where they are
  mechanically and electromagnetically sound. Typical permanent set: a dual-band
  NMO antenna for the always-on FM radio (a proper metal NMO mount and low-loss
  coax, not a permanent magnetic mount); separate, physically spaced antennas
  for HaLow and Meshtastic even though their bands overlap; and an active GNSS
  antenna feeding common position/time to the pass scheduler, logs, and radio
  services.
- **Stored, deployable antennas** — mounted to the roof rack or a mast **only
  while parked**: the large HF antenna and tuner (§2), directional satellite
  arrays, 23 cm and any microwave antennas, and dedicated receive antennas
  (ADS-B, AIS, weather). These are stored inside the vehicle in transit and
  raised for a mission.

Every deployable payload must be **identified before use**. The orchestrator
reads a payload's identity (via a keyed cable, 1-Wire EEPROM, coded resistor,
NFC tag, DC signature, camera check, or operator confirmation) and looks up its
frequency range, polarization, allowed receive-power/bias, maximum transmit
power, expected connector, rotator and wind limits, decoder profiles, required
filters, and calibration offsets. Running a mission against an unidentified
antenna is not permitted — it risks both hardware and legality.

Receiver protection is layered and deliberately not software-only, because an
expensive receive port must survive even a total software failure:

- One central **transmit-state bus** and a hardware **PTT-inhibit** line, so
  only one high-power transmitter can be keyed at a time and nearby receivers
  are muted or bypassed before RF appears.
- **RF-sensing** on major transmit feeds and **automatic LNA/bias shutdown**
  ahead of nearby transmission.
- **Band-specific filters** and **limiters** on vulnerable receive inputs.
- **Physical antenna separation** and **dedicated antennas** in preference to
  unverified RF combining or generic band switches.
- A labeled **coax bulkhead panel**, so connections are unambiguous during
  parked deployment.
- **Dummy-load-first commissioning**: measure desensitization and overload with
  each transmitter at low, then full, power before trusting a shared
  installation.

These are the physical counterpart to the transmit-authorization gates in
[safety-model.md](safety-model.md): the gates decide *whether* to transmit; the
hardware here bounds what a transmission can do to everything nearby.

## 6. Control model

Every radio and SDR in this document is a device the station drives through a
uniform, auditable path. The rule is the project's constant:

> **The AI proposes missions; deterministic services validate and execute
> them.**

The model never keys PTT, energizes a relay, drives a rotator, or writes
arbitrary bytes to a radio. It emits a **typed mission request**, and a
deterministic **communications orchestrator** decides whether to carry it out —
checking power, antenna identity, legal transmit ranges, vehicle and deployment
state, device health, mission ownership, and operator authorization. The full
transmit-authorization gates and the deployment state machine live in
[safety-model.md](safety-model.md).

Radios are reached through standard control interfaces behind that orchestrator:

- **Hamlib `rigctld`** for common transceiver control across manufacturers —
  the portable default.
- Direct **CI-V** (or the relevant vendor **CAT** protocol) for functions a
  generic layer does not expose reliably; the architecture keeps this vendor
  support present regardless of which radios a station actually owns.
- A radio's **network control port** as the primary path where it has one, with
  **USB/serial** as the fallback and maintenance path.
- Human-facing tools (such as `wfview`) for testing and visualization, and any
  vendor's proprietary remote-control software only as an optional reference/
  validation path — never a runtime dependency.

SDRs are driven through their own adapter layer (SoapySDR and the SDR/decoder
applications — SatDump, GNU Radio, SDRangel and similar), again behind the
orchestrator. Each radio and SDR adapter runs as an **isolated service** with
only the device access it needs, so a misbehaving decoder cannot reach a
transmitter and no single compromised component can escalate. Every control
action — every tune, key, relay, and rotator command — lands on the audited
event bus.

The payoff of one audited control path is uniformity: the AI, the touchscreen,
the CLI, and any authorized remote client are interchangeable clients of the
same typed interface, and adding or swapping a radio means writing one adapter,
not rewiring the trust model.

## Related documents

- [architecture.md](architecture.md) — the tiered power-and-control
  architecture and the canonical-state command flow these radios sit inside.
- [safety-model.md](safety-model.md) — the deployment state machine, transmit-
  authorization gates, and service isolation that bound every transmission.
- [ai-agent.md](ai-agent.md) — what the model does and does not do, and how its
  typed tool requests meet the control path.
- [satellite-profiles.md](satellite-profiles.md) — how the station knows what to
  receive and how to hunt for spacecraft, consumed by the satellite radio and
  SDR chains.
