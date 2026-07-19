<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# VHF/UHF SDR transmit chain

A software-defined radio is a superb receiver on its own, but its transmit output is
low-power (milliwatts) and spectrally dirty — it cannot legally or safely drive an
antenna without a supporting analog chain. This document specifies that chain for the
2 m and 70 cm bands, so a station can **transmit** — terrestrial contacts and
full-duplex satellite work — from an SDR plus parts, instead of a discrete transceiver.

This is the piece that makes the station's "SDR-first" approach real. For an
AI/software-driven station a commercial transceiver's manual front panel is dead
weight; what you actually need is a clean, sequenced, protected RF path the software
can key. See [radios.md](radios.md) for where this fits and where a discrete radio is
still the pragmatic choice (100 W HF; always-on FM).

> **Licensing and legality first.** Transmitting is done under the authority of a
> licensed control operator, within amateur privileges, and must meet your regulator's
> spurious-emission limits (in the US, FCC §97.307 — verify the current values for your
> power level). The filtering below is **mandatory for legality**, not an optimization.
> Nothing here is keyed except through the orchestrator's transmit-authorization gates
> (see [safety-model.md](safety-model.md)).

## Signal path

```
TX:  SDR TX out ──► band-pass filter ──► linear PA ──► low-pass/harmonic filter ──┐
                    (clean the drive)   (mW → watts)   (kill harmonics)            │
                                                                          T/R switch + sequencer ──► antenna
RX:  SDR RX in ◄── limiter/LNA ◄──────────────────────────────────────────────────┘
```

For **full-duplex satellite** (linear birds: transmit the uplink while hearing your own
downlink), uplink and downlink are on different bands (e.g. TX 2 m / RX 70 cm), so run
**two chains** — one per band — with enough band separation and filtering that the
transmit chain does not desensitize the receive chain. The SDR itself (e.g. a
dual-channel LimeSDR or bladeRF) does full-duplex natively; the analog side is what has
to be built so the two bands coexist.

## Components

1. **Linear power amplifier.** Must be **linear (Class AB)** to preserve SSB/CW and
   linear-transponder waveforms — a non-linear (Class C) amp will splatter SSB and
   generate intermodulation. **Size it modestly:** most LEO satellite uplinks close with
   only a few watts EIRP into a small directional antenna, so **~10–25 W is generous** for
   2 m/70 cm satellite and terrestrial simplex. Lower power means less heat, a simpler
   supply, and easier spectral cleanliness — do not reach for 100 W here without a reason.

2. **Band-pass filter (pre-PA) and low-pass/harmonic filter (post-PA).** The SDR's raw
   output carries harmonics, images, and wideband noise. A band-pass filter cleans the
   drive into the PA; a low-pass/harmonic filter after the PA suppresses the harmonics the
   PA itself produces. Both are **band-specific** and are the components that bring the
   emission inside legal spurious limits.

3. **T/R switch + sequencer.** Controls the order of operations so nothing is
   "hot-switched": on transmit, mute/protect the receive path first, then key the PA last;
   on receive, reverse, with millisecond-scale delays. Hot-switching destroys relays, PAs,
   and SDR front ends. Drive the sequence from a small microcontroller or the station
   node's GPIO. This is not optional — it is what keeps the expensive parts alive.

4. **Receive protection.** A limiter plus the T/R switch isolate the SDR's fragile receive
   input during transmit. An LNA at the antenna improves receive; it must be switched out
   or protected on transmit.

5. **Drive-level / ALC control.** The SDR's digital transmit gain must be set so the PA
   runs linear rather than clipping. A power/ALC feedback loop (or a careful fixed drive
   verified on a scope/analyzer) keeps it in range. This lives in software (e.g. GNU
   Radio) but depends on the power measurement below.

6. **SWR / power monitor.** A directional coupler and detector measure forward and
   reflected power; feed it back to the sequencer/software to **fold back or inhibit
   transmit on high SWR** (a bad or disconnected antenna), protecting the PA.

## Integration with the mast head

This chain lives in the mast-mounted enclosure alongside the SDR and the station node
(see [architecture.md](architecture.md)), so the coax from PA to antenna is short. The
node (or a dedicated MCU) drives the sequencer and reads SWR/power. **Thermal note:** the
PA is the heat source — in a sealed IP65 enclosure, heatsink it to the case exterior or
mount the PA outside the sealed box. Power the chain from the mast's fused 12 V branch,
sized for the PA's draw (the PA, not the SDR/SBC, dominates the current budget).

## Commissioning (do these in order)

1. **Bench, into a dummy load** — verify the sequencer timing and, with a spectrum
   analyzer or a second SDR + calibrated attenuator, confirm the output meets spurious
   limits. Do not skip this; an unfiltered SDR TX is not legal to radiate.
2. **Low-power on-air, terrestrial simplex** — confirm a real contact and the SWR
   fold-back behaves.
3. **Full-duplex satellite** — bring up the second band chain, verify the TX chain does
   not desense the RX chain, and let the software handle Doppler on both ends.
4. **Enclosure integration** — mount in the mast head, confirm thermal behavior under a
   sustained transmit duty cycle, and confirm the SWR-protect trips on a fault.

## Bench and test parts

Much of the test gear is already useful elsewhere in the station: a signal generator /
frequency converter (e.g. an Othernet moRFeus) plus fixed attenuators and a DC block for
closed-cable tests, a dummy load, and a directional coupler. A spectrum analyzer or a
second SDR with a calibrated attenuator is needed to verify spectral purity before going
on the air. **Never connect a transmitter output to a bare signal-generator input** — its
maximum input is milliwatts.

## Related documents

- [architecture.md](architecture.md) — where the mast head and SDR plane sit in the station
- [radios.md](radios.md) — the radio/SDR suite and the SDR-first vs. discrete-radio line
- [safety-model.md](safety-model.md) — transmit-authorization gates the software must pass
- [reference-build/bom.md](reference-build/bom.md) — parts and indicative cost bands
