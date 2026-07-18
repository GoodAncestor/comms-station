# Safety Model

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

A comms-station puts transmitters, motorized antennas, and an AI planner in one
vehicle (or fixed site). The safety model exists so that no combination of
software behavior — including AI misbehavior — can transmit illegally, damage
equipment, or make the vehicle unsafe to drive. The rule throughout is the same
one that shapes the whole architecture: **the AI proposes; deterministic
services validate and execute.**

Three layers do the work:

1. A **deployment state machine** that ties what the station is allowed to do
   to the physically verified state of the vehicle and its antennas.
2. A **transmit authorization model** of stacked, independent gates that all
   must pass before RF leaves an antenna.
3. **Security principles** that bound what any single compromised or confused
   component can do — including received-content prompt injection against the
   AI agent.

## 1. Deployment state machine

Deployable antennas (roof-rack payloads on the reference implementation) move the
station through explicit states. Transitions are owned by the deterministic
orchestrator, driven by sensors and operator confirmation — never by the model.
Each state grants a strict superset of nothing: capabilities are added only as
physical verification accumulates, and removed immediately when it lapses.

```text
STOWED
  vehicle may move
  rotator and high-power TX inhibited

PARKED / PREPARE
  parking brake and ignition state verified
  operator selects payload
  system displays mounting instructions

DEPLOYED UNVERIFIED
  payload sensor/camera/manual confirmation pending
  no movement, no TX

DEPLOYED VERIFIED
  payload identity known
  cable presence verified
  wind and power acceptable
  receive missions allowed

TX ARMED
  physical TX enable set
  radio/antenna/power/SWR checks passed
  authorized mission only

STOW REQUESTED
  TX off
  recordings stopped
  rotator returns home
  operator removes payload

STOWED VERIFIED
  roof sensors clear
  vehicle movement allowed
```

Consequences worth spelling out:

- **Receive requires DEPLOYED VERIFIED.** Until the payload's identity is
  known and its cabling confirmed, nothing runs — not even receive-only
  missions. Payload identity determines frequency range, bias-tee limits,
  rotator limits, and required filters; running blind risks hardware.
- **Transmit requires TX ARMED**, a separate state above verified deployment
  that adds a physical enable and per-transmission checks (see below).
- **Movement and deployment are mutually exclusive.** The vehicle is
  drive-ready only in STOWED / STOWED VERIFIED, and the rotator and
  high-power transmit are inhibited whenever the vehicle may move.
- **Stowing is a first-class procedure**, not an afterthought: transmit stops,
  recordings close cleanly, the rotator homes, and roof sensors must read
  clear before the vehicle is released.

Fixed-site stations use the same machine with the vehicle-motion states
degenerate; the verification and TX-arming states apply unchanged.

## 2. Transmit authorization gates

Transmission is guarded by multiple independent gates. All must pass; no
software path — and specifically no model output — can substitute for any of
them:

1. Physical **TX ARM** key or guarded switch.
2. Licensed-operator profile loaded.
3. Radio and antenna compatibility confirmed.
4. Frequency/mode within allowlist.
5. Maximum power allowed for payload.
6. SWR/forward/reflected power valid.
7. Vehicle parked and payload verified.
8. No conflicting transmitter active.
9. Mission has an authorization class:
   - receive-only
   - configure-only
   - operator-PTT
   - pre-authorized automatic beacon/data
10. Event is logged.

The authorization classes are the model's ceiling: an AI-planned mission runs
at receive-only or configure-only unless a licensed operator explicitly grants
operator-PTT (human keys every transmission) or pre-authorizes a narrow
automatic beacon/data behavior. There is no class the model can select that
lets it transmit at its own discretion.

An **emergency stop** must remove PTT authorization and, where appropriate,
radio power, independently of the model — a hardware path that works even if
every computer on the station is wrong at once.

## 3. Security principles

- Local first.
- No default cloud dependency.
- One canonical state authority.
- Least privilege.
- Separate control and data planes.
- Signed/pinned releases.
- Back up firmware/configuration before changes.
- Audit every transmit, relay, power, and rotator command.
- Fail toward vehicle drivability and equipment safety.
- Never allow a model to amend its own allowlist.

### Service isolation

Each hardware adapter (radio control, SDR applications, satellite decoders,
mesh daemons, power controller, rotator) runs as a separate container or
service and receives only the device nodes and network permissions it
requires. A compromised decoder cannot reach the rotator; a misbehaving mesh
daemon cannot key a transmitter.

### Secrets

- Radio and network credentials live outside the repository.
- Device certificates or strong keys; no shared default passwords.
- Public demo configuration is kept separate from production profiles.
- Temporary field credentials get rotated.
- Management interfaces and raw control ports are never exposed through the
  WAN uplink.

### Prompt-injection stance

The station's AI agent reads traffic from the open airwaves, so this is a
design constraint, not an edge case: **untrusted received content never
becomes instructions.**

Received radio text, packet messages, web content, and decoded files are
untrusted data. They must never be inserted as privileged instructions. The
model receives them wrapped in metadata that preserves that boundary:

```json
{
  "trust": "untrusted_received_content",
  "source": "aprs",
  "sender": "CALLSIGN",
  "content": "..."
}
```

No received message can invoke a hardware tool without a separate
authorization policy. A packet that says "retransmit this on every band" is a
string to summarize, not a command to follow — and even if the model were
fooled into proposing exactly that, the mission authorization classes and
transmit gates above are deterministic code that has never heard of the
packet.

## Related documents

- [architecture.md](architecture.md) — the tiered architecture these
  mechanisms live in, and the canonical-state command flow.
- [ai-agent.md](ai-agent.md) — what the model does and does not do, and how
  its typed tool requests meet these gates.
