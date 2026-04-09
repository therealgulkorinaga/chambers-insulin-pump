# Product Requirements Document (PRD)
# Chamber Sentinel — Insulin Pump & CGM Data Sovereignty Platform

**Version:** 1.0
**Date:** 2026-04-09
**Status:** Draft
**Source Document:** chamber_sentinel_insulin_cgm_v2.docx (Position Paper — April 2026)

---

## 1. Executive Summary

### 1.1 Purpose
This PRD defines the product requirements for implementing the Chamber Sentinel burden-of-justification framework for insulin pump and continuous glucose monitoring (CGM) ecosystems. The framework enforces a principle that **data persistence in connected medical device ecosystems must be justified by demonstrated clinical safety necessity** — and that any persistence exceeding that justification must be eliminated ("burned") by default.

### 1.2 Problem Statement
Current insulin pump/CGM ecosystems exhibit three systemic failures:

1. **Manufacturers act as mandatory data intermediaries** — all CGM data flows through manufacturer clouds before reaching clinicians; no direct sensor-to-clinician path exists.
2. **Persistence defaults exceed clinical safety necessity** — manufacturers retain raw glucose data indefinitely (e.g., Dexcom: "as long as the product is available for use") despite clinical utility being concentrated in 14–90 day windows.
3. **Patients occupy the weakest custodial position** — they generate all data, bear all consequences, and have the least control over downstream distribution across 90+ third-party apps.

### 1.3 Vision
A data architecture where:
- Data persistence defaults to destruction ("burn") unless a specific clinical safety justification is demonstrated.
- Patients hold the authoritative copy of their health data in a portable, interoperable format.
- Manufacturer retention is time-bounded, purpose-limited, and auditable.
- Consent revocation propagates through the entire data distribution chain.
- Paediatric-to-adult custodial transitions are handled gracefully.

### 1.4 Scope
- **In scope:** CGMs (Dexcom G7, Abbott FreeStyle Libre 3, Medtronic Guardian 4, Senseonics Eversense 365), insulin pumps (Tandem t:slim X2/Mobi, Insulet Omnipod 5, Medtronic MiniMed 780G, Ypsomed YpsoPump), AID systems (Control-IQ, Omnipod 5, CamAPS FX, Tidepool Loop), connected insulin pens (NovoPen 6/Echo Plus, Lilly Tempo), third-party aggregator platforms (Tidepool, Glooko/Diasend, Dexcom Clarity, Tandem Source, Abbott LibreView, Medtronic CareLink).
- **Out of scope:** Pacemaker/cardiac device ecosystems (covered in primary Chamber Sentinel paper), non-connected insulin delivery devices, general EHR/EMR systems.

---

## 2. Stakeholders

| Stakeholder | Role | Key Concern |
|---|---|---|
| Patients (adult) | Data subjects, device operators | Data sovereignty, privacy, portability, revocability |
| Patients (paediatric/adolescent) | Data subjects under custodial management | Graduated autonomy, historical data control at majority |
| Parents/Guardians | Custodial data managers for minors | Real-time safety alerts, appropriate oversight during transition |
| Endocrinologists / Diabetes Care Teams | Clinical data consumers | Sufficient clinical data for treatment decisions (AGP, TIR, patterns) |
| Device Manufacturers (Dexcom, Medtronic, Abbott, Tandem, Insulet, Ypsomed, Senseonics) | Data intermediaries, device producers | Regulatory compliance, algorithm training, safety signal detection, business model viability |
| Third-Party App Developers (90+ ecosystem) | Secondary data recipients via APIs | Data access for app functionality, compliance with burn-propagation requirements |
| Aggregator Platforms (Tidepool, Glooko) | Multi-device data consolidators | Interoperability, data portability, compliance |
| Regulators (FDA, EMA, national authorities) | Oversight | Patient safety, data protection, device classification |
| Insurance / Payer Organizations | Potential downstream data consumers | Risk modelling (identified as a harm vector, not a legitimate use) |
| Security Researchers | Attack surface analysis | BLE security, cloud security, real-time stream integrity |
| Consumer Wellness Users (non-diabetic CGM users) | Non-patient data subjects | No clinical safety justification for any retention — radical default-burn |

---

## 3. Data Ecosystem Architecture

### 3.1 Six-Layer Data Flow Model

#### Layer 1: Sensor/Pump (On-Device Storage)
- **Data types:** Glucose readings (1–5 min intervals), insulin delivery logs, basal rates, bolus history, alarms, AID algorithm decisions
- **Current persistence:** Sensor: until expiry (7–365 days). Pump: rolling buffer, 30–90 days
- **Volume:** ~288 glucose readings/day per CGM = ~105,000/year/patient
- **Required persistence:** Operational state only; constrained by device hardware lifecycle

#### Layer 2: Device → Phone (BLE Transmission)
- **Data types:** Real-time glucose, trends, alerts, insulin data
- **Current persistence:** Cached in app; some retain local history indefinitely
- **Protocol:** Bluetooth Low Energy (BLE)
- **Security concern:** BLE pairing announcements can identify users; encryption is optional on some devices

#### Layer 3: Phone → Manufacturer Cloud (Upload)
- **Data types:** All device data plus app metadata, identifiers, account info
- **Current persistence:** Appears indefinite (Dexcom: "as long as the product is available for use")
- **This is the primary burn target** — the manufacturer cloud is where unjustified indefinite retention occurs

#### Layer 4: Manufacturer Cloud → Clinician (Reports)
- **Data types:** AGP reports, time-in-range, glucose patterns, insulin summaries
- **Current persistence:** Retained in manufacturer cloud; clinician may download to EMR
- **Clinical window:** 14–90 days of data serves all standard clinical review needs

#### Layer 5: Third-Party Apps (API Distribution)
- **Data types:** Glucose, insulin, activity, meal logs, health events
- **Current persistence:** Varies by app; each has own retention policy; re-sharing is common
- **Scale:** Dexcom alone lists 90+ connected health apps
- **Critical problem:** Manufacturer disclaims control once data leaves via API ("no further control or responsibility")

#### Layer 6: Aggregated Pools (Population-Level)
- **Data types:** De-identified (claimed) aggregate statistics, RWE datasets
- **Current persistence:** Indefinite; feeds R&D, regulatory filings, commercial partnerships

### 3.2 Key Structural Differences from Pacemaker Ecosystem

| Dimension | Pacemakers | Insulin Pumps / CGMs |
|---|---|---|
| Data volume | Low: periodic transmissions | Very high: 288+ readings/day, continuous logs, AID decisions |
| Device lifespan | 5–15 years (implanted) | Sensor: 7–365 days. Pump: 4 years. Frequent replacement |
| Intermediary structure | Single manufacturer cloud; no third-party sharing | Manufacturer cloud + 90+ third-party apps via APIs |
| Patient population | Skews older; many elderly/cognitively impaired | Includes many children/adolescents (T1D). More technically engaged |
| Real-time therapeutic dependency | Device paces autonomously; data is for monitoring | Real-time glucose drives insulin dosing. Data loss = immediate therapeutic consequences |
| Regulatory coverage | Unambiguously medical devices; HIPAA applies via HCPs | Medical devices, but mfr-held data may fall outside HIPAA. Consumer wellness blurs further |

---

## 4. Typed Worlds Architecture

The framework organizes data flows into six distinct "worlds," each with defined scope, access controls, and burn schedules.

### 4.1 World 1: Real-Time Therapeutic
- **Data scope:** Current glucose, trend, insulin-on-board (IOB), active basal/bolus, AID algorithm state
- **Access:** Device, app, patient, AID algorithm
- **Burn schedule:** Operational state only. **Never subject to burn. Never persists in manufacturer cloud.**
- **Rationale:** This is the life-critical therapeutic stream. Interruption or corruption can cause immediate patient harm (hypo/hyperglycaemia, incorrect insulin dosing). It must be architecturally firewalled from burn semantics.
- **Requirements:**
  - REQ-RT-001: Real-time data stream must have zero-latency, zero-interference guarantee from any burn mechanism
  - REQ-RT-002: Authenticated encryption of BLE channel between sensor/pump and phone
  - REQ-RT-003: Mutual device authentication between CGM and AID algorithm
  - REQ-RT-004: Integrity verification of glucose readings at AID algorithm input
  - REQ-RT-005: Anomaly detection for implausible glucose values before therapeutic action
  - REQ-RT-006: Real-time data must never transit to or persist in manufacturer cloud as operational state

### 4.2 World 2: Clinical Review
- **Data scope:** AGP reports, glucose patterns, insulin summaries, event logs (14–90 day window)
- **Access:** Treating clinician (via manufacturer portal or direct delivery)
- **Burn schedule:** Burns from manufacturer relay after confirmed delivery to patient's portable record
- **Requirements:**
  - REQ-CR-001: Manufacturer relay generates processed clinical reports (AGP, TIR summaries) from raw data
  - REQ-CR-002: Processed reports are delivered to clinician AND patient's portable record
  - REQ-CR-003: Raw underlying data burns from manufacturer cloud after confirmed report delivery
  - REQ-CR-004: Clinician retains reports in EMR per standard medical record retention
  - REQ-CR-005: 14-day minimum, 90-day maximum raw data retention window for report generation
  - REQ-CR-006: Clinically significant event logs (severe hypoglycaemia, prolonged hyperglycaemia, pump occlusions, sensor failures) must be available until next clinical consultation
  - REQ-CR-007: Report generation must be idempotent — same raw data always produces same report
  - REQ-CR-008: Report sufficiency must be validated by endocrinologists across different clinical contexts before raw data burn is implemented

### 4.3 World 3: Device Maintenance
- **Data scope:** Sensor serial numbers, pump firmware versions, calibration data, hardware performance metrics
- **Access:** Manufacturer (warranty, recall purposes)
- **Burn schedule:** Rolling retention with minimal identifiers; burns on device replacement cycle
- **Requirements:**
  - REQ-DM-001: Retain only minimum identifiers necessary for warranty/recall functions
  - REQ-DM-002: Data burns automatically when device is replaced or decommissioned
  - REQ-DM-003: Sensor warmup periods, calibration events, and sensor accuracy metadata handled seamlessly during sensor replacement transitions
  - REQ-DM-004: Hardware performance data must not include patient glucose values or insulin delivery data
  - REQ-DM-005: Rolling retention window aligned to device warranty period

### 4.4 World 4: Research
- **Data scope:** Consent-gated data; distinguished between aggregable and non-aggregable per primary paper
- **Access:** Manufacturer R&D, academic researchers (under governance)
- **Burn schedule:** Burns on consent withdrawal or research programme completion
- **Requirements:**
  - REQ-RS-001: All research use requires explicit, informed, granular patient consent
  - REQ-RS-002: IRB/ethics review required before data contribution
  - REQ-RS-003: Defined retention periods tied to specific research protocols
  - REQ-RS-004: De-identification or governance appropriate to research protocol
  - REQ-RS-005: Distinguish aggregable data (population statistics) from non-aggregable data (individual traces needed for algorithm training)
  - REQ-RS-006: Non-aggregable data pathway for AID algorithm training: explicit consent, defined retention, ethics review
  - REQ-RS-007: Manufacturer may extract training value during permitted retention window rather than requiring indefinite access
  - REQ-RS-008: Retrospective safety signal detection served through research channel, not operational cloud
  - REQ-RS-009: Longitudinal outcome studies (retinopathy, nephropathy, cardiovascular correlations) require dedicated research repository with appropriate governance
  - REQ-RS-010: Data burns completely upon consent withdrawal — no residual copies
  - REQ-RS-011: Purpose limitation enforced — data contributed for algorithm training cannot be repurposed for insurance risk modelling

### 4.5 World 5: Patient (Portable Record)
- **Data scope:** All patient-generated data in portable, interoperable format
- **Access:** Patient, patient-designated delegates, any authorised clinician
- **Burn schedule:** Patient-controlled (patient decides what to keep and for how long)
- **Requirements:**
  - REQ-PR-001: Patient holds authoritative copy of all their health data
  - REQ-PR-002: Data format must be portable and interoperable (open standards)
  - REQ-PR-003: Patient can retain raw data indefinitely if they choose
  - REQ-PR-004: Patient can burn any or all historical data at any time
  - REQ-PR-005: Patient can delegate access to specific clinicians, family members, or caregivers
  - REQ-PR-006: Portable record must handle sensor replacement transitions (warmup, calibration metadata)
  - REQ-PR-007: Patient must be clearly informed that if they do not save raw data locally and manufacturer burns it, the data cannot be recovered or reprocessed
  - REQ-PR-008: Portable record must support role-based access controls for paediatric custody transitions
  - REQ-PR-009: Patient can grant and revoke manufacturer persistence at any time (patient-elected persistence)
  - REQ-PR-010: Default is burn; persistence requires affirmative patient action
  - REQ-PR-011: Election is granular — patient can elect persistence for some data types but not others

### 4.6 World 6: Third-Party Distribution
- **Data scope:** Data shared via API to authorised apps
- **Access:** Apps authorised by patient
- **Burn schedule:** Burn-propagation requirement — consent revocation must cascade downstream
- **Requirements:**
  - REQ-TP-001: Consent revocation by patient must propagate through entire distribution chain
  - REQ-TP-002: API-level burn-propagation protocol specification
  - REQ-TP-003: Contractual obligations mandating downstream burn upon consent revocation
  - REQ-TP-004: Third-party apps must implement burn endpoints responding to revocation signals
  - REQ-TP-005: Audit mechanism to verify downstream burn compliance (acknowledged as practically difficult)
  - REQ-TP-006: Manufacturer must not disclaim responsibility for data once shared via API — burn obligation transfers
  - REQ-TP-007: Each third-party app must have a published, standardised retention policy
  - REQ-TP-008: Re-sharing by third-party apps must propagate burn obligations to fourth parties
  - REQ-TP-009: Technical enforcement mechanism for burn verification (contractual alone is insufficient)

---

## 5. Theory of Harm — Five Categories

The justification for default-burn rests on five categories of harm from indefinite persistence, ordered from most concrete to most speculative:

### 5.1 Cybersecurity Exposure (Concrete)
- Every persistence point is a potential exfiltration point
- Manufacturer clouds holding years of glucose data for millions of patients are high-value targets
- Healthcare data breaches are frequent and well-documented
- **Requirement:** REQ-HARM-001: Data that has been burned cannot be exfiltrated in a future breach — burn reduces total attack surface

### 5.2 Function Creep (Demonstrated Pattern)
- Data collected for clinical monitoring repurposed for: insurance risk modelling, pharmaceutical market research, employer wellness analytics, advertising targeting
- Manufacturer privacy policies reserve broad rights ("improving products and services," "business partners," "research")
- **Requirement:** REQ-HARM-002: Purpose limitation must be architecturally enforced, not just policy-stated

### 5.3 Inferential Richness (Growing Risk)
- Continuous glucose traces reveal: sleep patterns, meal timing/composition, alcohol consumption, stress responses, menstrual cycles, medication adherence, exercise habits
- Analytical techniques will improve — data innocuous today becomes deeply revealing tomorrow
- **Requirement:** REQ-HARM-003: Indefinite persistence means patients cannot anticipate what their data will reveal to future analytical methods — burn limits this exposure

### 5.4 Loss of Practical Revocability (Structural)
- With 90+ connected apps, each with downstream sharing, practical revocability diminishes toward zero over time
- Every additional day of persistence at the distribution hub increases propagation surface
- **Requirement:** REQ-HARM-004: Burn at source (manufacturer cloud) limits the window during which data can propagate to uncontrollable downstream systems

### 5.5 Power Asymmetry Entrenchment (Systemic)
- Indefinite data accumulation creates structural dependency
- Patients cannot switch manufacturers if longitudinal records are locked in proprietary clouds
- Data becomes competitive moat; patient choice constrained by migration impossibility
- **Requirement:** REQ-HARM-005: Portable record + burn defaults prevent manufacturer lock-in through data accumulation

---

## 6. Counterargument Accommodation

The framework must engage with and accommodate legitimate manufacturer interests without abandoning the burn-default principle.

### 6.1 Retrospective Safety Signal Detection
- **Legitimate interest:** Detecting safety signals (e.g., sensor accuracy degradation over years)
- **Framework response:** Served by Research World (World 4) with consent-gated, governed access
- **Requirement:** REQ-CA-001: Dedicated safety signal research repository, separate from operational cloud, with appropriate governance

### 6.2 Longitudinal Outcome Studies
- **Legitimate interest:** Correlating glucose management with long-term health outcomes
- **Framework response:** Research World with explicit consent, IRB/ethics review, defined retention
- **Requirement:** REQ-CA-002: Outcome study data handled through Research World, not indefinite operational retention

### 6.3 Algorithm Training (Strongest Counterargument)
- **Legitimate interest:** AID algorithms improve through training on real-world glucose/insulin data — direct patient benefit
- **Framework response:** Research World non-aggregable pathway. Manufacturers extract training value during permitted retention window.
- **Acknowledged trade-off:** Whether time-limited access is sufficient for state-of-the-art algorithm development is an empirical question
- **Requirement:** REQ-CA-003: Algorithm training through governed research channel. Empirical validation needed on whether time-bounded access degrades algorithm quality.

### 6.4 Care Continuity and Patient Convenience
- **Legitimate interest:** Complete glucose history in single platform, accessible to any clinician
- **Framework response:** Served by portable record (World 5) + patient-elected persistence
- **Requirement:** REQ-CA-004: Patients who want manufacturer retention can opt in. Default is burn. Persistence is opt-in, not opt-out.

### 6.5 Manufacturer Behavioural Response Mitigation
- **Risk:** Manufacturers may front-load value extraction during permitted retention window (more aggressive training, more frequent exports)
- **Framework gap:** Burn semantics constrain duration but not intensity of use
- **Requirement:** REQ-CA-005: Supplementary governance needed — purpose limitation, use-based constraints, audit requirements during retention window. Architectural controls alone are insufficient.

---

## 7. Consumer Wellness CGM Requirements

### 7.1 The Radical Conclusion
For non-diabetic consumers using CGM as a wellness tool (e.g., Dexcom Stelo), there is **no clinical safety justification for any manufacturer data retention** beyond real-time display.

### 7.2 Requirements
- REQ-CW-001: For consumer wellness products, ALL manufacturer data retention defaults to zero/burn
- REQ-CW-002: Any retention requires explicit, informed, granular opt-in from the consumer
- REQ-CW-003: Consumer wellness users must not be treated as patients for data governance purposes unless they opt in
- REQ-CW-004: Same data architecture, different default — identical glucose data from identical sensors gets different persistence treatment based on user classification (patient vs. consumer)
- REQ-CW-005: If manufacturer business model cannot sustain without indefinite retention of consumer wellness data, this confirms the model depends on data monetisation — this fact must be disclosed to consumers

---

## 8. Paediatric and Adolescent Custodial Transition Requirements

### 8.1 Problem Statement
Many insulin pump/CGM users are children with Type 1 diabetes. The framework's "patient-as-vault-owner" principle assumes a single, stable autonomous agent. This fails for paediatric users where:
- A parent sets up the CGM account for an 8-year-old
- Over 10+ years, the child matures into an autonomous adolescent
- The transition is gradual, not binary
- The appropriate moment for custodial transfer is not standardised

### 8.2 Graduated Delegation Authority Requirements
- REQ-PED-001: Architecture supports graduated custody model: parent full authority → shared authority → young adult exclusive authority
- REQ-PED-002: Shared authority phase begins at configurable age (suggested 13–16 range, jurisdictionally variable)
- REQ-PED-003: During shared authority, adolescent can restrict parental access to historical data
- REQ-PED-004: During shared authority, parent retains access to real-time safety alerts
- REQ-PED-005: Young adult gains exclusive authority at age of majority
- REQ-PED-006: Role-based access controls with time-scoped permissions
- REQ-PED-007: Custody transfer protocols (currently do not exist in any consumer or medical data system)

### 8.3 Right to Historical Data Restriction
- REQ-PED-008: Upon assuming exclusive custody, young adult can burn historical data from parental-management period
- REQ-PED-009: A 20-year-old is not bound by data persistence choices made by parents when they were 8
- REQ-PED-010: Burn of parental-era data must be complete and irreversible

### 8.4 Acknowledged Complexity
- REQ-PED-011: This graduated model requires role-based access controls, time-scoped permissions, and custody transfer protocols that **do not currently exist** in any consumer or medical data system — this is an engineering requirement, not a solved problem

---

## 9. Cybersecurity Requirements

### 9.1 Attack Surface
The insulin pump/CGM ecosystem presents a broader attack surface than pacemakers:
- Continuously active Bluetooth
- Multiple third-party data recipients
- Smartphone as critical therapeutic node
- Extremely granular metabolic data

### 9.2 Known Vulnerabilities
- Insulin pump commands intercepted over unencrypted radio frequencies (published research)
- Bluetooth pairing announcements identifying users
- Authentication and encryption in pump communication are optional features

### 9.3 Requirements
- REQ-SEC-001: Authenticated encryption of BLE channel (sensor ↔ phone, pump ↔ phone)
- REQ-SEC-002: Mutual device authentication between all paired devices
- REQ-SEC-003: Integrity verification of glucose readings at AID algorithm input
- REQ-SEC-004: Anomaly detection for implausible glucose values before therapeutic action
- REQ-SEC-005: Burn semantics architecturally firewalled from real-time therapeutic stream — not merely specified that way
- REQ-SEC-006: Real-time stream protection is orthogonal to burn semantics — both are required
- REQ-SEC-007: Manufacturer cloud security hardened for reduced but still present data persistence
- REQ-SEC-008: Third-party app security requirements as condition of API access
- REQ-SEC-009: Incident response plan covering real-time data stream compromise (highest severity)

### 9.4 Honest Limitation
- REQ-SEC-010: The framework reduces total attack surface (historical data eliminated) but **does not address** the most safety-critical attack vector (real-time data integrity). Real-time protection requires orthogonal measures.

---

## 10. The Raw Data vs. Report Distinction

### 10.1 Principle
- A 14-day AGP report = a few kilobytes
- The underlying raw glucose data = tens of thousands of individual readings
- Clinical utility is concentrated in the processed report
- Commercial and research value is concentrated in the raw data

### 10.2 Proposed Burn Boundary
- REQ-RR-001: Manufacturer relay generates processed report from raw data
- REQ-RR-002: Processed report delivered to clinician and patient's portable record
- REQ-RR-003: Manufacturer burns underlying raw data after confirmed report delivery
- REQ-RR-004: Patient's portable record retains raw data if patient chooses
- REQ-RR-005: Manufacturer does not retain raw data regardless of patient choice (unless patient explicitly elects manufacturer persistence)

### 10.3 Acknowledged Limitations
- REQ-RR-006: If manufacturer burns raw data and patient did not save locally, manufacturer cannot generate new analyses from that period
- REQ-RR-007: Manufacturer cannot contribute that data to research even if patient later consents
- REQ-RR-008: Processed reports cannot be "unprocessed" back into raw data
- REQ-RR-009: Patients must be clearly informed of this trade-off before opting out of portable record raw data retention

---

## 11. Data Ownership and Legal Infrastructure

### 11.1 Current Gap
- No legislation in US or EU explicitly recognises ownership rights over medical device data
- Framework sidesteps ownership by focusing on custodial defaults and burden of proof
- But: if patient has no property interest in their glucose data, what is the legal mechanism for enforcing burn semantics?

### 11.2 Requirements
- REQ-OWN-001: Enforcement mechanism must be identified from: (a) legislative recognition of patient data property rights, (b) contractual obligations in device purchase/subscription terms, or (c) regulatory mandates for data minimisation not depending on ownership
- REQ-OWN-002: Framework governance claim ("whoever holds data must justify retention") needs at minimum one of the above legal bases
- REQ-OWN-003: Until legislative infrastructure exists, contractual and regulatory mechanisms are the available enforcement paths

---

## 12. Operational Preconditions

### 12.1 Non-Negotiable Preconditions
- REQ-OP-001: **Zero interference with real-time CGM-to-pump data flow** — any architecture change must guarantee this absolutely
- REQ-OP-002: Burn semantics architecturally firewalled from therapeutic stream
- REQ-OP-003: Sensor replacement transitions handled seamlessly (warmup periods, calibration events, accuracy metadata)

### 12.2 Verification Requirements
- REQ-OP-004: Third-party API revocation enforcement mechanism — verifying apps actually burn data upon consent revocation
- REQ-OP-005: Report sufficiency validation — endocrinologist validation that processed reports serve clinical needs across all clinical contexts
- REQ-OP-006: Paediatric custody transition protocols tested across jurisdictions with varying age-of-majority laws

### 12.3 Failure Mode Requirements
- REQ-OP-007: If burn mechanism fails, data must not be exposed — fail-safe to retention, not fail-safe to deletion of therapeutically active data
- REQ-OP-008: If portable record is unavailable, manufacturer must queue (not burn) clinical data until delivery is confirmed
- REQ-OP-009: If burn-propagation signal fails to reach third-party app, audit trail must flag the failure for manual follow-up

---

## 13. Regulatory Gap Requirements

### 13.1 Current State
- CGM data held by manufacturers does not always receive equivalent protection to data held by HCPs
- HIPAA Privacy Rule applies when a covered entity or business associate holds data — but CGM manufacturers may not qualify as either in all contexts
- Patient data in manufacturer cloud may face fewer legal constraints than the same data in clinician's EMR
- Consumer wellness positioning (e.g., Dexcom Stelo) widens this gap further

### 13.2 Requirements
- REQ-REG-001: Framework must function regardless of whether manufacturer qualifies as HIPAA covered entity
- REQ-REG-002: Data governance must not depend on regulatory classification of user as "patient" vs. "consumer"
- REQ-REG-003: Same glucose data from same sensor architecture must receive consistent protection regardless of marketing positioning
- REQ-REG-004: Framework should anticipate and support future regulatory mandates for data minimisation

---

## 14. Success Criteria

| Criterion | Metric | Target |
|---|---|---|
| Default persistence | Manufacturer cloud retention of raw data beyond clinical window | Zero (burn after report generation + confirmed delivery) |
| Patient data sovereignty | % of patients with portable record containing their complete data | >80% within 2 years of deployment |
| Burn propagation | % of third-party apps implementing burn-propagation protocol | 100% for new API partnerships; 80% of existing within 18 months |
| Clinical data availability | Clinician access to AGP/TIR reports for treatment decisions | 100% — no degradation from current state |
| Real-time therapeutic integrity | Incidents of burn mechanism interfering with therapeutic data stream | Zero (absolute requirement) |
| Paediatric transitions | Successful custody transfers without data loss or access gaps | 100% |
| Consent revocation latency | Time from patient revocation to complete downstream burn | <72 hours (target), <30 days (maximum) |
| Consumer wellness compliance | Manufacturer retention for non-opted-in wellness users | Zero |

---

## 15. Open Questions and Acknowledged Unknowns

8. **Simulation fidelity:** Do synthetic glucose traces from physiological models adequately represent real-world device behaviour for architecture validation? Simulation results must be cross-checked against real device data when available.

1. **Algorithm training sufficiency:** Can state-of-the-art AID algorithms be trained effectively with time-bounded data access rather than indefinite retention? (Empirical question — framework cannot answer)
2. **Burn-propagation feasibility:** API-level burn-propagation protocols are technically novel. No reference implementation exists.
3. **Legal enforcement mechanism:** Without legislative data property rights, enforcement depends on contractual and regulatory mechanisms that are currently insufficient.
4. **Report sufficiency:** Assumption that processed reports serve all clinical needs must be validated by endocrinologists across specialties and clinical contexts.
5. **Business model viability:** If consumer wellness CGM business models depend on data monetisation, the framework's radical conclusion (zero default retention) may be commercially unworkable — this is acknowledged as informative rather than disqualifying.
6. **Manufacturer behavioural response:** Burn constraints on duration may cause front-loading of value extraction during retention window — supplementary governance needed but not designed.
7. **International jurisdictional variation:** Age of majority, data protection law, medical device regulation vary by jurisdiction — framework must be adaptable.

---

## 16. Local Simulation Environment

### 16.1 Purpose
The Chamber Sentinel framework describes an architecture that spans devices, phones, manufacturer clouds, third-party apps, and patient-controlled portable records. Before any production implementation, the entire data lifecycle must be demonstrable, testable, and auditable in a **fully local simulation environment** — no external servers, no cloud dependencies, no network calls to real manufacturer APIs. The simulation proves the architecture works end-to-end before any stakeholder is asked to trust it.

### 16.2 Design Principles
- **Fully local:** Runs entirely on a single developer machine (laptop/workstation). All components containerised or process-isolated. Zero external network dependencies.
- **Full loop:** Covers the complete data lifecycle: simulated patient/device → manufacturer relay → typed world classification → burn execution → portable record delivery → burn verification.
- **Deterministic and reproducible:** Same inputs produce same outputs. Random seeds configurable. Every simulation run produces an audit-grade log.
- **Time-accelerated:** Simulates days, weeks, or months of data flow in minutes. Configurable time acceleration factor (1x real-time through 10,000x).
- **Scenario-driven:** Pre-built scenarios covering normal operation, edge cases, failure modes, and adversarial conditions.
- **Observable:** Every data item is traceable from creation to burn, with full provenance chain visible in real-time dashboards.

### 16.3 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LOCAL SIMULATION HOST                             │
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │  SIMULATED   │    │  SIMULATED   │    │    SIMULATED          │  │
│  │  PATIENT     │    │  PHONE/APP   │    │    MANUFACTURER       │  │
│  │  DEVICES     │    │              │    │    RELAY               │  │
│  │              │    │              │    │                       │  │
│  │ CGM Engine   │BLE │ App Runtime  │HTTP│  Cloud Stub           │  │
│  │ Pump Engine  ├───►│ AID Algo     ├───►│  World Classifier     │  │
│  │ Pen Engine   │sim │ Local Cache  │sim │  Report Generator     │  │
│  │              │    │              │    │  Burn Scheduler       │  │
│  └──────────────┘    └──────────────┘    │  Burn Executor        │  │
│                                          │  Audit Logger         │  │
│                                          └─────────┬─────────────┘  │
│                                                    │                │
│                              ┌──────────────────────┘               │
│                              │                                      │
│                              ▼                                      │
│  ┌───────────────────────┐  ┌───────────────────────┐              │
│  │  SIMULATED            │  │  SIMULATED            │              │
│  │  THIRD-PARTY APPS     │  │  PORTABLE RECORD      │              │
│  │                       │  │                       │              │
│  │  App A (fitness)      │  │  Patient Vault        │              │
│  │  App B (clinical)     │  │  Access Control       │              │
│  │  App C (aggregator)   │  │  Burn Controls        │              │
│  │  Burn Endpoint Stubs  │  │  Report Viewer        │              │
│  └───────────────────────┘  └───────────────────────┘              │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  SIMULATION CONTROL PLANE                                    │   │
│  │  Clock Controller │ Scenario Runner │ Dashboard │ Audit Log  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 16.4 Simulated Components

#### 16.4.1 Simulated Patient Devices

**CGM Engine**
- Generates synthetic glucose traces using physiological models (meal absorption, insulin action, dawn phenomenon, exercise response, sensor noise)
- Configurable patient profiles: well-controlled T1D, poorly-controlled T1D, T2D, gestational diabetes, consumer wellness (non-diabetic)
- Configurable sensor models: Dexcom G7 (5-min intervals, 10-day wear), Libre 3 (1-min, 14-day), Guardian 4 (5-min, 7-day), Eversense (5-min, 365-day)
- Simulates sensor warmup, calibration, drift, noise, and failure modes
- Output: timestamped glucose readings with sensor metadata, transmitted to simulated phone via in-process BLE simulation
- Requirements:
  - REQ-SIM-001: CGM engine produces physiologically plausible glucose traces validated against published CGM datasets (e.g., Ohio T1DM, REPLACE-BG)
  - REQ-SIM-002: Configurable patient profiles with at least 8 archetypes (child T1D, adolescent T1D, adult T1D well-controlled, adult T1D poorly-controlled, adult T2D, gestational, elderly T2D, consumer wellness)
  - REQ-SIM-003: Sensor noise model calibrated per manufacturer specifications (MARD: Dexcom G7 ~8.2%, Libre 3 ~7.9%, Guardian 4 ~8.7%)
  - REQ-SIM-004: Sensor failure injection (signal loss, compression lows, early termination) at configurable rates

**Pump Engine**
- Generates insulin delivery events: basal rates, bolus deliveries (normal, extended, correction), temporary basal adjustments
- Configurable pump models: Tandem t:slim X2 (300U reservoir, 0.001U increment), Omnipod 5 (200U pod, 72h wear), MiniMed 780G (300U, auto mode)
- Simulates reservoir changes, infusion set changes, occlusions, and pump alarms
- Requirements:
  - REQ-SIM-005: Pump engine accurately models insulin delivery mechanics (delivery delay, occlusion detection, reservoir tracking)
  - REQ-SIM-006: Pump events generated in response to AID algorithm commands (closed-loop operation) or manual bolus inputs (open-loop)

**AID Algorithm Stub**
- Simplified closed-loop algorithm: receives glucose readings, calculates IOB, adjusts basal, recommends corrections
- Not a production-grade AID — sufficient to generate realistic algorithm decision data (predictions, adjustments, mode changes)
- Configurable aggressiveness, target range, and insulin sensitivity
- Requirements:
  - REQ-SIM-007: AID stub generates all data types produced by real AID systems: predicted glucose (30/60/90 min), basal adjustment magnitude, auto-bolus amounts, mode transitions, insulin-on-board
  - REQ-SIM-008: AID stub operates in real-time within the simulation clock (responds to each CGM reading within simulated time constraints)

**Connected Pen Engine**
- Generates injection events: dose amount, timestamp, pen serial number, cartridge temperature
- Configurable pen models: NovoPen 6 (basal), Echo Plus (rapid-acting), Lilly Tempo
- Requirements:
  - REQ-SIM-009: Pen engine generates injection events at meal times and correction times per patient profile

#### 16.4.2 Simulated Phone/App Layer

- Receives data from simulated devices via in-process message passing (simulating BLE)
- Runs AID algorithm stub (for pump users)
- Maintains local app cache with configurable retention
- Uploads data to simulated manufacturer relay via local HTTP (localhost)
- Simulates: app restart (cache recovery), phone reboot (state recovery), connectivity loss (offline queuing)
- Requirements:
  - REQ-SIM-010: Phone/app layer caches data locally and uploads to relay on configurable schedule (immediate, batched every 5 min, batched every hour)
  - REQ-SIM-011: Simulates offline periods where data accumulates locally and uploads upon reconnection
  - REQ-SIM-012: App layer enforces real-time therapeutic stream isolation — burn commands from relay never affect app-layer therapeutic data

#### 16.4.3 Simulated Manufacturer Relay

The core of the simulation — implements the full Chambers architecture locally.

**Cloud Stub**
- Local HTTP server (localhost, configurable port) receiving data from simulated phone/app
- Implements all six Typed Worlds as isolated data stores (separate SQLite databases or separate directories)
- Requirements:
  - REQ-SIM-013: Relay runs as a local process (no Docker required for basic operation; Docker optional for isolation testing)
  - REQ-SIM-014: Each Typed World has physically separate storage (separate database files), not just logical separation
  - REQ-SIM-015: Relay accepts data via REST API identical in shape to a real manufacturer API (Dexcom API v3 compatible request/response format as reference)

**World Classifier**
- Receives incoming data items and classifies each into exactly one Typed World based on the data taxonomy
- Classification rules configurable via YAML/JSON policy file
- Logs every classification decision with rationale
- Requirements:
  - REQ-SIM-016: Every data item receives a world classification within 100ms of receipt
  - REQ-SIM-017: Classification policy is hot-reloadable (change policy without restarting simulation)
  - REQ-SIM-018: Unclassifiable data items default to the most restrictive burn schedule and generate a classification warning

**Report Generator**
- Generates clinical reports (AGP, TIR, glucose statistics) from raw data in the Clinical Review world
- Reports delivered to both simulated clinician endpoint and simulated portable record
- Requirements:
  - REQ-SIM-019: AGP report generated from 14 days of simulated CGM data, matching the structure of a real Dexcom Clarity or LibreView AGP
  - REQ-SIM-020: Reports include: median glucose, glucose management indicator (GMI), coefficient of variation (CV), time-in-range breakdown (very low <54, low 54–69, in-range 70–180, high 181–250, very high >250), daily glucose profiles
  - REQ-SIM-021: Report delivered to portable record before raw data burn is eligible

**Burn Scheduler**
- Tracks every data item's burn eligibility based on world classification, delivery confirmations, and time elapsed
- Configurable burn schedules per world (specified in minutes/hours for simulation, representing days/months in real time)
- Burn scheduling engine with pending/eligible/executed/failed states
- Requirements:
  - REQ-SIM-022: Burn scheduler processes burn eligibility checks every simulation tick
  - REQ-SIM-023: Burn eligibility requires: (a) data classified into a world, (b) world-specific burn trigger satisfied (time elapsed OR event-based confirmation), (c) no legal hold or pending delivery blocking burn
  - REQ-SIM-024: Burn schedule dashboard shows every data item's lifecycle state in real-time

**Burn Executor**
- Performs the actual data destruction
- Implements multiple burn mechanisms (configurable): file deletion, cryptographic erasure (key destruction), overwrite-and-delete
- Verifies burn completion and logs result
- Requirements:
  - REQ-SIM-025: Burn executor cryptographically verifies data is irrecoverable after burn (attempts to read burned data must fail)
  - REQ-SIM-026: Burn execution generates an audit record containing: data item ID, world, burn trigger, burn mechanism, timestamp, verification result — but NOT the data content
  - REQ-SIM-027: Failed burns are retried with exponential backoff; after 3 failures, burn is marked failed and alert generated

**Audit Logger**
- Append-only, hash-chained audit log of every significant event: data receipt, classification, world assignment, report generation, delivery confirmation, burn scheduling, burn execution, burn verification
- Log is the ground truth for simulation validation
- Requirements:
  - REQ-SIM-028: Audit log is append-only; no log entry can be modified or deleted during simulation
  - REQ-SIM-029: Each log entry includes a cryptographic hash of the previous entry (hash chain for tamper detection)
  - REQ-SIM-030: Audit log queryable by: data item ID, world, event type, time range, patient ID

#### 16.4.4 Simulated Third-Party Apps

- 3 simulated third-party app stubs representing different categories:
  - **App A (Fitness/Wellness):** Receives glucose data via simulated API, stores locally, shares downstream to a simulated sub-processor
  - **App B (Clinical Decision Support):** Receives glucose + insulin data, generates clinical recommendations, stores data in local database
  - **App C (Aggregator/Tidepool-like):** Receives data from multiple simulated patients, aggregates, produces population reports
- Each app implements a burn endpoint responding to burn-propagation signals from the manufacturer relay
- Requirements:
  - REQ-SIM-031: Each simulated third-party app maintains its own data store (separate from relay and portable record)
  - REQ-SIM-032: Apps receive burn-propagation signals and execute burn within configurable SLA
  - REQ-SIM-033: App A simulates re-sharing to a downstream sub-processor (4th party); burn must propagate through the full chain
  - REQ-SIM-034: One app can be configured to "refuse" or "delay" burn to test non-compliance handling
  - REQ-SIM-035: App data stores are inspectable to verify burn completion

#### 16.4.5 Simulated Portable Record (Patient Vault)

- Local file-based patient data store, encrypted at rest
- Receives data deliveries from manufacturer relay
- Sends delivery confirmations back to relay (triggering burn eligibility)
- Supports patient-initiated operations: browse data, export, share with clinician, burn own data
- Requirements:
  - REQ-SIM-036: Portable record stores all data in an encrypted local directory using AES-256
  - REQ-SIM-037: Delivery confirmation is a signed acknowledgement including hash of received data
  - REQ-SIM-038: Portable record can be "lost" (directory deleted) to simulate data loss scenarios — manufacturer relay must handle gracefully (no burn of undelivered data)
  - REQ-SIM-039: Patient can browse, query, and export data from the portable record via CLI or local web UI
  - REQ-SIM-040: Patient can initiate selective burns from their portable record

### 16.5 Simulation Control Plane

#### 16.5.1 Clock Controller
- Virtual clock driving all simulation time
- Configurable acceleration: 1x (real-time), 60x (1 hour = 1 minute), 1440x (1 day = 1 minute), 10080x (1 week = 1 minute)
- Pause, resume, step-forward (advance by N minutes), and jump-to-time controls
- All components synchronised to the virtual clock
- Requirements:
  - REQ-SIM-041: All timestamps in all components derived from virtual clock, not system clock
  - REQ-SIM-042: Clock acceleration does not skip events (every CGM reading is generated even at 10,000x)
  - REQ-SIM-043: Clock can be paused mid-simulation for inspection without data loss or state corruption

#### 16.5.2 Scenario Runner
Pre-built scenarios that exercise the full architecture:

| Scenario ID | Name | Description | Duration (sim time) |
|---|---|---|---|
| SCN-001 | Happy Path | Single patient, 90 days, normal CGM + pump operation, reports generated, raw data burned on schedule, portable record receives all data | 90 days |
| SCN-002 | Sensor Transition | Patient replaces CGM sensor mid-simulation; warmup period, overlapping data, seamless transition in reports | 14 days |
| SCN-003 | Consent Revocation | Patient revokes consent for App A; burn-propagation signal sent, App A burns data, sub-processor burns data, verification confirmed | 30 days |
| SCN-004 | Non-Compliant App | Patient revokes consent; App A refuses to burn; escalation path exercised (warning → API revocation) | 30 days |
| SCN-005 | Portable Record Loss | Patient's portable record destroyed mid-simulation; relay detects missing confirmation; data queued, not burned; patient creates new record; data re-delivered | 60 days |
| SCN-006 | Offline Period | Patient offline for 48 hours; data accumulates on phone; reconnects; batch upload; burn timers adjusted | 14 days |
| SCN-007 | Paediatric Transition | Child patient transitions through Phase 1 → Phase 2 (shared authority) → Phase 3 (exclusive authority); parent access changes at each phase; young adult burns parental-era data | 10 years |
| SCN-008 | Consumer Wellness | Non-diabetic consumer user; zero-retention default; all data burned from relay immediately after display; no manufacturer persistence | 30 days |
| SCN-009 | Emergency Burn | Patient triggers emergency burn ("panic button"); all data across all worlds and all third-party apps burned within 1 hour | 7 days |
| SCN-010 | Multi-Device Patient | Patient using Dexcom G7 + Tandem t:slim X2 + NovoPen 6; data from three sources flows through relay; integrated reports generated; all sources subject to burn schedules | 90 days |
| SCN-011 | AID Algorithm Data Classification | AID system generates both summary metrics and raw decision logs; summary goes to Clinical Review, raw logs to Research (consent-gated); verify burn schedules differ per world | 30 days |
| SCN-012 | Research Consent and Withdrawal | Patient consents to research use of data; data enters Research world; patient withdraws consent; Research world data burns; verify burn does not affect Clinical Review data | 180 days |
| SCN-013 | Report Sufficiency | Clinician requests retrospective analysis after raw data burn; system returns generated report and directs to portable record for raw data; verifies report-only pathway works | 90 days |
| SCN-014 | Burn Mechanism Failure | Burn executor encounters simulated failure (storage unavailable); retries; escalates; verifies no data leaked during failure period | 30 days |
| SCN-015 | Concurrent Multi-Patient | 100 simulated patients generating data simultaneously; verify burn scheduler handles load without skipping or delaying burns | 30 days |
| SCN-016 | Legal Hold | Legal hold placed on patient's data mid-simulation; burn suspended for affected data; hold lifted; burn resumes and executes | 90 days |
| SCN-017 | Manufacturer Insolvency | Manufacturer wind-down scenario; all patient data exported to portable records; all pending burns executed; verify zero data remains in relay after wind-down | 30 days |
| SCN-018 | Timezone Traversal | Patient travels across 6 timezones during simulation; verify burn schedules, reports, and timestamps handle transitions correctly | 14 days |
| SCN-019 | Adversarial Burn Prevention | Simulated attacker attempts to prevent burns (hold injection, clock manipulation, storage lock); verify burn mechanism resilience | 7 days |
| SCN-020 | Full Lifecycle Stress Test | 50 patients, 1 year simulated time, all device types, all scenarios interleaved randomly; verify system correctness under compound stress | 365 days |

- Requirements:
  - REQ-SIM-044: Each scenario is defined as a declarative YAML file specifying: patient profiles, device configurations, event schedule, expected outcomes
  - REQ-SIM-045: Scenario runner validates expected outcomes automatically (assertion-based) and produces pass/fail report
  - REQ-SIM-046: Custom scenarios can be authored by combining primitives (patient profiles, event triggers, failure injections)
  - REQ-SIM-047: Scenario execution is deterministic — same scenario file produces identical results across runs (given same random seed)

#### 16.5.3 Simulation Dashboard
- Local web UI (localhost) providing real-time visibility into the simulation
- Requirements:
  - REQ-SIM-048: Dashboard shows live data flow: readings generated → classified → stored → report generated → delivered → burned
  - REQ-SIM-049: Per-data-item lifecycle view: click any data item to see its full journey from creation to burn (or current state)
  - REQ-SIM-050: World occupancy view: how much data is in each Typed World at any moment (line chart over time — should trend downward as burns execute)
  - REQ-SIM-051: Burn queue view: pending burns, next scheduled burn, overdue burns, failed burns
  - REQ-SIM-052: Third-party app state view: data held by each app, pending burn-propagation signals, compliance status
  - REQ-SIM-053: Portable record state view: data received, confirmations sent, patient-initiated burns
  - REQ-SIM-054: Audit log viewer with filtering and search
  - REQ-SIM-055: Dashboard runs as a static SPA served by a local HTTP server; no external CDN or API dependencies

#### 16.5.4 Validation and Assertion Engine
- Automated validation that the simulation behaved correctly
- Requirements:
  - REQ-SIM-056: **Burn completeness assertion:** after a scenario completes, verify that every data item that should have been burned has been burned (query all data stores; burned items must return empty)
  - REQ-SIM-057: **Portable record completeness assertion:** every data item classified for the Patient world was delivered to and is present in the portable record
  - REQ-SIM-058: **No data resurrection assertion:** no data item that was burned reappears in any data store at any subsequent point in the simulation
  - REQ-SIM-059: **Burn-propagation completeness assertion:** every burn-propagation signal sent to a third-party app resulted in a confirmed burn (or a documented non-compliance escalation)
  - REQ-SIM-060: **World isolation assertion:** no data item was ever stored in a world it was not classified for
  - REQ-SIM-061: **Real-time stream isolation assertion:** burn operations never caused latency or data loss in the real-time therapeutic stream
  - REQ-SIM-062: **Audit chain integrity assertion:** audit log hash chain is unbroken from first to last entry
  - REQ-SIM-063: **Timing assertion:** all burns executed within their SLA (configurable per world)
  - REQ-SIM-064: **Report delivery assertion:** every clinical report was delivered to both clinician endpoint and portable record before raw data burn
  - REQ-SIM-065: **Custody transition assertion:** (for paediatric scenarios) access controls changed correctly at each transition phase

### 16.6 Technology Stack (Reference Implementation)

| Component | Technology | Rationale |
|---|---|---|
| Simulation runtime | Python 3.11+ | Accessibility, rapid prototyping, scientific libraries for glucose modelling |
| CGM/Pump engines | Python (NumPy/SciPy for physiological models) | Physiological signal generation with established mathematical models |
| Manufacturer relay | Python (FastAPI or Flask) on localhost | Lightweight local HTTP server; REST API compatible |
| Data stores | SQLite (one database per Typed World) | Zero-config, file-based, inspectable, no external database server |
| Burn executor | Python + OS-level file operations | Direct file deletion + optional cryptographic erasure |
| Portable record | Encrypted local directory (Python cryptography library, AES-256-GCM) | Patient vault as encrypted filesystem |
| Third-party app stubs | Python (Flask micro-instances on different localhost ports) | Simulates multiple independent apps |
| Simulation clock | Custom virtual clock (Python) | Decoupled from wall-clock for time acceleration |
| Dashboard | Local web UI (HTML/JS, served by Python) | No build step, no npm, no framework dependency; vanilla JS + lightweight charting |
| Scenario definitions | YAML files | Human-readable, version-controllable, diffable |
| Audit log | Append-only JSON lines file with SHA-256 hash chain | Simple, inspectable, tamper-evident |
| Test framework | pytest | Standard Python testing; scenario assertions as test cases |
| Configuration | YAML/TOML | All simulation parameters in config files, no hardcoded values |

- Requirements:
  - REQ-SIM-066: Entire simulation installable with `pip install -e .` and runnable with `python -m chamber_sentinel_sim`
  - REQ-SIM-067: No Docker, Kubernetes, or cloud services required for basic operation
  - REQ-SIM-068: No external network calls during simulation (enforced by simulation framework; fails loudly if any component attempts external network access)
  - REQ-SIM-069: Runs on macOS, Linux, and Windows
  - REQ-SIM-070: Complete simulation of SCN-001 (90-day happy path) completes in <5 minutes on a standard laptop at maximum acceleration
  - REQ-SIM-071: All simulation state persisted to a single output directory; entire simulation reproducible by re-running with the same config and seed

### 16.7 Simulation Data Flow — Full Loop Walkthrough

**Step 1: Patient Device Generates Data**
CGM engine generates a glucose reading (e.g., `{patient_id: "P001", timestamp: "2026-04-09T14:35:00Z", glucose_mg_dl: 142, sensor_id: "SN-G7-00412", trend: "flat"}`). Pump engine generates concurrent basal delivery event. AID algorithm processes glucose and issues basal adjustment.

**Step 2: Phone/App Receives and Caches**
Simulated app receives reading via in-process message. AID algorithm acts on it (real-time therapeutic world — operational state, not persisted upstream). App caches the reading and queues for upload to relay.

**Step 3: Upload to Manufacturer Relay**
App uploads batch to relay via `POST /api/v1/upload` on localhost. Relay receives, acknowledges, and passes to World Classifier.

**Step 4: World Classification**
World Classifier examines each data item:
- Glucose reading → Clinical Review world (14–90 day burn schedule)
- AID summary metric → Clinical Review world
- AID raw decision log → Research world (consent-gated, longer retention)
- Sensor metadata → Device Maintenance world (burns on sensor replacement)
- Glucose reading also forwarded to Report Generator queue

**Step 5: Report Generation**
After 14 days of accumulated data, Report Generator produces an AGP report. Report delivered to simulated clinician endpoint AND simulated portable record.

**Step 6: Portable Record Delivery Confirmation**
Portable record receives report + raw data. Sends signed confirmation (hash of received data + patient key signature) back to relay.

**Step 7: Burn Eligibility**
Burn Scheduler checks: Clinical Review world glucose readings from 14+ days ago, delivery confirmed to portable record → eligible for burn. Moves items to burn queue.

**Step 8: Burn Execution**
Burn Executor destroys eligible data items from relay's Clinical Review database. Verifies destruction (attempts to read → fails). Generates audit log entry.

**Step 9: Third-Party Burn Propagation**
If glucose data was also shared with App A, burn-propagation signal sent to App A's burn endpoint. App A burns data and confirms. If App A re-shared with sub-processor, App A propagates burn downstream.

**Step 10: Validation**
Assertion engine checks: burned data absent from relay, present in portable record, absent from App A and sub-processor, audit log complete and hash-chain intact.

### 16.8 Simulation Success Criteria

| Criterion | Metric | Target |
|---|---|---|
| Scenario pass rate | % of scenarios (SCN-001 through SCN-020) passing all assertions | 100% |
| Burn accuracy | % of data items burned exactly when eligible (not early, not late) | 100% |
| Zero data leakage | Data items present in any store after their burn was confirmed | 0 |
| Portable record completeness | % of patient-destined data items successfully delivered and confirmed | 100% |
| Burn-propagation success | % of third-party burn signals resulting in confirmed burns | 100% (for compliant apps) |
| Real-time stream integrity | Burn-caused latency or data loss events in therapeutic stream | 0 |
| Audit log integrity | Hash chain verification passing end-to-end | 100% |
| Performance | SCN-001 (90-day) at max acceleration on standard laptop | <5 min |
| Performance | SCN-020 (50 patients, 365-day stress test) on standard laptop | <30 min |
| Reproducibility | Identical outputs for identical inputs (config + seed) | 100% |

---

## 17. Glossary

| Term | Definition |
|---|---|
| AGP | Ambulatory Glucose Profile — standardised clinical report summarising CGM data over 14+ days |
| AID | Automated Insulin Delivery — closed-loop or hybrid closed-loop system connecting CGM to pump via algorithm |
| BLE | Bluetooth Low Energy — wireless protocol used for sensor/pump-to-phone communication |
| Burn | Irreversible destruction of data from a persistence point |
| Burn propagation | Cascading destruction of data through the distribution chain upon consent revocation |
| CGM | Continuous Glucose Monitor |
| Chamber / World | A typed data domain with defined scope, access controls, and burn schedule |
| IOB | Insulin on Board — calculated amount of active insulin from recent deliveries |
| Portable record | Patient-held, patient-controlled authoritative copy of all their health data |
| TIR | Time in Range — percentage of time glucose readings fall within target range |
| Simulation clock | Virtual clock driving time-accelerated simulation; all components reference this instead of wall-clock time |
| Scenario | A declarative YAML-defined test case specifying patient profiles, event schedules, failure injections, and expected outcomes |
| Burn-propagation signal | API call from manufacturer relay to third-party app instructing it to destroy specified patient data |
| Hash chain | Append-only audit log where each entry includes a cryptographic hash of the previous entry, ensuring tamper detection |
| Typed Worlds | Architecture pattern separating data flows by purpose, access, and retention policy |

---

*This PRD is derived from the Chamber Sentinel position paper (April 2026, Revised Draft) and should be read alongside the primary Chamber Sentinel medical devices paper. All classifications are tentative and require clinical stakeholder validation.*
