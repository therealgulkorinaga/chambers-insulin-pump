# Chamber Sentinel — Insulin Pump & CGM Data Sovereignty Simulation

A full-loop local simulation of the **Chamber Sentinel** burden-of-justification framework applied to insulin pump and continuous glucose monitoring (CGM) ecosystems. The simulation models the complete data lifecycle — from sensor readings through manufacturer relay classification, clinical report generation, portable record delivery, and scheduled data destruction ("burn").

## The Problem

Current insulin pump and CGM ecosystems have three systemic failures:

1. **Manufacturers act as mandatory data intermediaries** — all CGM data flows through manufacturer clouds before reaching clinicians. No direct sensor-to-clinician path exists.
2. **Persistence defaults exceed clinical safety necessity** — manufacturers retain raw glucose data indefinitely despite clinical utility being concentrated in 14–90 day windows.
3. **Patients occupy the weakest custodial position** — they generate all data, bear all consequences, and have the least control over downstream distribution across 90+ third-party apps.

## The Framework

Chamber Sentinel enforces a simple principle: **data persistence must be justified by demonstrated clinical safety necessity.** Any persistence exceeding that justification is eliminated by default.

Data flows through six "Typed Worlds", each with its own retention justification and burn schedule:

| World | Purpose | Typical Burn Window |
|---|---|---|
| Real-Time Therapeutic | Active glucose/insulin loop | Seconds–minutes |
| Clinical Review | AGP reports, time-in-range | 90 days |
| Device Maintenance | Sensor calibration, firmware | 10 days (sensor wear) |
| Research | De-identified population data | 365 days |
| Patient | Portable record (patient-held) | Patient-controlled |
| Third Party | API-distributed app data | 72 hours (SLA-based) |

## Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   CGM Engine │    │  Pump Engine │    │  Pen Engine  │
│  (Dexcom G7, │    │ (Tandem,     │    │ (NovoPen 6,  │
│   Libre 3…)  │    │  Omnipod 5…) │    │  Tempo…)     │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────┬───────┘───────────────────┘
                   ▼
          ┌────────────────┐
          │   Phone App    │ ← BLE simulation layer
          └────────┬───────┘
                   ▼
          ┌────────────────┐
          │  Manufacturer  │ ← World Classifier assigns items
          │     Relay      │   to typed worlds
          │                │
          │  ┌───────────┐ │    ┌─────────────────┐
          │  │  Worlds    │─┼───▶ Report Generator │
          │  └───────────┘ │    └────────┬────────┘
          │                │             │
          │  ┌───────────┐ │             ▼
          │  │   Burn     │ │    ┌─────────────────┐
          │  │ Scheduler  │ │    │ Portable Record  │
          │  └─────┬─────┘ │    │   (Patient Vault) │
          │        ▼       │    └─────────────────┘
          │  ┌───────────┐ │
          │  │   Burn     │ │    ┌─────────────────┐
          │  │ Executor   │─┼───▶  Audit Logger    │
          │  └───────────┘ │    │ (tamper-evident)  │
          └────────────────┘    └─────────────────┘
```

## Scenarios

The simulation ships with 9 built-in scenarios covering a range of real-world conditions:

| Scenario | Description | Duration |
|---|---|---|
| SCN-001 | Happy path — single patient, normal operation, full burn cycle | 90 days |
| SCN-002 | Consumer wellness (non-diabetic CGM) — zero clinical retention | 30 days |
| SCN-003 | Consent revocation — third-party data propagation and burn | 30 days |
| SCN-004 | Paediatric-to-adult custodial handover | 60 days |
| SCN-005 | Portable record loss and recovery | 90 days |
| SCN-006 | 48-hour offline period with batch sync | 30 days |
| SCN-009 | Emergency burn — patient-initiated immediate destruction | 14 days |
| SCN-010 | Multi-device patient (CGM + pump + pen) | 90 days |
| SCN-015 | Multi-patient scalability (10 patients) | 30 days |

## Assertions

Every scenario run is validated against a suite of correctness assertions:

- **Burn completeness** — all burn-eligible items were destroyed on schedule
- **Portable record completeness** — the patient vault received all data before relay destruction
- **No data resurrection** — burned items cannot be retrieved from any store
- **World isolation** — no data leaked between typed worlds
- **Audit chain integrity** — tamper-evident log covers every state transition
- **Timing** — burn schedules respected within tolerance
- **Report delivery** — every generated report delivered before raw data burn

## Quick Start

### Requirements

- Python 3.11+
- Dependencies: `numpy`, `scipy`, `flask`, `pyyaml`, `cryptography`

### Install

```bash
pip install -e .
```

### Run a Scenario

```bash
# Run the happy path scenario
chamber-sim run SCN-001

# Run with verbose output
chamber-sim run SCN-001 -v

# Custom seed and time acceleration
chamber-sim run SCN-001 --seed 123 --acceleration 2880
```

### List Available Scenarios

```bash
chamber-sim list-scenarios
```

### View Results

```bash
chamber-sim report sim_output/SCN-001-happy-path
```

### Run Tests

```bash
pytest chamber_sentinel_sim/tests/
```

## Output Structure

Each simulation run produces:

```
sim_output/<scenario-name>/
├── config.json                    # Scenario configuration snapshot
├── stats.json                     # Simulation statistics
├── audit/audit.jsonl              # Tamper-evident audit log
├── assertions/results.json        # Assertion pass/fail results
├── portable_record/<patient>/
│   └── vault.db                   # Patient-held encrypted data vault
├── relay/
│   ├── real_time_therapeutic/     # Per-world SQLite stores
│   ├── clinical_review/
│   ├── device_maintenance/
│   ├── research/
│   ├── patient/
│   └── third_party/
└── third_party/                   # Third-party app stores (if applicable)
```

## Sample Results (SCN-001 Happy Path, 90 days)

| Metric | Value |
|---|---|
| Items generated | 129,388 |
| Items classified | 129,658 |
| Items delivered to vault | 100,019 |
| Items burned | 17 |
| Reports generated | 6 |
| Wall time | 180.6s |

## Supported Devices

**CGMs:** Dexcom G7, Abbott FreeStyle Libre 3, Medtronic Guardian 4, Senseonics Eversense 365

**Pumps:** Tandem t:slim X2/Mobi, Insulet Omnipod 5, Medtronic MiniMed 780G, Ypsomed YpsoPump

**AID Systems:** Control-IQ, Omnipod 5, CamAPS FX, Tidepool Loop

**Connected Pens:** NovoPen 6/Echo Plus, Lilly Tempo

## License

All rights reserved.
