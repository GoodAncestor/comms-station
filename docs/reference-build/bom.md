# Reference Station — Bill of Materials

This is the equipment list for the reference-build design: an AI-managed
communications station, described generically so it can be reproduced on a
different vehicle, a trailer, or a fixed site. The design was validated on the
Good Ancestor VW bus ([ev.goodancestor.com](https://ev.goodancestor.com)), but
nothing here names a specific unit as *required* — every row describes a **role**
and gives an example model only to make the role concrete. Substitute any
hardware that fills the same role.

The list is organized by subsystem so a build can adopt subsystems
independently: mesh and monitoring without radios, receive without transmit,
satellite without HF, and so on. Nothing here is mandatory as a set; the class
column marks what the core architecture actually depends on.

> **Costs are indicative.** All cost bands are US$, snapshot 2026-07 — verify
> before purchase. Street prices for radios, SDRs, and mesh gear move with
> promotions, rebates, and stock; used-market prices for radio gear are often
> well below these bands. Bands cover the item as typically kitted (e.g. a dev
> board with its usual accessories), not shipping or tax.
>
> **Safety and commissioning gear can be borrowed.** Dummy loads,
> forward/reflected power (SWR) measurement, and a VNA/antenna analyzer are
> needed for commissioning, not for daily operation. Rather than buying this
> equipment up front, arrange *access* to it — borrowed or rented, or supplied
> by an installer or local radio club — before relying on automated
> transmission. Ownership is optional.

**Class column:** `core` = the core architecture depends on this role (any
hardware that fills the role works); `optional` = added per pillar or capability
as a build grows. Treat it as a dependency signal, not a shopping list. Amateur
*transmit* paths always require an appropriate license in your jurisdiction;
receive paths are license-free in most places, but check local rules.

---

## 1. Compute and control

| Item (example) | Role | Qty | Indicative cost band (US$) | Class |
|---|---|---:|---|---|
| Single-board mission controller with touchscreen (e.g. Raspberry Pi 5) | Primary mission controller: canonical state authority, dashboard, low-rate radio/rotator/network control | 1 | $150–250 | core |
| AI compute node (e.g. NVIDIA Jetson AGX Thor 128 GB; smaller Jetson-class or x86+GPU boxes also work) | Local AI model host, multimodal agent, high-rate SDR/DSP, signal classification and recording | 1 | $1,200–3,500 | optional |
| Microcontroller supervisor boards (e.g. ESP32 family) | Tier-0 power supervision: converter enables, current/voltage/temperature sensing, deployment sensors, watchdogs | 3–6 | $30–80 (set) | core |
| Secondary display for the AI node | Technical waterfall / decoder display; not needed for headless operation | 1 | $100–250 | optional |

## 2. Conventional radios and interfaces

| Item (example) | Role | Qty | Indicative cost band (US$) | Class |
|---|---|---:|---|---|
| Network/data-capable VHF/UHF FM mobile (e.g. VERO/VGC VR-N7600) | Everyday FM voice, APRS, packet/KISS; low-power always-available service radio | 1 | $250–350 | core |
| Compact 100 W HF/6 m all-mode (e.g. Icom IC-7100) | Compact HF: Winlink, regional and long-distance terrestrial links | 1 | $850–1,100 | optional (required only for the long-haul HF path) |
| Full-duplex VHF/UHF/23 cm all-mode (e.g. Icom IC-9700) | Automated full-duplex satellite work, VHF/UHF weak-signal, 23 cm | 1 | $2,000–2,300 | optional (required only for satellite *transmit*; receive-only builds use SDRs) |
| Handheld with APRS/GPS (e.g. Kenwood TH-D75A) | Independent portable field radio, handheld satellite work, backup when the vehicle station is down | 1 | $650–750 | optional |
| Portable HF/all-mode field radio (e.g. Yaesu FTX-1 Field or Icom IC-705 class) | Portable field kit; also exercises multi-vendor CAT automation in the orchestrator | 1 | $900–1,400 | optional |
| Deployable SHF/microwave transceiver, split RF+controller (e.g. Icom IC-905 class) | 1.2/2.4/5.6/10 GHz experimentation with RF unit mounted near the antenna | 1 | $2,500–4,000 | optional |
| Sound-card/PTT interface (e.g. DigiRig Mobile) | Reserve digital-modes interface for radios without native USB/network data paths | 1 | $50–70 | optional |

## 3. SDR and RF accessories

| Item (example) | Role | Qty | Indicative cost band (US$) | Class |
|---|---|---:|---|---|
| Low-cost RX-only SDR (e.g. RTL-SDR Blog V4) | Low-power scheduled receive on the mission controller; dish feed or fixed monitoring missions | 2–3 | $30–50 each | core (the minimum viable Observe pillar) |
| Mid-range full-duplex SDR (e.g. LimeSDR Mini 2.0) | **The baseline transmit-capable / satellite SDR:** 1×1 full-duplex, 10 MHz–3.5 GHz — covers the common mobile satellite bands (UHF / L / S) and drives the transmit chain; compact. Also serves as the wideband development SDR. | 1–2 | $350–450 | core for the satellite / transmit pillars |
| High-end dual-channel SDR (e.g. bladeRF 2.0 micro xA9) | **Optional, advanced only:** 2×2 phase-coherent capture (polarization diversity), coverage to ~6 GHz, and on-board FPGA processing. Physically larger than the Mini — specify only when coherent, above-3.5 GHz, or FPGA work is actually needed. | 0–1 | $900–1,100 | optional (advanced) |
| HF upconverter (e.g. NooElec Ham It Up Plus class) | HF receive on SDRs that start above HF | 1 | $60–90 | optional |
| Programmable signal generator / frequency converter (e.g. Othernet moRFeus class) | Closed-cable test source and frequency translation for SDR commissioning | 1 | $150–250 | optional |
| External regulated bias tee | Stable DC for active antenna feeds, independent of SDR driver state | 1 | $20–50 | core (if using active feeds) |
| Closed-cable test kit: DC block, 10/20 dB attenuators, short SMA jumpers (e.g. Mini-Circuits BLK-89-S+, VAT-20A+, VAT-10A+, 086-18SMRSM+) | Safe cabled testing of generators against receivers; no radiated signals | 1 set | $50–120 | core (before any generator-to-receiver testing) |
| RF limiters, filters, couplers | Receiver front-end protection near transmitters; band filtering | as needed | $150–400 (set) | core (for co-sited transmit + SDR receive) |
| Dummy load, SWR/power meter, VNA/antenna analyzer | Transmit commissioning and antenna verification | access to 1 each | $0 (borrow/rent) — $300–800 if purchased | core as *access*, not ownership (see note above) |

## 4. Satellite and antenna

| Item (example) | Role | Qty | Indicative cost band (US$) | Class |
|---|---|---:|---|---|
| Motorized L-band dish kit (e.g. KrakenRF Discovery Dish class) | Deployable dish for L-band satellite receive missions | 1 | $150–250 | optional |
| Azimuth/elevation tracking mount (e.g. Discovery Drive class) | Automated pass tracking for dish and antenna payloads | 1 | $250–350 | optional (strongly recommended for automated satellite work) |
| L-band active satellite feeds (weather, Inmarsat) | Band-specific active feeds for the dish | 2 | $50–100 each | optional |
| Dual-band satellite antenna, 2 m + 70 cm (e.g. Arrow 146/437-10BP) | Split-boom dual-band Yagi with independent feeds; primary initial automated satellite payload | 1 | $150–200 | optional |
| Cross-polarized 70 cm antenna (e.g. Arrow 437X14) | Two orthogonal 7-element arrays with independent feeds; polarization-diversity / circular-polarization development payload | 1 | $130–180 | optional |
| Polarization phasing network / 90° hybrid or RF switch | Combine cross-polarized feeds for switchable linear or RHCP/LHCP; band-specific, transmit-rated | 1 | $100–400 | optional |
| Mobile VHF/UHF whip + NMO mount and coax (e.g. Comet SBB-5NMO on a through-hole NMO base) | Permanent everyday antenna for the FM service radio | 1 | $100–160 | core |
| Dedicated 902–928 MHz HaLow antenna | Exterior antenna for the mesh anchor; physically separated from the Meshtastic antenna | 1 | $20–60 | core (for the Form-networks pillar) |
| Dedicated 915 MHz Meshtastic antenna | Exterior antenna for the low-rate messaging gateway; separated from HaLow despite the overlapping band | 1 | $15–50 | core (for the Communicate pillar) |
| Active multi-constellation GNSS antenna | Common position/time source for pass prediction, logging, and radio services | 1 | $20–60 | core |
| Roof rack / mast mounting platform | Parked-only antenna payload mounting | 1 | $300–800 | core (some elevated mounting for deployed antennas) |
| Coax runs, bulkheads, weatherproofing wrap, strain relief | Antenna-to-radio interconnect; measured and specified per installation | as needed | $100–300 | core |

## 5. Networking and mesh

| Item (example) | Role | Qty | Indicative cost band (US$) | Class |
|---|---|---:|---|---|
| Multi-WAN travel router (e.g. GL.iNet class) | Edge firewall, VPN, WAN failover policy, LAN segmentation; the network trust boundary | 1 | $100–250 | core |
| Managed Ethernet switch (VLAN-capable) | Core wired backbone and VLAN segmentation between compute, radio, and mesh domains | 1 | $50–200 | core |
| Satellite broadband terminal (e.g. Starlink Mini) | Optional WAN/backhaul where available | 1 | $300–500 (hardware) | optional |
| HaLow/OpenMANET anchor node — SBC + 802.11ah radio (e.g. Pi 5 + MM8108) | Vehicle's primary long-range Wi-Fi mesh anchor and gateway | 1 | $150–300 | core (for the Form-networks pillar) |
| Deployable HaLow relay/service node — SBC + 802.11ah radio, cased (e.g. Pi 4 + MM6108) | Drop-off mesh relays and service nodes extending coverage | 2+ | $150–250 each | optional |
| Additional generic mesh node — SBC for 802.11s/BATMAN infrastructure | Extra field relays, remote SDR/ADS-B hosts, store-and-forward and service endpoints | as needed | $100–250 each | optional |
| HaLow USB dongles / gateway boards (e.g. Heltec HaLow class) | End-device adapters, test nodes, auxiliary links; treat as auxiliary tier until interoperability is proven | several | $30–60 each | optional |
| Meshtastic devices | Low-rate text, position, alerts, telemetry; hand-out nodes for a team | 4+ | $30–80 each | core (cheapest path to the Communicate pillar) |
| Reticulum-capable LoRa boards / RNodes | Encrypted store-and-forward transport across LoRa, HaLow, serial, and IP | 2+ | $30–100 each | optional |

## 6. HF antenna kit (parked deployment)

Bundled separately because it is a self-contained kit added only when the
long-haul HF path is in scope; it depends on nothing else in the build. Aim for
at least two deployable configurations: a fast telescoping vertical, and a low
horizontal/sloping wire for regional NVIS coverage.

| Item (example) | Role | Qty | Indicative cost band (US$) | Class |
|---|---|---:|---|---|
| Remote automatic antenna tuner (e.g. Icom AH-730 class) | Matches a deployed wire or vertical at the feedpoint across HF bands | 1 | $400–650 | core (for the HF path) |
| Telescoping mast / support | Rapid vertical setup and wire support | 1 | $80–250 | core (for the HF path) |
| Wire element set + counterpoise / radials | Fast-vertical and NVIS/wire configurations | 1 set | $60–200 | core (for the HF path) |
| Common-mode choke / 1:1 current balun | Feedline decoupling and RF-in-the-shack control | 1 | $30–80 | core (for the HF path) |
| Weatherproof feedpoint box + labeled cables | Protected, repeatable field connections | 1 | $40–120 | optional |
| Ground / bonding kit | RF ground and lightning bonding appropriate to the platform | 1 | $50–200 | core (for the HF path) |
| HF feedline (coax) with connectors | Feedpoint-to-radio run; length measured per installation | as needed | $60–200 | core (for the HF path) |

## 7. Power

| Item (example) | Role | Qty | Indicative cost band (US$) | Class |
|---|---|---:|---|---|
| 12 V distribution panel with fusing | Central protected DC distribution for radios, compute, and mesh gear | 1 | $50–150 | core |
| DC-DC converters (per power tier, enable-controlled) | Isolated, individually switchable supplies so subsystems can be power-gated by the supervisor | 3–6 | $20–80 each | core |
| Current/voltage/temperature sensor boards | Telemetry inputs for the Tier-0 power supervisor | as needed | $30–100 (set) | core |
| Anderson/powerpole connectors, wiring, chassis bonding | Standardized DC interconnect and RF grounding/bonding | as needed | $50–200 | core |
| Portable battery box / auxiliary battery | Off-vehicle power for deployed relay nodes and field kits | 1+ | $150–500 | optional |

## 8. Mast-mounted SDR head (parked deployment)

An **optional** subsystem for stations that deploy a satellite dish/antenna and
want to digitize at the feed. It packages a small compute node and the
satellite SDR(s) into a weatherproof enclosure at the mast, so the lossy
high-band coax run is a few centimetres and the long cables back to the cabin
carry only Ethernet and power. The head is raised only while parked and stows
for transit (see the physical-zoning section of
[architecture.md](../architecture.md)). Within this group the enclosure, SBC,
SDR, and power feed are the `core` of the subsystem; the transmit-chain parts are
`optional`, added only when the head also *transmits* — for example full-duplex
satellite via the SDR (see [sdr-transmit-chain.md](../sdr-transmit-chain.md)).

| Item (example) | Role | Qty | Indicative cost band (US$) | Class |
|---|---|---:|---|---|
| Outdoor IP65 pole-mount electronics enclosure (e.g. KrakenRF Discovery Outdoor Enclosure class) | Weatherproof die-cast aluminium housing at the mast; thermal-pad heat path to the case, cable glands, pole clamp; holds the compute node + SDR(s) close to the feed | 1 | $80–180 | core (of this subsystem) |
| Dedicated single-board compute node | Mast-resident node: owns the dish/rotator control and the satellite SDR plane, runs light local decode so it works with the AI/DSP node off | 1 | $100–250 | core (of this subsystem) |
| Mast-resident satellite SDR(s) | The dish-feed / satellite-band SDR(s), digitizing inches from the feed; RX (and, with the transmit chain below, TX) | 1–2 | $30–200 each | core (of this subsystem) |
| PoE-or-12 V power feed to the head (PoE splitter/injector, or fused 12 V branch + weatherproof connectors) | Powers the head over the run from the cabin; a fused 12 V branch avoids a PoE power ceiling when the node plus several SDRs (and a possible amplifier) exceed it | 1 | $20–80 | core (of this subsystem) |
| Linear power amplifier, VHF/UHF (band-appropriate) | Transmit amplification for the SDR-driven transmit chain; runs hot — heatsink or mount outside the sealed enclosure | 1 | $150–500 | optional (SDR-transmit path only) |
| Band-pass + low-pass filters (band-appropriate) | Keep the SDR's transmit emission clean and in-band; protect co-sited receivers | 1 set | $50–200 | optional (SDR-transmit path only) |
| T/R sequencer | Orders switch/PA/PTT timing so nothing is hot-switched between receive and transmit | 1 | $50–150 | optional (SDR-transmit path only) |
| Directional coupler / SWR-power sensor | Forward/reflected power sensing for the transmit interlock and antenna verification at the feed | 1 | $30–150 | optional (SDR-transmit path only) |

---

## Reading this list for your own build

A minimum useful station — mesh, monitoring, and offline services, no transmit
licensing required — is roughly: the mission controller, one low-cost RX SDR,
the router, a mesh anchor of your choice (a commodity Wi-Fi / AREDN access point
or a Wi-Fi HaLow node), a few Meshtastic/LoRa nodes, and clean 12 V power. That
lands in the **$700–1,300** range and exercises most of the software.

Everything else is added per pillar: the compact HF radio and the HF antenna kit
for long-haul terrestrial links, the full-duplex all-mode radio plus a
satellite antenna and tracking mount for automated satellite work, the dish and
active feeds for L-band receive, and the AI compute node when local model
inference and high-rate DSP become the bottleneck. Amateur transmit paths
require an appropriate license in your jurisdiction; every receive path here is
license-free in most places, but check your local rules.
