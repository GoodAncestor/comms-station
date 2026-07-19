<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Networking and Mesh Stack

A comms-station's second pillar is **Form networks**: stand up connectivity for a group or a neighborhood when infrastructure is down or sparse, and give *other people* access to it. The station is a network anchor, not just a terminal — it deploys relays outward and publishes services inward.

This document describes the networking stack by role, so a builder can assemble it from whatever hardware is accessible. No single bearer is required. A useful station can be built entirely from commodity Wi-Fi and LoRa; higher-throughput bearers are an upgrade, not a prerequisite. The layers stack like this:

```text
  SERVICES            Mumble voice · ATAK/CoT · maps · Archive · dashboards
                              │
  SECURE MESSAGING    Reticulum / LXMF  (encrypted, identity-based, store-and-forward)
                              │
  IP MESH + BEARERS   commodity P2P Wi-Fi / AREDN · Wi-Fi HaLow (OpenMANET) · Meshtastic/LoRa
                              │
  WAN EDGE            multi-WAN router · firewall · segmentation · optional satellite uplink
```

Everything below the WAN edge works with no Internet connection. The WAN is one more bearer — useful when present, never assumed.

The mesh itself spans **two roles distinguished by availability, not by bearer**:

- An **always-on, low-rate mesh** (Meshtastic/LoRa-class) that runs whenever the station is powered — including *while mobile*. It is cheap and low-power enough that keeping it up costs almost nothing, so team position, text, and alerts flow on the road with no deployment step and no mast.
- A **high-throughput mesh anchor** (Wi-Fi HaLow / AREDN-class) that carries real IP traffic but **benefits from height** — so it is raised on the mast only when the station is parked and deployed, and stows for transit.

This split is bearer-agnostic: the roles are "always-on low-rate, works moving" and "high-throughput, wants elevation, deployed when parked." Any radio that fills a role works. A station can run either alone, or both — the reference build runs both.

Companion documents: the [architecture](architecture.md) places this stack in the tiered system; the [safety model](safety-model.md) covers the control-plane isolation these principles enforce.

## 1. Accessible bearers most builders start with

Two bearers cover the majority of real deployments and need no exotic hardware. A first build can and often should stop here.

### Point-to-point Wi-Fi and AREDN

Commodity 2.4/5 GHz Wi-Fi radios — the ubiquitous outdoor CPE and sector units — give the cheapest high-throughput links available. Two paths:

- **Plain point-to-point / point-to-multipoint Wi-Fi.** Directional links between the station and elevated relays or camp access points. Standard gear, standard tooling, tens of Mbps over usable distances with line of sight.
- **AREDN (Amateur Radio Emergency Data Network).** The same class of hardware reflashed with mesh firmware that operates in the amateur portions of the 2.4/3.4/5.8 GHz bands under an amateur license. AREDN gives a self-configuring, self-healing IP mesh with an established ecosystem of services (chat, tunnels, mapping) and — because it runs in amateur spectrum — more permissive power and antenna options than Part 15 Wi-Fi, at the cost of requiring licensed operators and being receive-and-transmit under those rules.

Both are excellent where line of sight and elevation are available. Their weakness is exactly that dependence: throughput falls off hard without a clear path, and 2.4/5 GHz does not go through terrain or foliage well.

### Meshtastic over LoRa

Where Wi-Fi cannot reach, **Meshtastic over LoRa** carries low-rate text, position, and telemetry across kilometres at milliwatt power on 900 MHz-class ISM bands (region-dependent). It is the most accessible bearer of all — inexpensive nodes, battery-friendly, no license required in most regions — and it degrades gracefully where everything faster has failed.

Meshtastic is treated as a **separate low-rate bearer, not an IP transport**. It is deliberately *not* bridged transparently into the station LAN. Its role is short text, positions, alerts, battery/temperature telemetry, rendezvous ("return to the station"), network-outage notification, and status/pass reports. It can also carry *requests* — but only ones that map to predefined commands and pass the normal orchestrator policy engine ([safety-model.md](safety-model.md)); no unrestricted station or radio control is permitted over the mesh.

Recommended station gateway pattern:

```text
Meshtastic node
  → USB serial (not Bluetooth for the permanent gateway)
  → mission controller (Tier 1)
  → Meshtastic integration / API
  → event bus (MQTT-class)
```

A wired serial gateway is used for the fixed station node because it is more reliable than Bluetooth for an always-on service. Handheld Meshtastic nodes carried by field teams pair however is convenient.

## 2. Higher-throughput option: Wi-Fi HaLow with OpenMANET

When a station needs a resilient IP mesh that reaches *further than Wi-Fi through obstacles* while still carrying real IP traffic (voice, maps, file sync), **Wi-Fi HaLow (802.11ah)** in sub-GHz spectrum is one strong choice. It trades raw throughput for range and penetration relative to 2.4/5 GHz Wi-Fi, and unlike LoRa it presents a true IP domain.

**OpenMANET** is a common way to run it: HaLow radios in **802.11s** mesh mode with **BATMAN-adv / BATMAN-V** providing Layer-2/3 resilient routing, presented as a flat routed IP mesh. Nodes are typically small single-board computers with a HaLow modem (for example, boards built around Morse Micro MM6108/MM8108-class chips, such as the "Haven"-family nodes). WPA3-SAE secures the link layer; multicast and mDNS make service discovery work across hops.

Because throughput and range both improve with a clear elevated path, the anchor radio is a natural **mast-deployed** component: raised on the mast when the station is parked (alongside the dish and satellite antennas) and stowed for transit, while the always-on low-rate mesh keeps the team connected on the road. The always-on mesh and the deployed anchor are complementary, not alternatives.

This is presented as *an option*, not a requirement. Reasons a builder might pick it:

- Better obstacle/terrain penetration than 2.4/5 GHz for a given power.
- A real IP mesh (routing, multicast, DHCP) rather than a message bus.
- Self-healing multi-hop without manual link planning.

Reasons a builder might skip it: HaLow hardware is less commodity than Wi-Fi, throughput is lower than a clean 5 GHz shot, and sub-GHz spectrum rules vary by region. Many stations run AREDN/Wi-Fi for the fast links and reserve HaLow for the non-line-of-sight legs — or omit it entirely.

**Interoperability caution.** Do not assume every vendor's stock HaLow firmware participates correctly in a specific OpenMANET combination of 802.11s, BATMAN-V, multicast, WPA3-SAE, and addressing. Auxiliary or off-brand HaLow gear (dongles, gateways, camera bridges) should be treated as an unproven tier until it passes acceptance tests: associate with each anchor/relay, confirm BATMAN neighbour visibility, confirm multi-hop unicast, confirm multicast/mDNS, confirm the application services (ATAK/CoT, Reticulum AutoInterface), confirm DHCP, reboot/rejoin, confirm encryption, confirm channel width and region, then run sustained-traffic and roaming tests. Until it passes, keep it on a separately routed segment.

## 3. Node types and roles

A mesh is built from a handful of node roles. One physical box can fill several, but keeping the roles distinct in the design keeps the network reproducible.

| Role | Purpose |
|---|---|
| **Anchor** | The station's primary mesh node and gateway between the mesh and the station core. Highest-capability node; Ethernet-connected to the mesh-services network segment. There is normally one anchor per station. |
| **Relay** | An elevated, often deployable node that extends coverage — placed on a mast, rooftop, or high ground to bridge line-of-sight gaps and add hops. |
| **Camp / access node** | A node providing local client access (Wi-Fi AP or HaLow client bridge) at a camp, shelter, or work site so ordinary phones/laptops get onto the mesh. |
| **Remote SDR / ADS-B node** | A node hosting a receiver away from the station — a remote RTL-SDR for spectrum monitoring, or a 1090 MHz ADS-B receiver feeding an air picture back over the mesh. Puts the antenna where reception is good, not where the station is parked. |
| **Sensor gateway** | A node aggregating field sensors (weather, environmental, telemetry) onto the mesh. |
| **Map / content cache** | A node holding a local cache of maps, weather products, and Archive material so clients pull them over the mesh without any WAN. |
| **Store-and-forward node** | An always-on node holding messages for peers who are currently unreachable (see §4). |

Design rules for nodes:

- **Keep routing nodes lean.** Do not run the station's main automation, AI, or heavy service stack on nodes whose job is routing — a congested or crashed router should not take an application down with it.
- **Keep node profiles reproducible.** Minimise unique per-node manual changes so a lost node can be reflashed and redeployed from a known image.
- **Deployable relays are outward-facing.** They exist to give a group coverage, and are provisioned to be handed out and placed by non-experts.

## 4. Encrypted, store-and-forward messaging layer

IP meshes and LoRa bearers move packets; they do not by themselves give you **encrypted, identity-addressed messaging that survives nodes going offline**. **Reticulum** provides that layer, and it is bearer-agnostic by design — it runs over IP (HaLow/AREDN/Wi-Fi), over LoRa radios, over serial, and over the Internet, all at once, bridging between them.

**LXMF** (Lightweight Extensible Message Format) is the messaging service on top of Reticulum: store-and-forward messages addressed to cryptographic identities rather than IP addresses, so a message reaches a person regardless of which bearer they are currently on, and waits on a propagation node if they are offline.

Staged rollout:

1. **Endpoints first.** Run Reticulum on the mission controller, the AI/DSP node, operator laptops, and phones/tablets (via a Sideband-class client). Over an IP mesh, Reticulum's AutoInterface discovers peers through multicast where permitted — so on a HaLow/AREDN domain the mesh "just works" for encrypted messaging with no address configuration.
2. **Store-and-forward.** Add an always-on Reticulum/LXMF service on the station and/or a dedicated store-and-forward node: LXMF message storage, NomadNet pages, a service directory, and mission bulletins. Now messages survive recipients being temporarily unreachable.
3. **LoRa RNode bridge.** Add dedicated LoRa **RNode** hardware as a Reticulum interface, bridging the encrypted mesh across LoRa, IP, and optional Internet at chosen transport nodes — extending reach to nodes far outside Wi-Fi/HaLow range.

Two operational cautions:

- **A LoRa board flashed for Meshtastic is not simultaneously an RNode.** Keep separate device pools for Meshtastic and Reticulum RNodes; the same radio cannot do both jobs at once.
- **Avoid loops and uncontrolled broadcast forwarding** when bridging Reticulum across multiple bearers. Bridge deliberately, at chosen transport nodes.

Reticulum sits *above* the bearers and *below* the applications: it is what lets "send this message by the best available path" mean something when the paths are a mix of HaLow, LoRa, and a flaky WAN.

## 5. Services on top of the mesh

The mesh exists to carry useful services to whoever can reach the station. The core set:

- **Local voice — Mumble/Murmur.** Encrypted low-latency group voice over the IP mesh, hosted on the station or a dedicated service node, with clients on phones/tablets/laptops. Voice must not depend on the WAN or a satellite uplink — it runs entirely on the local mesh. Where congestion testing shows a need, voice traffic is prioritised on the mesh.
- **Situational awareness — ATAK/CoT.** A Cursor-on-Target relay distributes position and situational data to ATAK/WinTAK/iTAK clients across the mesh, giving a shared map picture with no Internet.
- **Local maps and content.** Offline map tiles, weather and satellite products, and Archive material served from a content-cache node — the station is a mobile Archive node.
- **Message and radio gateways.** A gateway that lets mesh clients send/receive through the station's messaging bearers and radio-message paths, always through the orchestrator's policy engine — never as raw radio control.
- **Read-only dashboards and documentation.** A read-only system dashboard and local docs/package cache for clients on the mesh.

These are the services *published* to mesh clients. What is deliberately **not** published is the control plane (§6).

## 6. WAN edge

The WAN edge is where optional Internet uplinks meet the station, and where the trust boundary lives.

### Multi-WAN router and firewall

A single **multi-WAN travel/edge router** (a GL.iNet-class device is a common, capable choice) acts as the station's WAN aggregator, firewall, DNS-policy point, VPN endpoint, and segmentation enforcer. It handles:

- WAN aggregation across a wired uplink, a satellite terminal, a cellular tether/modem, and a public-Wi-Fi repeater link.
- Firewall, DNS policy, guest isolation, and VLAN routing.
- VPN / overlay networking (WireGuard/Tailscale-class) for remote support.
- The rule that **radio controls, SDR transmit control, and management interfaces are never exposed to the WAN.**

A sensible WAN priority order, highest first:

```text
1. trusted wired WAN
2. satellite terminal
3. cellular
4. public Wi-Fi repeater
```

### Optional satellite uplink

A portable satellite Internet terminal (Starlink Mini-class) is an **optional** broadband backhaul for software/data updates, TLE refresh, remote support over VPN, large map/weather downloads, and Internet-based messaging where appropriate. It is explicitly *not* required for the station's core work: local networking, mesh voice and messaging, SDR reception and decoding, satellite tracking, the local AI, and cached maps/TLEs all run with the uplink absent. Treat it as the fastest bearer when available and nothing more.

## 7. Segmentation and isolation principles

The network carries transmitter controls, an AI planner, expensive receivers, and untrusted guests on the same physical station. Segmentation keeps a problem in one domain from becoming a problem in all of them. Actual VLAN capability depends on the chosen router and managed switch, but the design intent is fixed:

| Segment | Contents |
|---|---|
| Core services | Mission controller, canonical state store, internal APIs |
| AI / DSP | GPU compute node, high-rate SDR services |
| Radio management | Transceivers, rotator maintenance, radio control adapters |
| Mesh services | Mesh anchor uplink, CoT / Mumble / Reticulum gateways |
| End-user / guest | Tablets, laptops, temporary users |
| IoT / power | Microcontrollers and sensors |
| Cameras | Roof/cabin cameras |
| Untrusted WAN | Public Wi-Fi and external networks — kept separate |

Principles:

- **The mesh domain is routed and filtered from the station core, not bridged into it.** Publish selected services to the mesh (§5) rather than exposing the whole core LAN. A mesh client uses the station's services; it cannot reach the station's control plane.
- **Blocked to mesh clients by default:** station-automation administrator access, compute-node SSH, raw radio-control ports, SDR transmit control, router administration, credential stores, arbitrary event-bus/MQTT topics, power-relay control, and firmware-update endpoints.
- **Control and data planes are separate.** Bearer daemons and application services run isolated from the deterministic control services that own transmit, power, and rotator authority.
- **Least privilege per bearer.** Meshtastic requests, mesh gateway requests, and remote clients are all the same kind of policy-checked request — none of them is a side channel around the orchestrator.

The consequence, stated plainly: standing up a big open network for a community and keeping the station's transmitters and controls safe are the *same* design problem, solved by publishing services outward and firewalling control inward.

## Related documents

- [architecture.md](architecture.md) — the tiered architecture and communications topology this stack lives in.
- [safety-model.md](safety-model.md) — control-plane isolation, service isolation, and why untrusted received content is never an instruction.
- [ai-agent.md](ai-agent.md) — how "send this by the best available bearer" becomes a typed, policy-checked mission request.
