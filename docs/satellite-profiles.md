# Satellite Profiles

A comms-station needs to know how to listen to (and, where authorized, talk to) a spacecraft: what bands it uses, what waveforms it emits, and how to go looking for it when its state is uncertain. That knowledge lives in **satellite profiles** — small, machine-readable YAML files validated against a common JSON Schema.

The design goal is a clean separation between the *type system* (public, in this repo) and the *instances* (which may be public or private). The tooling only ever depends on the type system. Any profile that validates against the schema works with the station's tracking, capture, and decode pipeline — whether it shipped with this repo or was loaded by an operator from somewhere else.

> **Note on private profiles:** operators load private profiles for spacecraft they are authorized to work; this repo ships only public examples.

## The profile type system

The schema lives at [`profiles/schema/satellite-profile.schema.json`](../profiles/schema/satellite-profile.schema.json). A public example profile lives in [`profiles/examples/`](../profiles/examples/), with more planned (weather, Inmarsat). The validator is [`tools/validate_profile.py`](../tools/validate_profile.py):

```
python tools/validate_profile.py <profile.yaml>   # exit 0 = valid, 1 = invalid
```

### Profile types

Every profile declares a `type`, which tells the station what kind of mission logic and decoder plugins to bring to bear:

| `type` | What it means |
|---|---|
| `datacast-satellite` | One-to-many data delivery (DTN bundles, broadcast content, update distribution). The station acts primarily as a receive-and-cache node. |
| `weather-satellite` | Imagery downlinks (e.g. NOAA APT, LRPT). Decoders produce weather products for local serving. |
| `amateur-satellite` | Amateur-service spacecraft: telemetry beacons, transponders, digipeaters. Two-way use is gated on operator licensing. |
| `inmarsat` | Geostationary L-band services receivable with modest hardware. |
| `generic` | Anything else. Gets tracking, capture, and hunt support, but no type-specific decode assumptions. |

### Required structure

Four top-level keys are required in every profile:

| Key | Contents |
|---|---|
| `schema_version` | Version of the schema the profile targets. |
| `type` | One of the types above. |
| `identity` | What the spacecraft is: name, and identifiers such as a NORAD catalog number where known (identifiers may be null for spacecraft not yet correlated to a catalog entry). |
| `links` | The RF interface: a list of link definitions, described below. |

Each entry in `links[]` requires:

| Field | Contents |
|---|---|
| `name` | A short handle for the link (e.g. `apt_downlink`). |
| `direction` | `uplink`, `downlink`, or `duplex` — named relative to the spacecraft: `uplink` is ground-to-space; `downlink` is space-to-ground (what a station receives). |
| `freq_mhz_min` / `freq_mhz_max` | The frequency range in MHz. Equal values describe a single channel; a range describes a band the signal may appear within. |
| `modulations` | Array of modulation/waveform strings (e.g. `["apt"]`, `["lora", "gfsk"]`). These select decoder plugins; unknown strings are allowed and simply mean "no decoder yet". |

Anything beyond the required keys is open: profiles may carry optional sections (`hunt`, `stages`, `notes`, and others) anywhere, and validators must tolerate keys they do not recognize. This is deliberate — it lets richer profiles drive richer behavior without schema churn, and lets private profiles carry operational detail the public tooling never needs to know the shape of.

### Example

A minimal amateur-satellite profile (see `profiles/examples/` for the real, validated version):

```yaml
schema_version: 1
type: amateur-satellite
identity:
  name: ISS ARISS packet digipeater
  norad_id: 25544
links:
  - name: aprs_digipeater
    direction: duplex
    freq_mhz_min: 145.824
    freq_mhz_max: 145.826
    modulations: [afsk]
```

This describes the 1200-baud AFSK APRS digipeater on 145.825 MHz aboard the ISS — a long-running ARISS service (verify current status at [ariss.org](https://www.ariss.org) before relying on it).

## Satellite hunt

Most satellite software assumes you know where the spacecraft is and what it is transmitting. **Satellite hunt** is a first-class mission type for the harder case: a spacecraft whose state is uncertain — newly launched and not yet correlated, long silent, tumbling, or degraded. The mission combines:

1. **Pass prediction.** Propagate the best available TLE (or a set of candidate TLEs when the object isn't yet firmly identified) to schedule observation windows.
2. **Blind beacon search.** During a window, capture wideband IQ around the expected band(s) from the profile's `links[]` rather than tuning a single channel — a spacecraft in a fault state may not be where, or what, you expect.
3. **Doppler-signature matching.** A real LEO signal carries a predictable Doppler curve for a given pass geometry. Matching detected carriers against the predicted curve separates the spacecraft from terrestrial interference far more reliably than signal strength does, and can help disambiguate which object in a launch cluster you are hearing.
4. **Beacon decoders.** LoRa and GFSK beacon decoders run against candidate detections, because these are common choices for small-satellite telemetry and are decodable with inexpensive SDR hardware. A successful decode upgrades the mission result from "heard something" to "confirmed, and here is its telemetry".

A profile's optional `hunt` section parameterizes this: search bands, expected beacon modulations, whether Doppler matching applies. Profiles may also carry an optional `stages` section describing a staged campaign (e.g. acquire, receive, transmit) with gates between stages — the station can track campaign progress against it.

Hunt missions produce value even when they fail to find anything: a recorded, Doppler-annotated spectrum survey of a band during a predicted pass is a reusable observation, and "confirmed not heard" is itself information for a spacecraft's operators.

## The local-sky map

The station maintains a **local-sky map**: a TinyGS/SatNOGS-style dashboard of what is overhead now and what is coming up next, computed from a locally cached TLE set and enriched, when connectivity allows, with observations from community ground-station networks. For each object it shows pass times, elevation, and — where a profile exists — what you could receive and with what hardware.

Two properties make this a good early deliverable:

- **It needs no RF hardware.** TLE propagation is pure computation, so the local-sky map is useful on day one, before any antenna is connected — and it is the natural front door to the rest of the system ("that one is receivable; start a mission").
- **It degrades gracefully offline.** The TLE cache means the map keeps working without internet, with accuracy decaying slowly as elements age; the dashboard shows element age so the operator knows how much to trust it.

Community networks (TinyGS, SatNOGS) complement the local station: they tell you what others are hearing, which is especially valuable during a hunt — a spacecraft heard by a station on another continent constrains its state even when your own horizon hasn't offered a pass yet.

## Public and private profiles

This repo ships **public examples only**: spacecraft whose downlinks are openly documented and legally receivable (weather satellites, amateur satellites, published geostationary services). It contains no operational parameters for any private spacecraft.

Operators load private profiles for spacecraft they are authorized to work. Because such profiles validate against the same public schema, they get the full pipeline — tracking, hunt, capture, decode plugins, the local-sky map — without any private detail ever entering this repo. Compatibility is guaranteed by the type system, not by shipped data. Keep private profiles in private storage, and treat frequencies, schedules, and procedures for non-public spacecraft as sensitive by default.
