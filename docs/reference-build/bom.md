# Reference Station — Bill of Materials

This is the equipment list for the reference station design: an AI-managed
communications station as validated on the Good Ancestor VW bus
([ev.goodancestor.com](https://ev.goodancestor.com)). It is organized by
subsystem so that other builds — a different vehicle, a trailer, a fixed site —
can adopt subsystems independently. Nothing here is mandatory as a set; the
required/optional column marks what the core architecture actually depends on.

> **Costs are indicative.** All cost bands are US$, snapshot 2026-07 — verify
> before purchase. Street prices for radios and SDRs move with promotions,
> rebates, and stock; used-market prices for the radio gear are often well below
> these bands. Bands cover the item as typically kitted (e.g. a dev board with
> its usual accessories), not shipping or tax.
>
> **Safety and commissioning gear can be borrowed.** Dummy loads,
> forward/reflected power (SWR) measurement, and a VNA/antenna analyzer are
> needed for commissioning, not for daily operation. Rather than buying this
> equipment up front, arrange *access* to it — borrowed or rented, or supplied
> by an installer or local radio club — before relying on automated
> transmission. Ownership is optional.

**Class column:** `core` = the core architecture depends on this role (any
hardware that fills the role works); `optional` = added per pillar or
capability as a build grows. Treat it as a dependency signal, not a shopping
list.

---

## 1. Compute and control

| Item | Role | Qty | Indicative cost band (US$) | Required? | Class |
|---|---|---:|---|---|---|
| Raspberry Pi 5 with touchscreen | Primary mission controller: canonical state authority, dashboard, low-rate radio/rotator/network control | 1 | $150–250 | Required | core |
| NVIDIA Jetson AGX Thor (128 GB) | Local AI model host, multimodal agent, high-rate SDR/DSP, signal classification and recording | 1 | $3,000–3,500 | Optional (any capable AI compute node works; smaller Jetson-class or x86+GPU boxes are viable) | optional |
| ESP32-family boards | Tier-0 power supervision: converter enables, current/voltage/temperature sensing, deployment sensors, watchdogs | 3–6 | $30–80 (set) | Required | core |
| Secondary display for AI node | Technical waterfall / decoder display; not needed for headless operation | 1 | $100–250 | Optional | optional |

## 2. Conventional radios and interfaces

| Item | Role | Qty | Indicative cost band (US$) | Required? | Class |
|---|---|---:|---|---|---|
| VERO/VGC VR-N7600 (or similar network-controllable VHF/UHF FM mobile) | Everyday FM voice, APRS, packet/KISS; low-power always-available service radio | 1 | $250–350 | Required (some VHF/UHF FM radio with a data/control interface) | core |
| Icom IC-7100 (or similar compact 100 W HF/6 m + VHF/UHF all-mode) | Compact HF: Winlink, regional and long-distance terrestrial links | 1 | $850–1,100 | Optional (required only for long-haul HF links under the Communicate pillar) | optional |
| Icom IC-9700 (or similar full-duplex VHF/UHF/23 cm all-mode) | Automated full-duplex satellite work, VHF/UHF weak-signal, 23 cm | 1 | $2,000–2,300 | Optional (required only for satellite *transmit*; receive-only builds use SDRs) | optional |
| Handheld with APRS/GPS (e.g. Kenwood TH-D75A) | Independent portable field radio, handheld satellite work, backup when the vehicle station is down | 1 | $650–750 | Optional | optional |
| Sound-card/PTT interface (e.g. DigiRig Mobile) | Reserve digital-modes interface for radios without native USB/network data paths | 1 | $50–70 | Optional | optional |
| Portable HF/all-mode field radio (e.g. Yaesu FTX-1 Field class) | Portable field kit; also exercises multi-vendor CAT automation in the orchestrator | 1 | $1,100–1,400 | Optional | optional |

## 3. SDR and RF accessories

| Item | Role | Qty | Indicative cost band (US$) | Required? | Class |
|---|---|---:|---|---|---|
| RTL-SDR (e.g. RTL-SDR Blog V4) | Low-power scheduled receive on the mission controller; dish feed or fixed monitoring missions | 1 | $30–50 | Required (the minimum viable Observe pillar) | core |
| Mid-range full-duplex SDR (e.g. LimeSDR Mini 2.0) | Wideband development SDR on the AI node; 1×1 full-duplex to ~3.5 GHz | 1 | $350–450 | Optional | optional |
| High-end dual-channel SDR (e.g. bladeRF 2.0 micro xA9) | Dual-channel coherent capture, higher bandwidth, FPGA offload; polarization-diversity experiments | 1 | $900–1,100 | Optional | optional |
| HF upconverter (e.g. Ham It Up Plus class) | HF receive on SDRs that start above HF | 1 | $60–90 | Optional | optional |
| Programmable signal generator / frequency converter (e.g. moRFeus class) | Closed-cable test source and frequency translation for SDR commissioning | 1 | $150–250 | Optional | optional |
| External regulated bias tee | Stable DC for active antenna feeds, independent of SDR driver state | 1 | $20–50 | Required (if using active feeds) | core |
| Closed-cable test kit: DC block, 10/20 dB attenuators, short SMA jumpers | Safe cabled testing of generators against receivers; no radiated signals | 1 set | $50–120 | Required (before any generator-to-receiver testing) | core |
| RF limiters, filters, couplers | Receiver front-end protection near transmitters; band filtering | as needed | $150–400 (set) | Required (for co-sited transmit + SDR receive) | core |
| Dummy load, SWR/power meter, VNA/antenna analyzer | Transmit commissioning and antenna verification | access to 1 each | $0 (borrow/rent) — $300–800 if purchased | Required as *access*, not ownership (see note above) | core |

## 4. Satellite and antenna

| Item | Role | Qty | Indicative cost band (US$) | Required? | Class |
|---|---|---:|---|---|---|
| Motorized L-band dish kit (e.g. Discovery Dish class) | Deployable dish for L-band satellite receive missions | 1 | $150–250 | Optional | optional |
| Azimuth/elevation tracking mount (e.g. Discovery Drive class) | Automated pass tracking for dish and antenna payloads | 1 | $250–350 | Optional (strongly recommended for automated satellite work) | optional |
| L-band satellite feeds (weather, Inmarsat) | Band-specific active feeds for the dish | 2 | $50–100 each | Optional | optional |
| Dual-band satellite antenna (e.g. Arrow 146/437-10BP) | 2 m + 70 cm split-boom antenna; primary initial automated satellite payload | 1 | $150–200 | Optional | optional |
| Cross-polarized 70 cm antenna (e.g. Arrow 437X14) | Polarization-diversity and circular-polarization development payload | 1 | $130–180 | Optional | optional |
| Roof rack / mast mounting platform | Parked-only antenna payload mounting | 1 | $300–800 | Required (some elevated mounting for deployed antennas) | core |
| Mobile VHF/UHF whip + NMO mount and coax | Permanent everyday antenna for the FM service radio | 1 | $100–160 | Required | core |
| Coax runs, bulkheads, weatherproofing wrap, strain relief | Antenna-to-radio interconnect; measured and specified per installation | as needed | $100–300 | Required | core |

## 5. Networking and mesh

| Item | Role | Qty | Indicative cost band (US$) | Required? | Class |
|---|---|---:|---|---|---|
| Satellite broadband terminal (e.g. Starlink Mini) | Optional WAN/backhaul where available | 1 | $300–500 (hardware) | Optional | optional |
| Multi-WAN travel router (GL.iNet class) | Edge firewall, VPN, WAN failover policy, LAN segmentation | 1 | $100–250 | Required | core |
| HaLow/OpenMANET anchor node (Pi 5 + 802.11ah radio) | Vehicle's primary long-range Wi-Fi mesh anchor | 1 | $150–300 | Required (for the Form-networks pillar) | core |
| Deployable HaLow relay nodes (Pi 4 + 802.11ah radio, cased) | Drop-off mesh relays and service nodes extending coverage | 2+ | $150–250 each | Optional | optional |
| Additional OpenMANET Pi nodes | Extra 802.11ah/802.11s mesh infrastructure | as needed | $100–250 each | Optional | optional |
| HaLow USB dongles / gateway boards | End-device adapters, test nodes, auxiliary links | several | $30–60 each | Optional | optional |
| Meshtastic devices | Low-rate text, position, alerts, telemetry; hand-out nodes for a team | 4+ | $30–80 each | Required (cheapest path to the Communicate pillar) | core |
| Reticulum-capable LoRa boards / RNodes | Encrypted store-and-forward transport across LoRa, HaLow, serial, and IP | 2+ | $30–100 each | Optional | optional |

## 6. Power

| Item | Role | Qty | Indicative cost band (US$) | Required? | Class |
|---|---|---:|---|---|---|
| 12 V distribution panel with fusing | Central protected DC distribution for radios, compute, and mesh gear | 1 | $50–150 | Required | core |
| DC-DC converters (per power tier, enable-controlled) | Isolated, individually switchable supplies so subsystems can be power-gated by the supervisor | 3–6 | $20–80 each | Required | core |
| Current/voltage/temperature sensor boards | Telemetry inputs for the Tier-0 power supervisor | as needed | $30–100 (set) | Required | core |
| Anderson/powerpole connectors, wiring, chassis bonding | Standardized DC interconnect and RF grounding/bonding | as needed | $50–200 | Required | core |
| Portable battery box / auxiliary battery | Off-vehicle power for deployed relay nodes and field kits | 1+ | $150–500 | Optional | optional |

---

## Reading this list for your own build

A minimum useful station — mesh, monitoring, and offline services, no
transmit licensing required — is roughly: the mission controller, one RTL-SDR,
the router, the HaLow anchor, a few Meshtastic nodes, and clean 12 V power.
That lands in the **$700–1,300** range and exercises most of the software.

Everything else is added per pillar: HF radio for long-haul terrestrial links,
the full-duplex all-mode radio for satellite transmit, the dish and tracking
mount for automated L-band receive, and the AI compute node when local model
inference and high-rate DSP become the bottleneck. Amateur transmit paths
require an appropriate license in your jurisdiction; every receive path here is
license-free in most places, but check your local rules.
