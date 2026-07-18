# The AI Agent

<!-- SPDX-License-Identifier: CC-BY-4.0 -->

A comms-station is designed to be operated by people without radio skills. The
onboard AI is the radio operator: it turns "can you get a message to my
family" or "what's that signal" into concrete missions. But it is an operator
with a strictly bounded job. The model plans and explains; a deterministic
orchestrator validates and executes. This document defines that boundary.

## 1. What the model does

The local model performs:

- Natural-language intent parsing
- Mission planning
- Device and bearer selection
- Explanation
- Retrieval from manuals, band plans, local logs, frequency databases, and TLEs
- Voice interaction
- Interpretation of DSP-produced features
- Summarization of received traffic where lawful
- Suggested decoder/modulation hypotheses
- Report generation

## 2. What the model does not do

The model does not:

- Directly actuate hardware.
- Invent frequencies or modes when authoritative data is available.
- Bypass the transmitter allowlist.
- Override voltage, wind, movement, SWR, temperature, or antenna interlocks.
- Change its own permissions.
- Treat model confidence as a substitute for measured RF data.

Every item on the "does not" list is enforced outside the model. The station
does not depend on the model choosing to behave; it depends on deterministic
services that check every request (see [safety-model.md](safety-model.md)).

## 3. Model interface

The model is exposed through an OpenAI-compatible local endpoint or a neutral
internal API — the station works offline, so the model runs on station
hardware. Required capabilities:

- Tool/function calling
- Long-context retrieval
- Audio input or integration with local speech recognition
- Optional image input for antenna/cable/camera verification
- JSON-schema-constrained output
- Fast small-model fallback on the low-power controller
- Larger multimodal model on the compute node

Model selection stays pluggable. Candidate local models should be benchmarked
on tool-call correctness, latency, hallucination rate, radio terminology,
ability to use local manuals, audio quality, robustness with noisy cabin
speech, resource use on the compute node, and fallback performance on the
low-power controller.

## 4. Typed tool requests

The model never touches a device. It emits typed, schema-validated tool
requests; the orchestrator checks each one against canonical state, device
inventory, allowlists, power budgets, and mission leases before anything
happens. Three representative examples:

### Tune a receiver

```json
{
  "operation": "receiver.tune",
  "device": "rtl_v4c_1",
  "frequency_hz": 137100000,
  "sample_rate": 2400000,
  "mode": "iq",
  "antenna": "vhf_satellite_payload",
  "purpose": "spectrum_survey"
}
```

### Prepare IC-9700 for a pass

```json
{
  "operation": "mission.prepare_satellite_contact",
  "satellite_id": "catalog-number-or-local-id",
  "radio": "ic9700",
  "payload": "vhf_uhf_satellite_array",
  "transmit_authorization": "operator-required",
  "record_iq": true
}
```

### Send a message through the best bearer

```json
{
  "operation": "message.route",
  "recipient": "identity-or-callsign",
  "content": "Arrived safely; vehicle station is online.",
  "priority": "routine",
  "allowed_bearers": ["reticulum", "meshtastic", "aprs", "winlink"],
  "max_cost": "offline-preferred"
}
```

Note what the requests contain and what they omit. The model states intent
(`purpose`, `priority`, `allowed_bearers`) and proposes parameters; it does
not carry authorization. `transmit_authorization: "operator-required"` is a
declaration the orchestrator enforces, not a permission the model grants
itself. A request that names an unavailable device, an out-of-allowlist
frequency, or an antenna incompatible with the current deployment state is
rejected with a reason the model can relay to the operator.

## 5. Frequency exploration workflow

For "find interesting signals near X":

1. Resolve request and legal receive status.
2. Query device/antenna coverage.
3. Select the least-power receiver capable of the mission.
4. Measure local noise and gain state.
5. Capture spectrum.
6. Detect candidates using conventional DSP.
7. Measure center frequency, bandwidth, duty cycle, SNR, Doppler, and periodicity.
8. Match against offline frequency databases and scheduled satellites.
9. Run candidate demodulators.
10. Present confidence-ranked results.
11. Store unknown signals in SigMF with full metadata.
12. Let the model explain evidence and uncertainty.

The model does not inspect raw high-rate I/Q token by token; DSP reduces it to
features, images, audio, and candidate decodes. The division of labor is
consistent throughout: signal processing produces measurements, the model
produces hypotheses and explanations, and the record (SigMF captures with full
metadata) outlives both, so a signal unidentified today can be revisited with
better decoders tomorrow.

## Related documents

- [safety-model.md](safety-model.md) — deployment states, transmit gates, and
  the prompt-injection stance (received content is never instructions).
- [architecture.md](architecture.md) — where the model, orchestrator, and DSP
  run, and how canonical state flows between them.
- [satellite-profiles.md](satellite-profiles.md) — the profile type system
  that gives the model authoritative satellite parameters instead of guesses.
