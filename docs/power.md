<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Power Architecture

A comms-station is a large, spiky electrical load — several transmitters, a
GPU compute node, a motorized antenna, a satellite terminal, and a rack of
receivers — running off a modest off-grid battery. The power design has one
job above all others: no software behavior, and no combination of equipment
switching on at once, can brown out the always-on brain, exceed the wiring, or
strand a motorized antenna in a position that makes the vehicle unsafe to
move. It does this with the same discipline as the rest of the architecture —
**deterministic services own the energy budget; the AI only ever requests** —
and it mirrors the tiered structure described in
[architecture.md](architecture.md): lower power tiers never depend on higher
ones, and the layer that must be correct is kept small and simple.

This document assumes a generic house system: a lithium 12 V battery fed by a
DC-DC converter (from a vehicle traction pack or alternator) or a mains/solar
charger, distributed to loads through individually fused branches. Concrete
capacities, wire gauges, and fuse values are engineering decisions per build
and are recorded in the station profile and bill of materials, not here.

## 1. The always-on supervision layer (Tier 0)

The bottom tier is a small, always-powered supervision layer built from
microcontroller-class power supervisors and simple hardware interlocks. It has
no AI, no general-purpose operating system, and no network dependency it
cannot survive losing. It runs fixed rules, and it is the only layer with the
authority to cut power to everything above it.

Its responsibilities:

- Continuously monitor battery voltage, current, and temperature.
- Sense vehicle state (parking brake, ignition, motion) and antenna
  deployment status.
- Drive the enable inputs of DC-DC converters and the coils of load-switching
  relays and contactors.
- Enforce hard timeouts and watchdogs, so a hung higher tier cannot leave a
  load energized indefinitely.
- Hold every switched output in a **default-safe state** on reset, brownout,
  or loss of its controller.

Because it is the layer that must be correct, it is deliberately kept dumb.
Its rules are the kind that can be reasoned about exhaustively: below voltage
X, shed load; above temperature Y, shut down; if the heartbeat from the
mission controller stops, hold current outputs and raise an alarm rather than
change state unpredictably. It draws little enough that it can run indefinitely
on the house battery while everything else is off, which is what makes the
station's deep-sleep and low-power watch modes possible.

The supervision layer supervises; it does not carry load. Its low-current
control outputs switch the gates of automotive-rated high-side switches,
optoisolated drivers, DC-DC enable pins, and appropriately rated
relays/contactors — never the load current itself.

## 2. Switched, power-gated peripherals (Tier 3)

Heavy peripherals — transceivers, the antenna rotator and its active feed, the
satellite internet terminal, amplifiers, LNAs, secondary displays, and powered
USB/SDR hubs — each live in their **own switched power domain**. Nothing in
this tier is on by default; each domain is energized only when a validated
mission needs it, and de-energized when it does not.

This per-domain switching is what lets the orchestrator budget energy per
mission and lets the supervision layer shed load safely. It also contains
faults: a peripheral that misbehaves electrically can be dropped without
taking down its neighbors or the always-on tiers.

Switching this tier requires care beyond flipping a relay:

- **Inrush.** High-inrush loads (the satellite terminal, converters feeding
  large capacitors) need switches and fuses rated for the surge, not just the
  steady draw, and benefit from soft-start or pre-charge where the draw is
  large.
- **Inductive kick.** Relay coils, the rotator motor, and other inductive
  loads need flyback/snubber suppression so switching transients do not couple
  into sensitive receive electronics or damage the switch.
- **Sequencing.** Some domains must not be cut arbitrarily — a compute node or
  a moving rotator needs a graceful sequence (§5), not a hard disconnect.
- **Current sensing.** Each significant branch should be measurable, so the
  orchestrator can verify a load actually drew what was expected and Tier 0
  can trip on an overcurrent.

## 3. Branch-circuit classes by draw

Loads are grouped into branch-circuit classes sized by their draw, each with a
dedicated fused feed and return. The classes below are generic design
categories; the exact ampacity, wire gauge, and fuse rating for each are
finalized from the actual run length and the manufacturer's stated maximum
draw for the chosen equipment.

| Branch class | Character | Design notes |
|---|---|---|
| **Always-on supervision** | Very low current, never switched | Independent of the mission controller; runs in every mode including deep sleep. |
| **Mission controller / core network** | Low, steady, must not be interrupted | Protected, always-on branch; hold-up capacitance or a small UPS preferred so brief transients do not reboot the canonical state authority. |
| **Compute / DSP node** | Moderate to high, variable | Dedicated DC-DC and fuse; switched via its enable input and only after a graceful shutdown (§5). |
| **High-power transmitter** | High, intermittent, spiky | Dedicated cable and return per transmitter, sized with margin above the radio's maximum transmit draw; hardware transmit interlock shared across all transmitters. |
| **Low/medium-power radio** | Moderate | Dedicated branch verified against the manufacturer's requirement; smaller than a high-power transmitter branch but still individually fused. |
| **Rotator / active feed** | Moderate, motor + bias | Separate switched branch; stow before removing power (§5). |
| **Satellite terminal / WAN** | Moderate with high inrush | Dedicated switched converter rated for surge and variable draw. |
| **Receive SDR / USB** | Low, but sensitive to instability | Powered hub with per-port control; avoid marginal bus power that browns out mid-capture. |

Two rules cut across all classes:

- **Wire and fuse to the branch, not to the average.** Size the conductor and
  its protection for the worst-case draw of that branch plus margin, and let
  the fuse protect the wire.
- **Dedicated returns.** High-current branches get their own return path;
  sharing returns invites ground-loop noise into receivers and unpredictable
  voltage drop under transmit load.

## 4. One high-power transmitter at a time

The dominant electrical risk in a small off-grid station is several
transmitters keying simultaneously. Transmit draw is both large and
coincident, and the sum of a station's transmitters can approach or exceed what
the battery, DC-DC converter, and wiring can deliver. The governing rule is
therefore conservative by default:

> **Only one high-power transmitter is enabled at a time, until a complete
> load analysis — covering the battery, DC-DC/charger capacity, wiring, fuses,
> and thermal limits — explicitly approves otherwise.**

This is enforced as a deterministic interlock, not a guideline the AI is
trusted to respect. A single shared transmit-enable resource is leased to at
most one transmitter; a request to key a second high-power radio while another
holds the lease is denied at the orchestrator and, where the hardware allows,
blocked by a physical interlock line as well. The rule composes with the
transmit-authorization gates in [safety-model.md](safety-model.md): passing
those gates is necessary but not sufficient — the transmitter must also hold
the single high-power lease.

Lifting the restriction is a deliberate engineering act, per build, backed by
the load analysis and recorded in the profile — never an inference the model
makes because a mission would be more convenient with two radios keyed.

## 5. Graceful shutdown sequences

Two classes of load must never be dropped by a bare power cut: the compute
node, which can lose or corrupt state, and the rotator, which can be left
pointed somewhere that blocks stowing or endangers a moving vehicle. Each has
an ordered shutdown sequence owned by the deterministic orchestrator; power is
removed only at the end, after the device confirms it is safe.

**Compute / DSP node:**

```text
1. Stop accepting new jobs (SDR captures, DSP tasks, model requests).
2. Stop and flush in-flight recording and buffered data to storage.
3. Persist model and mission state.
4. Request an orderly OS shutdown.
5. Wait for shutdown confirmation — heartbeat loss or a shutdown-complete signal.
6. Hold briefly for storage/flush margin.
7. Remove the DC-DC enable.
```

**Rotator / motorized antenna:**

```text
1. Revoke the tracking lease so no client can command further motion.
2. Stop any transmit through the antenna.
3. Return the rotator to its stow/home position.
4. Verify the reported position.
5. Disable feed bias where appropriate.
6. Remove rotator power.
```

The ordering matters: recordings close before state is persisted so nothing is
half-written; the rotator homes and its position is *verified* before power is
cut, because a rotator that lost power mid-slew is exactly the failure the stow
sequence exists to prevent. If a step cannot complete — the OS will not shut
down, the rotator will not confirm home — the sequence escalates to an alarm
and a held-safe state rather than proceeding to the power cut.

Emergency stop is the exception that proves the rule: it removes transmit
authorization and, where appropriate, radio power immediately and
independently of any software, on the principle that an operator must be able
to make RF stop even when every computer on the station is wrong at once. The
graceful sequences are for planned power-down; emergency stop is for when
graceful is not an option.

## 6. Low-voltage cutoffs and safe defaults

Off-grid, the battery is the constraint the whole design bends around. The
supervision layer enforces a **staged response to falling voltage** so the
station degrades predictably instead of collapsing:

1. **Advisory** — the orchestrator is told the battery is under pressure and
   begins declining non-essential missions and shedding optional loads.
2. **Load-shed** — Tier 3 peripherals and the compute node are shut down (via
   their graceful sequences while there is still headroom to do so), leaving
   the mission controller and supervision layer running.
3. **Protective cutoff** — at the low-voltage threshold the house system is
   brought down to protect the battery, leaving only the supervision layer
   alive to watch for recovery.

Thresholds are set with hysteresis so the station does not oscillate around a
cutoff point, and the load-shed stage is entered early enough that graceful
compute and rotator shutdowns can finish before the protective cutoff — a
hard cutoff mid-slew or mid-write is precisely what the staging avoids.

The safe-default rules that back this up:

- **De-energized is the reset state.** On controller reset, brownout, or loss
  of the supervision layer, every switched output falls to off. Nothing latches
  on across a fault.
- **Transient-immune switching.** Relays must not chatter during engine crank
  or other voltage transients; brief sags are ridden through, not reacted to.
- **The always-on tiers are protected first.** Load-shed sacrifices capability
  (transmit, compute, WAN) to preserve the always-available brain and the
  supervision layer for as long as the battery allows.
- **Manual override exists and is independent of software.** An operator can
  force-off any switched domain and trigger emergency stop without the mission
  controller or the model in the loop.
- **Motion and high power are mutually exclusive** with an un-stowed antenna,
  enforced here as a power interlock as well as in the deployment state
  machine ([safety-model.md](safety-model.md)).

## 7. Commissioning checks

Before a station is trusted to run missions unattended, the power system is
verified end to end, not just wired and assumed:

- Confirm every branch's fuse and wire size against its measured draw.
- Measure idle and peak current per branch and for the station as a whole.
- Verify the Tier-0 low-voltage staging and protective cutoff actually trip at
  their thresholds, with correct hysteresis.
- Verify the graceful compute and rotator shutdown sequences complete, and
  that an interrupted sequence escalates to a safe held state.
- Verify no relay chatter through a crank/voltage transient.
- Verify the one-high-power-transmitter interlock denies a second key.
- Verify manual override and emergency stop work with the mission controller
  powered down.

## Related documents

- [architecture.md](architecture.md) — the tiered power-and-control
  architecture this document details, and the canonical-state command flow
  that owns the energy budget.
- [safety-model.md](safety-model.md) — the transmit-authorization gates and
  deployment state machine that the one-transmitter interlock and stow
  sequence compose with.
- [reference-build/bom.md](reference-build/bom.md) — concrete power components
  and indicative cost bands for the reference station.
