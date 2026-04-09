# Chamber Sentinel — Insulin Pump & CGM
# Exhaustive Issue List

**Generated from:** chamber_sentinel_insulin_cgm_v2.docx
**Date:** 2026-04-09
**Total Issues:** 231

---

## Issue Categories

| Category | Count | Priority Range |
|---|---|---|
| A. Architecture — Typed Worlds Design | 18 | P0–P2 |
| B. Real-Time Therapeutic Stream | 15 | P0 |
| C. Burn Semantics & Scheduling | 22 | P0–P1 |
| D. Third-Party Burn Propagation | 16 | P0–P1 |
| E. Portable Record (Patient Vault) | 19 | P0–P1 |
| F. Clinical Review & Report Generation | 14 | P0–P1 |
| G. Paediatric Custodial Transitions | 15 | P1 |
| H. Consumer Wellness | 11 | P1 |
| I. Cybersecurity | 17 | P0–P1 |
| J. Regulatory & Legal Infrastructure | 12 | P1–P2 |
| K. Data Classification & Governance | 14 | P1 |
| L. Manufacturer Counterargument Accommodation | 9 | P1–P2 |
| M. Operational Preconditions & Failure Modes | 11 | P0–P1 |
| N. Validation & Stakeholder Review | 14 | P1–P2 |
| O. Local Simulation Environment | 44 | P0–P2 |

**Priority Legend:** P0 = Safety-critical / blocking. P1 = Core framework requirement. P2 = Important but deferrable.

---

## A. Architecture — Typed Worlds Design

### A-001: Define Typed Worlds boundary specifications
**Priority:** P0
**Category:** Architecture
**Description:** Formally specify the boundaries between the six Typed Worlds (Real-Time Therapeutic, Clinical Review, Device Maintenance, Research, Patient, Third-Party Distribution). Each world must have mathematically precise entry/exit conditions, data type enumerations, and access control lists. The current paper describes them narratively — an implementable architecture requires formal interface definitions.
**Acceptance Criteria:**
- Each world has a formal schema defining permitted data types
- Inter-world data transfer protocols specified
- Access control matrix defined for every world × role combination
- Boundary violations detectable and auditable

### A-002: Design inter-world data transfer protocols
**Priority:** P1
**Category:** Architecture
**Description:** Data legitimately moves between worlds (e.g., raw data in Clinical Review world is processed into reports, then raw data burns). Define the exact protocol for each permitted inter-world transfer, including: data transformation requirements, confirmation handshakes, burn triggers, and rollback procedures if transfer fails mid-stream.
**Acceptance Criteria:**
- Every permitted inter-world data flow documented with sequence diagrams
- Failed transfer recovery procedures defined
- No world receives data it is not authorized to hold

### A-003: Resolve whether framework is unified or a family of domain-specific proposals
**Priority:** P2
**Category:** Architecture
**Description:** The paper acknowledges that the adaptations required for insulin pump/CGM are substantial enough that a reader could question whether this is one framework or a family resemblance. The shared core (burden-of-justification principle, typed worlds, destruction-as-default) must be formally extracted as a reusable specification, with domain-specific modules clearly separated.
**Acceptance Criteria:**
- Core framework specification document independent of device class
- Domain-specific extension specification for insulin pump/CGM
- Clear interface between core and extension
- Test: can a third device class (e.g., implantable neurostimulator) be specified by writing only the extension?

### A-004: Define data taxonomy for insulin pump/CGM ecosystem
**Priority:** P1
**Category:** Architecture
**Description:** Create an exhaustive enumerated taxonomy of every data type generated in the ecosystem: glucose readings (raw, filtered, calibrated), insulin delivery events (basal, bolus, correction, extended), AID algorithm outputs (predicted glucose, adjustment magnitude, mode changes), device metadata (serial numbers, firmware, calibration), user-entered data (meals, activity, notes), app metadata (timestamps, GPS, device identifiers). Each data type must be classified into exactly one world.
**Acceptance Criteria:**
- Complete data type enumeration (estimated 80–120 distinct types)
- Each type mapped to one primary world
- Each type annotated with: source device, generation frequency, size, clinical utility assessment, burn schedule

### A-005: Specify burn schedule timing for each world
**Priority:** P0
**Category:** Architecture
**Description:** The paper provides qualitative burn schedules ("burns after confirmed delivery," "rolling retention," "burns on consent withdrawal"). Convert these to precise timing specifications with defined triggers, grace periods, confirmation requirements, and failure handling.
**Acceptance Criteria:**
- Each world has a numeric burn schedule (hours/days/event-triggered)
- Grace periods defined for each burn trigger
- Confirmation mechanisms specified (what constitutes "confirmed delivery"?)
- Failure modes defined (what happens if confirmation never arrives?)

### A-006: Design world isolation enforcement mechanism
**Priority:** P0
**Category:** Architecture
**Description:** Worlds must be architecturally isolated, not just logically separated. Data in the Real-Time Therapeutic world must be physically incapable of being persisted in the manufacturer cloud. This requires infrastructure-level enforcement (separate storage systems, network isolation, access control enforcement) rather than application-level policy.
**Acceptance Criteria:**
- Infrastructure isolation specification for each world
- Penetration test criteria for world boundary violations
- Audit logging for any cross-world data access
- Enforcement mechanism cannot be disabled by application code

### A-007: Handle data that legitimately belongs to multiple worlds
**Priority:** P1
**Category:** Architecture
**Description:** Some data has dual utility (e.g., AID algorithm performance data serves both clinical review and research). The paper acknowledges this as "the classification's hardest case." Define rules for data with legitimate multi-world membership: does it exist in multiple worlds simultaneously? Is the most restrictive burn schedule applied? How are access controls reconciled?
**Acceptance Criteria:**
- Policy for multi-world data defined
- Default: most restrictive burn schedule applies
- If data exists in multiple worlds, each copy burns independently per its world's schedule
- Clinical copy cannot be extended by research consent; research copy cannot substitute for clinical delivery

### A-008: Design manufacturer cloud architecture changes
**Priority:** P1
**Category:** Architecture
**Description:** Current manufacturer clouds (Dexcom Clarity, Abbott LibreView, Medtronic CareLink, Tandem Source) are monolithic data stores. Implementing typed worlds requires architectural decomposition: separate storage tiers for each world, independent access control systems, burn mechanism integration. Specify the target architecture for a reference manufacturer cloud implementation.
**Acceptance Criteria:**
- Reference architecture diagram for a Chambers-compliant manufacturer cloud
- Storage tier separation specification
- Data lifecycle management system requirements
- Migration path from current monolithic architecture

### A-009: Define audit trail requirements for burn operations
**Priority:** P1
**Category:** Architecture
**Description:** Every burn operation must be auditable without retaining the burned data itself. Design an audit trail that records: what data was burned, when, by what trigger, confirmation status, and any failures — without storing the actual data content.
**Acceptance Criteria:**
- Audit trail schema defined
- Audit records retained for regulatory compliance period
- Audit trail itself cannot be used to reconstruct burned data
- Audit trail tamper-resistant (append-only, hash-chained)

### A-010: Specify data format standards for inter-system exchange
**Priority:** P1
**Category:** Architecture
**Description:** The portable record, clinical reports, and inter-world transfers all require standardised data formats. Evaluate and specify which standards to use: FHIR for clinical data, IEEE 11073 for device data, custom schemas where no standard exists.
**Acceptance Criteria:**
- Data format standard selected for each data type category
- Mapping between internal data types and standard representations
- Versioning strategy for format evolution
- Backward compatibility requirements defined

### A-011: Design real-time vs. historical data architectural boundary
**Priority:** P0
**Category:** Architecture
**Description:** The paper identifies a critical architectural boundary between real-time therapeutic data (which must never be subject to burn) and historical data (which must burn by default). This boundary must be enforced at the infrastructure level, not the application level. A glucose reading that is "current" at time T must transition to "historical" at time T+N — define N and the transition mechanism.
**Acceptance Criteria:**
- Precise definition of when real-time data becomes historical (time threshold, event trigger, or both)
- Transition mechanism specified
- No data can remain in "real-time" classification indefinitely to avoid burn
- Transition is automatic, not dependent on manufacturer action

### A-012: Handle AID algorithm state persistence requirements
**Priority:** P0
**Category:** Architecture
**Description:** AID algorithms (Control-IQ, Omnipod 5, CamAPS FX, Tidepool Loop) maintain internal state including insulin-on-board calculations, predicted glucose trajectories, and learning parameters. This state is therapeutically critical and cannot be naively burned. Define which algorithm state elements are operational (must persist) vs. historical (must burn).
**Acceptance Criteria:**
- AID algorithm state taxonomy (estimated 15–30 distinct state variables)
- Each variable classified as operational-persistent or historical-burnable
- Algorithm restart/recovery procedures after device swap
- No algorithm state persists in manufacturer cloud unless justified

### A-013: Define data minimisation principle for each layer
**Priority:** P1
**Category:** Architecture
**Description:** At each of the six layers (sensor/pump, device→phone, phone→cloud, cloud→clinician, third-party apps, aggregated pools), define the minimum data necessary for that layer's function. Current practice transmits everything upstream; the framework requires each layer to justify what it receives.
**Acceptance Criteria:**
- Each layer has a defined minimum data set
- Data types not in the minimum set are stripped before transmission to that layer
- Justification documented for each data type in each layer's minimum set

### A-014: Specify timestamp and timezone handling across ecosystem
**Priority:** P1
**Category:** Architecture
**Description:** CGM data spans timezones (traveling patients), daylight saving transitions, and device clock drift. The portable record, burn schedules, and clinical reports all depend on accurate timestamps. Define timestamp standards, synchronisation requirements, and handling of clock discrepancies.
**Acceptance Criteria:**
- UTC as canonical time format with local timezone metadata
- Device clock synchronisation protocol
- Handling of timestamp gaps (sensor warmup, device off)
- Timezone transition handling in reports and burn schedules

### A-015: Design data deduplication strategy
**Priority:** P2
**Category:** Architecture
**Description:** The same glucose reading may exist in multiple systems simultaneously (device, phone app, manufacturer cloud, portable record, third-party apps). During transitions and burn operations, ensure deduplication does not cause data loss (premature burn of the only copy before portable record receipt) or data resurrection (burned data reappearing from a sync).
**Acceptance Criteria:**
- Deduplication rules for each data flow
- Anti-resurrection mechanism (burned data cannot reappear from delayed sync)
- At-least-once delivery guarantee to portable record before burn

### A-016: Handle offline/disconnected operation scenarios
**Priority:** P0
**Category:** Architecture
**Description:** Patients may be offline for extended periods (travel, connectivity issues). The architecture must handle: CGM data accumulating on device/phone without cloud upload, burn timers pausing or adjusting during offline periods, clinical reports queued for delivery, portable record sync resumption.
**Acceptance Criteria:**
- Offline operation mode specified for each data flow
- Burn timers do not fire during offline periods if confirmation is pending
- Data integrity maintained through offline-to-online transitions
- Maximum offline period before clinical data delivery is degraded

### A-017: Specify data compression and storage efficiency for portable record
**Priority:** P2
**Category:** Architecture
**Description:** A single patient generates ~105,000 glucose readings per year. Over a 30-year diabetes management lifetime, the portable record could contain millions of readings plus insulin delivery logs. Define storage efficiency requirements, compression strategies, and archival tiers.
**Acceptance Criteria:**
- Estimated storage requirements per year, per decade, per lifetime
- Compression strategy for historical glucose data
- Archival tier specification (hot/warm/cold)
- Portable record must remain functional on consumer-grade storage

### A-018: Define interoperability requirements between manufacturers
**Priority:** P1
**Category:** Architecture
**Description:** Patients frequently switch devices (e.g., Dexcom CGM to Abbott CGM, Tandem pump to Omnipod). The portable record must accept data from any manufacturer in a unified format, and burn obligations must persist across manufacturer boundaries.
**Acceptance Criteria:**
- Manufacturer-agnostic data ingestion specification
- Data format translation layer for each major manufacturer
- Burn obligations transfer when patient switches manufacturers
- Historical data from previous manufacturer remains in portable record

---

## B. Real-Time Therapeutic Stream

### B-001: Guarantee zero-latency isolation of real-time stream from burn mechanisms
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Real-Time
**Description:** The real-time CGM→AID→pump data stream is life-critical. Any architectural change that introduces latency, interruption, or corruption risk to this stream is unacceptable. Burn mechanisms must be architecturally firewalled — not just logically separated — from the therapeutic stream. A software bug in the burn system must be physically incapable of affecting the real-time stream.
**Acceptance Criteria:**
- Separate process/thread/container for burn mechanisms
- No shared memory or shared I/O between burn and real-time systems
- Formal verification or extensive fuzz testing of firewall
- Kill switch: burn system can be completely disabled without affecting therapy

### B-002: Define real-time data stream encryption requirements
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Real-Time
**Description:** Published research demonstrates insulin pump commands can be intercepted over unencrypted radio frequencies. Require authenticated encryption of the BLE channel for all CGM-to-phone and pump-to-phone communications. This is orthogonal to burn semantics but equally critical.
**Acceptance Criteria:**
- AES-256 or equivalent encryption on all BLE communications
- Mutual device authentication (both endpoints verified)
- Key rotation schedule
- Encryption cannot be optionally disabled

### B-003: Implement anomaly detection for implausible glucose values
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Real-Time
**Description:** An attacker who corrupts real-time CGM readings can cause the AID algorithm to deliver incorrect insulin doses. Implement anomaly detection at the AID algorithm input that flags physiologically implausible values (e.g., glucose jumping from 100 to 400 mg/dL in one minute) and triggers safe-mode operation.
**Acceptance Criteria:**
- Physiological rate-of-change limits defined (consult endocrinology literature)
- Anomalous readings flagged and excluded from AID calculations
- Safe-mode operation when anomaly detected (e.g., suspend automation, alert patient)
- False positive rate acceptable for clinical use (<0.1% of legitimate readings)

### B-004: Define real-time data retention boundary
**Priority:** P0
**Category:** Real-Time
**Description:** A glucose reading that was "real-time" 5 minutes ago is no longer needed for immediate therapy. Define the precise time window after which a real-time reading transitions to historical data subject to the Clinical Review world's burn schedule. Consider: AID algorithms use trailing windows of varying lengths (typically 15–60 minutes of glucose history for trend prediction).
**Acceptance Criteria:**
- Maximum real-time retention window defined (recommend: longest AID algorithm trailing window + safety margin)
- Transition mechanism specified (time-based, automatic)
- No manual override to extend real-time classification
- AID algorithm requirements from all major systems surveyed (Control-IQ, Omnipod 5, CamAPS FX, Loop)

### B-005: Handle sensor warmup periods in real-time stream
**Priority:** P0
**Category:** Real-Time
**Description:** New CGM sensors require a warmup period (30 minutes to 24 hours depending on model) during which readings are unreliable. Define how the architecture handles this: are warmup readings treated as real-time data? Are they flagged? Does the AID algorithm receive them?
**Acceptance Criteria:**
- Warmup period metadata attached to readings
- AID algorithm either excludes warmup readings or applies reduced confidence
- Warmup readings do not contribute to clinical reports
- User alerted during warmup period about reduced reliability

### B-006: Specify CGM-to-AID data integrity verification
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Real-Time
**Description:** The integrity of glucose readings flowing from CGM to AID algorithm must be verified at every hop. If a reading is corrupted in transit (BLE interference, software bug, attack), the AID algorithm must detect the corruption before acting on it.
**Acceptance Criteria:**
- Cryptographic integrity check on every glucose reading
- AID algorithm verifies integrity before processing
- Corrupted readings discarded with alert to patient
- Integrity verification adds <1ms latency to data path

### B-007: Handle multiple simultaneous CGM sources
**Priority:** P1
**Category:** Real-Time
**Description:** Some patients wear two CGMs simultaneously (e.g., during sensor transitions, or as a redundancy practice). The architecture must handle multiple real-time glucose streams without confusion about which is authoritative for AID dosing.
**Acceptance Criteria:**
- Primary/secondary CGM designation
- Conflict resolution when readings diverge
- Seamless handoff during sensor transitions
- Both streams subject to same security and integrity requirements

### B-008: Define fallback behaviour when real-time stream is interrupted
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Real-Time
**Description:** BLE connections drop. Phones run out of battery. Sensors malfunction. Define the exact behavior of every component in the system when the real-time data stream is interrupted for varying durations (seconds, minutes, hours).
**Acceptance Criteria:**
- AID algorithm behavior specified for interruptions of: <5 min, 5–30 min, 30–60 min, >60 min
- Patient notification escalation schedule
- Graceful degradation path (closed-loop → open-loop → manual)
- Reconnection and state recovery protocol

### B-009: Ensure real-time stream does not leak to manufacturer cloud
**Priority:** P0
**Category:** Real-Time
**Description:** The framework states real-time therapeutic data "never persists in manufacturer cloud." However, current architectures upload glucose readings to the manufacturer cloud in near-real-time (e.g., Dexcom Share). This upload must be decoupled from the therapeutic stream — it is a Layer 3 function, not a Layer 2 function.
**Acceptance Criteria:**
- Therapeutic stream terminates at AID algorithm/patient app — does not continue to cloud
- Cloud upload is a separate, independent data flow from phone to manufacturer
- Disabling cloud upload has zero impact on therapeutic operation
- Therapeutic stream has no dependency on internet connectivity

### B-010: Handle insulin-on-board (IOB) calculation across device boundaries
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Real-Time
**Description:** IOB calculations are critical for safe insulin dosing. IOB state persists across boluses and must survive device disconnections, app restarts, and phone reboots. Define where IOB state is persisted, how it is protected, and what happens when state is lost.
**Acceptance Criteria:**
- IOB state persisted on both pump and phone (redundancy)
- State synchronisation protocol between pump and phone
- Recovery procedure when IOB state is lost (conservative: assume maximum IOB)
- IOB state classified as operational (never burns) until insulin action window expires (typically 4–6 hours)

### B-011: Specify maximum acceptable latency for each real-time data hop
**Priority:** P0
**Category:** Real-Time
**Description:** Define maximum acceptable latency for: sensor→transmitter, transmitter→phone, phone→AID algorithm, AID algorithm→pump. Each hop adds latency that can make glucose readings clinically stale.
**Acceptance Criteria:**
- Latency budget for each hop defined (recommend: total <5 minutes sensor-to-pump)
- Latency monitoring and alerting
- Readings exceeding age threshold flagged as stale
- AID algorithm adjusts confidence based on reading age

### B-012: Address Bluetooth signal interference in medical environments
**Priority:** P1
**Category:** Real-Time
**Description:** Hospital environments have dense RF environments that can interfere with BLE. Patients in hospital, during surgery, or in imaging suites may experience degraded BLE connectivity affecting their therapeutic stream.
**Acceptance Criteria:**
- Known interference scenarios documented
- Graceful degradation in high-interference environments
- Hospital/clinical staff awareness protocols
- Wired or alternative connectivity backup (if feasible)

### B-013: Handle daylight saving time and timezone transitions in real-time stream
**Priority:** P1
**Category:** Real-Time
**Description:** A patient crossing timezones or experiencing DST transition must not have their AID algorithm confused by timestamp discontinuities. The real-time stream must handle clock changes without treating them as data anomalies.
**Acceptance Criteria:**
- Real-time stream uses monotonic timestamps, not wall-clock time
- Timezone changes do not trigger anomaly detection
- AID algorithm behavior unaffected by clock adjustments
- Clinical reports correctly reflect local time for readability

### B-014: Specify real-time stream behaviour during firmware updates
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Real-Time
**Description:** Pump and CGM firmware updates require device restarts. Define the exact therapeutic protocol during firmware updates: when is it safe to update? How long is the therapeutic gap? What patient warnings are required?
**Acceptance Criteria:**
- Firmware update window constrained (e.g., only when glucose is in range and stable)
- Patient must confirm before update proceeds
- Maximum therapeutic gap from update defined and acceptable
- IOB state preserved across firmware update restart

### B-015: Define real-time data for connected insulin pens (non-pump)
**Priority:** P1
**Category:** Real-Time
**Description:** Connected insulin pens (NovoPen 6, Lilly Tempo) log injection doses but do not have a continuous real-time stream like pumps. Define what "real-time" means for pen users: is a dose log entry "real-time" at the moment of injection? How does this integrate with CGM data in the therapeutic stream?
**Acceptance Criteria:**
- Pen dose events classified (real-time at injection, historical after IOB window)
- Integration with CGM data for dosing decision support
- Pen dose data subject to same burn schedules as pump data after IOB window

---

## C. Burn Semantics & Scheduling

### C-001: Define "burn" as a technical operation
**Priority:** P0
**Category:** Burn
**Description:** "Burn" must be precisely defined as a technical operation. Is it: cryptographic erasure (key destruction), physical overwrite, logical deletion with scheduled overwrite, or something else? Different mechanisms have different security guarantees, performance characteristics, and verification properties.
**Acceptance Criteria:**
- Burn mechanism specified for each storage tier (SSD, HDD, cloud object storage, database)
- Cryptographic erasure preferred where hardware supports it
- Verification mechanism to confirm burn completed
- Burned data irrecoverable even with physical media access

### C-002: Specify burn confirmation protocol
**Priority:** P0
**Category:** Burn
**Description:** The paper repeatedly references burning "after confirmed delivery" to the portable record. Define what constitutes confirmed delivery: is it an acknowledgement from the portable record system? A hash verification? A timeout-based presumption? What happens if confirmation never arrives?
**Acceptance Criteria:**
- Confirmation is a cryptographic acknowledgement from portable record
- Timeout threshold defined (after which data is NOT burned but escalated)
- Retry mechanism for failed deliveries
- Manual override process for stuck deliveries

### C-003: Design burn scheduling engine
**Priority:** P1
**Category:** Burn
**Description:** Build a scheduling engine that tracks every data item, its world classification, its burn trigger, and its current lifecycle state. The engine must handle: time-based burns (e.g., 90 days), event-triggered burns (e.g., confirmed delivery), consent-revocation burns (immediate), and patient-initiated burns.
**Acceptance Criteria:**
- Scheduler handles millions of individual data item burn schedules
- Burn events executed within defined SLA (<1 hour of trigger for time-based, <24 hours for event-based)
- Scheduler resilient to crashes (no burn events lost)
- Dashboard showing pending/completed/failed burns

### C-004: Handle burn failures and retries
**Priority:** P0
**Category:** Burn
**Description:** Burn operations can fail (storage unavailable, concurrent access, system crash). Define retry policy, maximum retry duration, escalation path, and the system state during failed burns (is data accessible while burn is pending?).
**Acceptance Criteria:**
- Retry policy: exponential backoff, max 3 retries, then escalate
- During pending burn: data access restricted to burn system only
- Escalation: alert to data governance team after max retries
- Failed burns tracked in audit trail

### C-005: Prevent burn circumvention through backup/restore
**Priority:** P0
**Category:** Burn
**Description:** If manufacturer cloud data is backed up before a burn and restored after, the burn is nullified. Backup systems must either: not include burned data, or themselves implement burn propagation.
**Acceptance Criteria:**
- Backup systems respect burn markers
- Restored data re-checks burn status and re-burns if necessary
- Point-in-time recovery does not resurrect burned data
- Backup retention schedules aligned with burn schedules

### C-006: Define burn semantics for derived data
**Priority:** P1
**Category:** Burn
**Description:** If raw glucose data is burned but a machine learning model was trained on that data, the model retains "learned" information from the burned data. Define whether derived artifacts (trained models, aggregate statistics, de-identified datasets) must also be burned, and under what conditions.
**Acceptance Criteria:**
- Models trained on data: model itself does not burn (impractical), but training provenance recorded
- Aggregate statistics: do not burn (cannot be reversed to individual data)
- De-identified datasets: burn if re-identification risk exists
- Clear policy for each class of derived data

### C-007: Specify burn semantics for data in transit
**Priority:** P1
**Category:** Burn
**Description:** Data in transit (e.g., being uploaded from phone to cloud, being delivered to clinician) may still be "in flight" when a burn trigger fires. Define the interaction: does the burn wait for in-flight data to land? Does it cancel in-flight transmissions?
**Acceptance Criteria:**
- In-flight data: burn waits for transmission to complete, then burns at source
- If destination is the portable record: burn at source after delivery confirmation
- If destination is third-party: burn at source; burn-propagation signal sent to third party
- Cancelled transmissions: data burns at source immediately

### C-008: Handle burn of encrypted data
**Priority:** P1
**Category:** Burn
**Description:** If data is encrypted at rest, the most efficient burn mechanism is key destruction (cryptographic erasure). Define key management requirements that enable per-item or per-world key destruction without affecting other data.
**Acceptance Criteria:**
- Per-world or per-patient encryption key hierarchy
- Key destruction verified and auditable
- Key management system separate from data storage system
- Key backup/escrow compatible with burn requirements (no key recovery after intentional destruction)

### C-009: Define patient-initiated burn interface
**Priority:** P1
**Category:** Burn
**Description:** Patients must be able to initiate burns of their data at any time. Design the user interface and workflow: what data can they burn? What warnings are shown? Is there a grace period? Can a burn be reversed within the grace period?
**Acceptance Criteria:**
- Patient can view all data held about them by manufacturer
- Patient can select specific data types, time ranges, or all data for burn
- Clear warning: "This action is irreversible. Data cannot be recovered."
- Short grace period (e.g., 24 hours) before irreversible execution
- After grace period: burn is immediate and complete

### C-010: Specify burn semantics for audit trails themselves
**Priority:** P2
**Category:** Burn
**Description:** Audit trails recording burn operations must themselves be retained for a regulatory compliance period — but they must not contain burned data. Define the retention period for audit trails and their own eventual burn schedule.
**Acceptance Criteria:**
- Audit trail retention: regulatory compliance period (e.g., 7 years)
- Audit trail contains metadata only (data type, timestamp, trigger, result) — never content
- Audit trails burn after retention period
- Audit trail burn is itself audited (meta-audit)

### C-011: Define burn schedule for device maintenance data
**Priority:** P1
**Category:** Burn
**Description:** Device maintenance data (serial numbers, firmware versions, calibration) burns on device replacement cycle. But patients may keep a pump for 4 years and replace CGM sensors every 7–14 days. Define separate burn schedules for pump maintenance data vs. CGM sensor maintenance data.
**Acceptance Criteria:**
- Pump maintenance data: burns on pump replacement (typically 4 years)
- CGM sensor data: burns on sensor replacement (7–365 days depending on model)
- Warranty claims extend maintenance data retention until claim resolved
- Recall data retained until recall resolved, then burns

### C-012: Handle burn scheduling across multiple timezones
**Priority:** P2
**Category:** Burn
**Description:** A patient traveling across timezones may have data in manufacturer clouds in multiple jurisdictions with different regulatory requirements. Burn schedules must be calculated in a consistent timezone (UTC) but displayed to the patient in local time.
**Acceptance Criteria:**
- Burn schedules calculated in UTC
- Patient-facing displays show local time
- Jurisdictional variations (e.g., EU GDPR vs. US regulations) handled through policy configuration
- Burn does not fire prematurely or late due to timezone ambiguity

### C-013: Define burn semantics for shared/family data
**Priority:** P1
**Category:** Burn
**Description:** Some data is shared between patients and caregivers (e.g., parent viewing child's glucose data via Dexcom Follow). If the patient burns their data, what happens to the caregiver's copy? The shared view should burn, but the caregiver's own interaction logs may be separate.
**Acceptance Criteria:**
- Patient burn triggers burn of all shared views
- Caregiver's own notes/interactions about the patient: governed by caregiver's consent, but flagged for review
- Burn propagates to all "follow" accounts
- Caregiver notified when shared data is burned

### C-014: Specify burn semantics for data exported by patient
**Priority:** P2
**Category:** Burn
**Description:** If a patient downloads their data to a local file (CSV, PDF export), that local copy is outside the framework's control. Define whether the framework addresses patient-held exports (likely: no, patient controls their own data) and how the system handles re-import of previously burned data.
**Acceptance Criteria:**
- Patient-held exports: outside framework scope; patient controls
- Re-import of previously burned data: system accepts but does not retroactively apply burn
- Framework explicitly states: "Patient's own copies are patient's responsibility"
- Manufacturer cannot import patient exports to circumvent burn

### C-015: Define emergency burn ("panic button") for compromised accounts
**Priority:** P0
**Category:** Burn
**Description:** If a patient's manufacturer account is compromised (credential theft, social engineering), they need an emergency burn that immediately destroys all data across all worlds and all third-party recipients. This must be faster than standard burn schedules.
**Acceptance Criteria:**
- Emergency burn destroys all data within 1 hour
- Trigger: patient request via verified identity channel (in-person, phone with identity verification)
- Burn propagation to all third parties initiated simultaneously
- Real-time therapeutic stream unaffected (operates independently of cloud)
- Account recovery process does not restore burned data

### C-016: Handle burn in disaster recovery scenarios
**Priority:** P1
**Category:** Burn
**Description:** If a manufacturer's primary datacenter fails and operations switch to a disaster recovery (DR) site, the DR site may contain data that should have been burned. Define DR synchronisation requirements for burn state.
**Acceptance Criteria:**
- Burn state replicated to DR site in near-real-time
- DR failover does not resurrect burned data
- DR site applies pending burns within same SLAs as primary
- DR testing includes burn state verification

### C-017: Specify burn semantics for data in search indices and caches
**Priority:** P1
**Category:** Burn
**Description:** Manufacturer systems may index patient data in search engines (Elasticsearch, Solr), cache it in CDNs or application caches (Redis, Memcached), or materialise it in analytics views. Burn must reach all of these secondary storage locations.
**Acceptance Criteria:**
- Data inventory of all secondary storage locations (indices, caches, materialised views)
- Burn propagates to all secondary locations
- Cache invalidation triggered by burn
- Search indices purged of burned data
- Analytics views recomputed without burned data

### C-018: Define burn verification and audit reporting
**Priority:** P1
**Category:** Burn
**Description:** Regulators, patients, and auditors need to verify that burns occurred. Define a burn verification report: what it contains, who can request it, and how it proves burn without revealing burned data.
**Acceptance Criteria:**
- Burn verification report: timestamp, data scope, trigger, completion status, verification hash
- Patient can request verification report for their data
- Regulator can request aggregate burn compliance statistics
- Verification uses cryptographic proof (e.g., Merkle proof of absence)

### C-019: Define burn semantics for metadata and logs
**Priority:** P1
**Category:** Burn
**Description:** Even after data content is burned, metadata may persist: access logs showing who viewed the data, API call logs showing when data was shared, analytics events showing data was processed. Define whether metadata burns with content or has an independent schedule.
**Acceptance Criteria:**
- Metadata associated with burned content: burns on same schedule or shorter
- Access logs: retain for security audit period, then burn
- API call logs: retain caller/timestamp, strip data content references
- No metadata combination can be used to reconstruct burned data

### C-020: Handle legal hold / litigation preservation and burn conflicts
**Priority:** P1
**Category:** Burn
**Description:** If a patient or manufacturer is involved in litigation, legal hold requirements may conflict with burn schedules. Define the interaction: does legal hold override burn? How is the conflict resolved? What happens after the hold is lifted?
**Acceptance Criteria:**
- Legal hold suspends burn for affected data
- Hold scope narrowly defined (only data relevant to the matter)
- Hold duration tracked; burn resumes when hold lifted
- Patient notified when their data is under legal hold (if legally permissible)
- Legal hold does not become a mechanism for indefinite retention

### C-021: Define burn semantics for aggregated/anonymised population data
**Priority:** P2
**Category:** Burn
**Description:** Layer 6 (Aggregated Pools) contains "de-identified aggregate statistics, RWE datasets." If individual contributions to these aggregates are burned, the aggregate itself changes. Define whether aggregates are recomputed after individual burns or frozen at computation time.
**Acceptance Criteria:**
- Aggregates frozen at computation time (not retroactively modified by individual burns)
- Aggregate must be genuinely aggregated (k-anonymity threshold: k≥50)
- Aggregates flagged with computation date; consumers know data reflects a point in time
- Individual patients cannot be re-identified from aggregate (verified by privacy review)

### C-022: Specify burn semantics for data shared with insurers or employers
**Priority:** P0
**Category:** Burn
**Description:** If glucose data has been shared (through any pathway) with insurers or employers, burn propagation must reach those recipients. This is legally and practically the most contentious burn-propagation scenario. Define the mechanism even if enforcement is uncertain.
**Acceptance Criteria:**
- Burn-propagation signal sent to all known downstream recipients including insurers/employers
- Contractual obligation for insurers/employers to burn upon signal
- Audit trail recording signal sent and response received
- Acknowledged limitation: practical verification may be impossible

---

## D. Third-Party Burn Propagation

### D-001: Design burn-propagation API protocol
**Priority:** P0
**Category:** Third-Party
**Description:** The paper identifies this as "the framework's most technically and legally challenging element." Design an API protocol that manufacturer platforms expose to propagate burn signals to all third-party apps that received patient data. This protocol is technically novel — no reference implementation exists.
**Acceptance Criteria:**
- RESTful or webhook-based burn-propagation API specification
- Signal includes: patient identifier, data scope, burn deadline, verification requirement
- Third-party must acknowledge receipt and confirm completion
- Protocol handles: unreachable third parties, defunct apps, apps that refuse to comply
- Versioned protocol with backward compatibility

### D-002: Define third-party compliance requirements for API access
**Priority:** P1
**Category:** Third-Party
**Description:** Third-party apps accessing manufacturer APIs (e.g., Dexcom API) must agree to burn-propagation requirements as a condition of API access. Define the contractual, technical, and audit requirements.
**Acceptance Criteria:**
- API access agreement includes burn-propagation obligation
- Third-party must implement burn endpoint meeting protocol specification
- Annual compliance audit (self-report + spot check)
- Non-compliant apps lose API access
- Transition period for existing 90+ Dexcom partner apps

### D-003: Handle defunct or unreachable third-party apps
**Priority:** P1
**Category:** Third-Party
**Description:** A patient authorised an app 3 years ago; the app company has since shut down. Burn-propagation signal has no recipient. Define the system behavior: is the data considered "burned" by abandonment? Is it flagged as unverifiable? What is the patient told?
**Acceptance Criteria:**
- Defunct app registry maintained by manufacturer
- Patient notified that data shared with defunct app cannot be verified as burned
- Audit trail records undeliverable burn signals
- Risk disclosed to patient at time of initial authorisation ("if this app ceases to exist, we cannot guarantee burn")

### D-004: Prevent re-sharing by third-party apps
**Priority:** P1
**Category:** Third-Party
**Description:** Third-party apps may re-share data with fourth parties (sub-processors, analytics providers, ad networks). Burn propagation must cascade through the entire chain. Define how the manufacturer tracks and enforces downstream re-sharing.
**Acceptance Criteria:**
- Third-party apps must disclose all downstream data recipients in API agreement
- Re-sharing obligates the third party to propagate burn to their recipients
- Chain of custody tracked (manufacturer → app → sub-processor → ...)
- Maximum re-sharing depth defined (recommend: 2 hops)
- Patient can view the complete sharing chain for their data

### D-005: Define burn-propagation SLA (time to burn)
**Priority:** P1
**Category:** Third-Party
**Description:** How quickly must a third-party app burn data after receiving a burn-propagation signal? Define the SLA and consequences for non-compliance.
**Acceptance Criteria:**
- Standard burn: 72 hours from signal receipt
- Emergency burn: 24 hours from signal receipt
- Compliance verification: third party sends burn confirmation with cryptographic proof
- Non-compliance escalation: warning → API rate limiting → API revocation

### D-006: Handle partial data burns in third-party apps
**Priority:** P1
**Category:** Third-Party
**Description:** A patient may revoke consent for a specific data type (e.g., meal logs) but not others (e.g., glucose readings). Burn-propagation signals must support granular, per-data-type burns.
**Acceptance Criteria:**
- Burn signal includes data type scope (not just "burn everything")
- Third-party apps can burn specific data types while retaining others
- Data type taxonomy consistent between manufacturer and third parties
- Verification confirms correct scope of burn

### D-007: Design third-party data inventory for patient visibility
**Priority:** P1
**Category:** Third-Party
**Description:** Patients must be able to see which third-party apps hold their data, what data types, and since when. The manufacturer must maintain this inventory as a condition of providing API access.
**Acceptance Criteria:**
- Patient-facing dashboard showing all third-party apps with access
- For each app: data types shared, date range, sharing status (active/revoked)
- Patient can revoke access per app from this dashboard
- Inventory updated in real-time as sharing changes

### D-008: Handle third-party apps operating in jurisdictions with conflicting data laws
**Priority:** P2
**Category:** Third-Party
**Description:** A third-party app may operate in a jurisdiction where data retention is legally required (e.g., financial records retention), creating a conflict with burn-propagation requirements. Define conflict resolution.
**Acceptance Criteria:**
- Jurisdictional conflict identified at API access agreement time
- Patient informed if data shared with an app in a conflicting jurisdiction
- Minimum retention overrides burn-propagation during mandatory retention period
- After mandatory period: burn-propagation resumes

### D-009: Specify burn-propagation for real-time data sharing (e.g., Dexcom Follow/Share)
**Priority:** P1
**Category:** Third-Party
**Description:** Some third-party integrations receive real-time glucose data (e.g., caregiver following patient's glucose via Dexcom Follow). If consent is revoked, should historical data on the follower's device also burn? Define burn scope for real-time sharing features.
**Acceptance Criteria:**
- Consent revocation immediately terminates real-time sharing
- Historical data on follower's device: burn signal sent to follower's app
- Follower's locally cached data: burn on next app sync
- Follower notified that access has been revoked

### D-010: Design third-party app certification programme
**Priority:** P2
**Category:** Third-Party
**Description:** A formal certification programme for third-party apps demonstrating burn-propagation compliance. Analogous to SOC 2 or HITRUST certification for data governance.
**Acceptance Criteria:**
- Certification criteria defined
- Testing methodology (simulated burn signals, verification)
- Certification validity period (annual renewal)
- Public registry of certified apps
- Patient-facing badge/indicator for certified apps

### D-011: Handle consumer wellness apps differently from clinical apps
**Priority:** P1
**Category:** Third-Party
**Description:** A fitness app receiving glucose data for wellness tracking has a different risk profile than a clinical decision support app. Define whether burn-propagation requirements differ by app category.
**Acceptance Criteria:**
- App classification system (clinical, wellness, research, commercial)
- Burn-propagation requirements apply equally regardless of classification (no weaker requirement for wellness apps)
- Data minimisation requirements may differ by classification
- Consumer wellness apps cannot reclassify to avoid burn requirements

### D-012: Define manufacturer liability for third-party burn failures
**Priority:** P1
**Category:** Third-Party
**Description:** The paper quotes Dexcom disclaiming "no further control or responsibility" for data shared via API. The framework rejects this disclaimer. Define the liability model: is the manufacturer responsible for third-party burn failures? Jointly? Wholly?
**Acceptance Criteria:**
- Manufacturer retains residual responsibility for data they distributed via API
- Manufacturer must demonstrate reasonable efforts to enforce burn propagation
- Joint liability model for burn failures
- Manufacturer cannot use API terms to disclaim all responsibility

### D-013: Handle data aggregators (Tidepool, Glooko) as special-case third parties
**Priority:** P1
**Category:** Third-Party
**Description:** Aggregators like Tidepool and Glooko receive data from multiple manufacturers and devices. They act as secondary hubs with their own downstream sharing. Burn-propagation must treat them as intermediate nodes, not terminal recipients.
**Acceptance Criteria:**
- Aggregators classified as intermediate nodes in burn-propagation chain
- Aggregators must propagate burn signals to their downstream recipients
- Aggregators must implement burn for data from all contributing manufacturers
- Patient's portable record may duplicate aggregator's function, reducing dependency

### D-014: Specify burn-propagation for data already published in research
**Priority:** P2
**Category:** Third-Party
**Description:** If patient data has been included in a published research paper (even if de-identified), the publication cannot be "burned." Define the interaction between burn-propagation and published research.
**Acceptance Criteria:**
- Published research data: outside burn scope (impractical to retract publications)
- Data contributing to published research must have been in Research World with consent
- Patient informed at consent time: "data used in published research cannot be recalled"
- Raw data underlying published research: burns per research channel schedule; published output remains

### D-015: Design burn-propagation monitoring and alerting
**Priority:** P1
**Category:** Third-Party
**Description:** The manufacturer must monitor the burn-propagation chain for failures, delays, and non-compliance. Design a monitoring system that tracks every burn signal through the chain.
**Acceptance Criteria:**
- Dashboard showing burn-propagation status per patient, per third party
- Alert on: unacknowledged signals (>24h), failed burns, non-compliant apps
- Regular compliance reports for regulatory submission
- Patient can check status of their burn-propagation requests

### D-016: Handle API versioning and backward compatibility for burn-propagation
**Priority:** P2
**Category:** Third-Party
**Description:** The burn-propagation API will evolve. Define versioning strategy ensuring that older third-party integrations still receive and respond to burn signals.
**Acceptance Criteria:**
- Semantic versioning for burn-propagation API
- Minimum supported version policy (e.g., support last 2 major versions)
- Deprecation notice period (12 months minimum)
- Old-version apps receive burn signals in their supported format

---

## E. Portable Record (Patient Vault)

### E-001: Define portable record architecture
**Priority:** P0
**Category:** Portable Record
**Description:** The portable record is the patient's authoritative data store. Define its architecture: is it a local application (phone/computer), a patient-controlled cloud, a hardware device, or a hybrid? It must be: patient-controlled, portable, interoperable, and capable of holding a lifetime of CGM/pump data.
**Acceptance Criteria:**
- Architecture decision with trade-off analysis
- Minimum storage capacity: 30 years of CGM + pump + AID data
- Encryption at rest with patient-held keys
- No vendor lock-in (open standards for data format and access)

### E-002: Specify portable record data format
**Priority:** P1
**Category:** Portable Record
**Description:** Define the data format for the portable record. Evaluate: FHIR (healthcare interoperability), Tidepool's open data model, IEEE 11073 (medical device communication), custom format. Must support all data types from the taxonomy (Issue A-004).
**Acceptance Criteria:**
- Primary format selected with rationale
- Import/export capabilities for manufacturer-specific formats
- Schema versioning for format evolution
- Human-readable export option (CSV, PDF)

### E-003: Design portable record access control system
**Priority:** P1
**Category:** Portable Record
**Description:** The portable record supports multiple access levels: patient (full), delegated clinician (read-only, time-scoped), caregiver (configurable), researcher (consent-gated). Design the access control system.
**Acceptance Criteria:**
- Role-based access control (RBAC) with fine-grained permissions
- Time-scoped access (clinician sees only data relevant to their care period)
- Access revocation is immediate
- Audit log of all access events
- Emergency access protocol (patient incapacitated)

### E-004: Handle portable record loss or destruction
**Priority:** P0
**Category:** Portable Record
**Description:** If the patient's portable record is lost (phone broken, hard drive failure, cloud provider shutdown), the data is gone — the manufacturer has already burned their copy. Define backup and recovery strategy that is consistent with patient sovereignty.
**Acceptance Criteria:**
- Backup mechanism under patient control (not manufacturer-controlled)
- Backup encrypted with patient-held keys
- Backup can be stored in any cloud provider or local media
- Recovery procedure tested and documented
- Clear patient education: "If you lose your portable record and have no backup, data cannot be recovered from the manufacturer"

### E-005: Design portable record data ingestion from multiple manufacturers
**Priority:** P1
**Category:** Portable Record
**Description:** A patient using a Dexcom CGM with a Tandem pump and an Abbott Libre as a backup sensor needs their portable record to ingest data from three different manufacturers in three different formats. Design the multi-manufacturer ingestion system.
**Acceptance Criteria:**
- Manufacturer-specific data adapters/plugins
- Data normalisation to common internal format
- Conflict resolution for overlapping data (two CGMs, same time period)
- Data provenance tracking (which manufacturer provided which data)

### E-006: Specify portable record delivery confirmation protocol
**Priority:** P0
**Category:** Portable Record
**Description:** Burn triggers depend on "confirmed delivery to patient's portable record." Define the technical protocol for delivery confirmation: how does the manufacturer know the portable record received and stored the data?
**Acceptance Criteria:**
- Cryptographic acknowledgement from portable record to manufacturer
- Acknowledgement includes hash of received data for integrity verification
- Acknowledgement signed by patient's key (proves delivery to correct patient)
- Manufacturer cannot burn until valid acknowledgement received

### E-007: Handle patients who decline the portable record
**Priority:** P1
**Category:** Portable Record
**Description:** Some patients will not want to manage a portable record. The framework states patients can elect manufacturer persistence. Define the experience for patients who opt out of the portable record entirely: does the manufacturer then retain indefinitely? With what governance?
**Acceptance Criteria:**
- Patient-elected persistence replaces portable record for opt-out patients
- Elected persistence requires explicit opt-in with clear terms
- Manufacturer retention under elected persistence has defined governance (purpose limitation, access controls)
- Patient can switch from elected persistence to portable record at any time, receiving a data export

### E-008: Design portable record for low-tech patients
**Priority:** P1
**Category:** Portable Record
**Description:** Elderly patients, low-income patients, and patients with limited technical literacy may struggle with managing a portable record. Define accessibility requirements and alternative implementations (e.g., clinician-managed on patient's behalf, simplified interface, physical media).
**Acceptance Criteria:**
- Simplified interface option (minimal technical interaction required)
- Clinician-delegated management option (clinician manages on patient's behalf with patient consent)
- Physical backup option (USB drive, printed QR code for key)
- Multi-language support
- Accessibility compliance (WCAG 2.1 AA minimum)

### E-009: Specify portable record sharing with new clinicians
**Priority:** P1
**Category:** Portable Record
**Description:** When a patient changes endocrinologists, they need to share their portable record with the new clinician. Define the sharing workflow: how is access granted? What data is shared? How is access revoked from the previous clinician?
**Acceptance Criteria:**
- Patient initiates sharing (not clinician-initiated)
- Sharing options: full history, specific date range, specific data types
- Previous clinician access revoked on patient request
- Shared data delivered to clinician's EMR in interoperable format
- Sharing audit trail

### E-010: Handle portable record data integrity over decades
**Priority:** P1
**Category:** Portable Record
**Description:** A portable record holding 30 years of data must remain readable and intact through: format changes, storage technology changes, key rotations, and application updates. Define long-term integrity requirements.
**Acceptance Criteria:**
- Data integrity verification (checksums, hash chains)
- Format migration strategy (old data converted to new format as needed)
- Key rotation without data re-encryption of entire archive
- Data readable by any compliant application, not just the original

### E-011: Define portable record regulatory classification
**Priority:** P2
**Category:** Portable Record
**Description:** Is the portable record software a medical device (subject to FDA/CE clearance)? A personal health record (less regulated)? A data storage tool (unregulated)? The classification affects development constraints, liability, and adoption timeline.
**Acceptance Criteria:**
- Regulatory counsel opinion on classification
- If SaMD (Software as a Medical Device): define regulatory submission strategy
- If PHR: define applicable regulations
- Classification may vary by jurisdiction

### E-012: Design portable record migration between platforms
**Priority:** P1
**Category:** Portable Record
**Description:** If a patient's portable record is currently in Platform A and they want to move to Platform B, the entire data set must be exportable and importable without loss. Define the migration protocol.
**Acceptance Criteria:**
- Full data export in open, documented format
- Full data import with integrity verification
- Migration does not trigger re-burn of manufacturer data (data already in patient custody)
- Dual-platform operation during transition period

### E-013: Specify portable record emergency access
**Priority:** P0
**Category:** Portable Record
**Description:** If a patient is incapacitated (emergency, coma), emergency medical personnel need access to their recent glucose and insulin data. Define an emergency access mechanism that doesn't compromise normal access controls.
**Acceptance Criteria:**
- Emergency access provides recent data (last 14 days) without full authentication
- Emergency access is read-only
- Emergency access is logged and auditable
- Emergency access does not expose decades of historical data
- Mechanism (e.g., medical ID card, phone emergency mode, QR bracelet)

### E-014: Handle portable record for patients with multiple conditions
**Priority:** P2
**Category:** Portable Record
**Description:** A patient may use multiple connected medical devices (CGM, pump, pacemaker, continuous blood pressure monitor). The portable record should ideally hold all medical device data, not just diabetes data. Define extensibility.
**Acceptance Criteria:**
- Portable record architecture supports arbitrary medical device data types
- Device-specific modules/plugins for data ingestion
- Cross-device data correlation capabilities (e.g., glucose + cardiac)
- Unified access control across all device data

### E-015: Specify portable record performance requirements
**Priority:** P1
**Category:** Portable Record
**Description:** Clinical review requires loading a 90-day AGP report quickly. Patient browsing requires navigating through years of data. Define performance requirements.
**Acceptance Criteria:**
- AGP report generation from raw data: <5 seconds
- Data browsing/navigation: <1 second per view
- Search across full history: <10 seconds
- Data import from manufacturer: <30 seconds for 90 days of data

### E-016: Design portable record sync between patient's devices
**Priority:** P1
**Category:** Portable Record
**Description:** A patient may access their portable record from their phone, tablet, and computer. Define synchronisation requirements to keep all copies consistent.
**Acceptance Criteria:**
- End-to-end encrypted sync
- Conflict resolution for simultaneous edits (rare but possible)
- Sync status indicator
- Offline operation with deferred sync

### E-017: Handle portable record cost and sustainability
**Priority:** P1
**Category:** Portable Record
**Description:** Who pays for the portable record infrastructure? If it requires cloud storage, compute for report generation, and ongoing development, the cost model must be sustainable without creating a new data intermediary dependency.
**Acceptance Criteria:**
- Cost model analysis (patient-paid, manufacturer-subsidised, government-funded, open-source community)
- No single commercial entity controls the portable record ecosystem
- Patient cost must not be a barrier to adoption
- Open-source reference implementation available

### E-018: Specify portable record identity and authentication
**Priority:** P0
**Category:** Portable Record
**Description:** The portable record must authenticate the patient's identity to ensure data sovereignty. Design the identity system: what prevents someone from claiming another person's portable record? How does the patient prove ownership?
**Acceptance Criteria:**
- Strong identity verification at setup (government ID, biometric, clinician attestation)
- Multi-factor authentication for ongoing access
- Key recovery mechanism (loss of phone/password doesn't mean loss of record)
- No centralised identity provider dependency

### E-019: Define portable record data deletion (patient burns their own data)
**Priority:** P1
**Category:** Portable Record
**Description:** The patient should be able to selectively or completely burn data from their own portable record. Define the interface and irreversibility guarantees.
**Acceptance Criteria:**
- Patient can select any data for deletion
- Deletion is cryptographically irreversible (key destruction)
- Warning: "This data exists nowhere else. Deletion is permanent."
- Deletion granularity: by data type, by date range, by source device, or all

---

## F. Clinical Review & Report Generation

### F-001: Validate AGP report sufficiency across clinical contexts
**Priority:** P0
**Category:** Clinical
**Description:** The framework assumes processed reports (AGP, TIR summaries) serve all clinical needs. This assumption must be validated with endocrinologists specialising in: adult T1D, adult T2D, paediatric T1D, pregnancy/gestational diabetes, elderly patients, and complex comorbidity patients.
**Acceptance Criteria:**
- Endocrinologist survey (n≥50) across subspecialties
- Identify any clinical scenario where raw data is needed and processed reports are insufficient
- If such scenarios exist, define narrow exceptions to raw data burn
- Document validated sufficiency with clinical evidence

### F-002: Define standard clinical report formats
**Priority:** P1
**Category:** Clinical
**Description:** Define the set of standard clinical reports the manufacturer relay generates before burning raw data: AGP (14-day and 90-day), time-in-range distribution, glucose variability metrics, insulin delivery summary, AID performance summary, significant event log.
**Acceptance Criteria:**
- Report catalogue with specifications for each report type
- Report formats aligned with international consensus guidelines
- Reports include sufficient context for clinical decision-making without raw data
- Reports timestamped and immutable after generation

### F-003: Define report delivery protocol to clinician EMR
**Priority:** P1
**Category:** Clinical
**Description:** Reports must reach the clinician's EMR, not just the manufacturer portal. Define the delivery protocol: FHIR, HL7, direct download, or clinician-pull model.
**Acceptance Criteria:**
- FHIR-based report delivery to EMR systems
- Fallback: clinician downloads from manufacturer portal
- Report delivery confirmed by clinician system acknowledgement
- Reports available in manufacturer portal only until confirmed delivery to EMR, then burn

### F-004: Handle report generation for periods spanning sensor gaps
**Priority:** P1
**Category:** Clinical
**Description:** CGM data has gaps (sensor warmup, sensor removal, connectivity loss). Reports must accurately represent these gaps rather than interpolating or hiding them.
**Acceptance Criteria:**
- Sensor gaps clearly marked in reports
- No interpolation across gaps >30 minutes
- Report metadata includes: total monitoring time, gap count, gap duration
- Clinical metrics (TIR, GMI) calculated only from valid data periods

### F-005: Define report regeneration limitations after raw data burn
**Priority:** P1
**Category:** Clinical
**Description:** After raw data is burned, the report is the only remaining record. If a clinician needs a different analysis (e.g., different target range, different time window, overlay with insulin data), it cannot be generated. Define what is lost and how to mitigate.
**Acceptance Criteria:**
- List of analyses impossible after raw data burn
- Mitigation: generate a comprehensive set of reports before burn
- Mitigation: patient retains raw data in portable record for ad-hoc analysis
- Clear documentation of limitations for clinicians

### F-006: Specify report retention in clinician EMR
**Priority:** P2
**Category:** Clinical
**Description:** Once a report is in the clinician's EMR, it is subject to medical record retention laws (typically 7–10 years for adults, until age of majority + 7 years for minors). The framework does not control EMR retention. Document this boundary.
**Acceptance Criteria:**
- Reports in EMR: outside framework's burn scope
- EMR retention governed by medical record retention laws
- Framework specifies that EMR reports are the clinician's responsibility
- Patient cannot burn data from clinician's EMR (but can request via existing medical records processes)

### F-007: Handle real-time clinical alerts vs. historical reports
**Priority:** P0
**Category:** Clinical
**Description:** Some clinical information is time-sensitive (severe hypoglycaemia alert to clinician). This is different from a historical report. Define how real-time clinical alerts are handled in the burn framework.
**Acceptance Criteria:**
- Real-time alerts: delivered immediately, not subject to burn schedule
- Alert metadata (timestamp, severity, glucose value) persists in clinical record
- Full context supporting the alert (surrounding glucose data): subject to Clinical Review world burn schedule
- Alert delivery confirmation required

### F-008: Define AID algorithm performance summary metrics
**Priority:** P1
**Category:** Clinical
**Description:** The paper proposes that summary metrics of AID performance serve clinical needs while raw algorithm decision logs serve manufacturer needs. Define the specific summary metrics that constitute "sufficient for clinical review."
**Acceptance Criteria:**
- Metric set: % time in closed loop, frequency of manual overrides, average algorithm-driven adjustment, mode exit frequency and reasons, predicted vs. actual glucose accuracy
- Metrics validated with endocrinologists specialising in AID management
- Metrics computable from raw data during retention window
- Metrics sufficient for: dose adjustment decisions, algorithm tuning, safety assessment

### F-009: Handle clinical reports for patients using multiple devices
**Priority:** P1
**Category:** Clinical
**Description:** A patient using a CGM + pump + connected pen has data from three sources. Clinical reports must integrate data from all sources into a unified view (as Tidepool and Glooko do today).
**Acceptance Criteria:**
- Multi-device report integration specification
- Time-aligned data from different devices
- Device-specific annotations (which device contributed which data)
- Integrated reports delivered to portable record and clinician

### F-010: Specify report content for paediatric vs. adult patients
**Priority:** P1
**Category:** Clinical
**Description:** Paediatric diabetes management has different clinical targets, metrics, and reporting needs than adult management. Define report variations for paediatric patients.
**Acceptance Criteria:**
- Paediatric-specific target ranges
- Growth-adjusted metrics where applicable
- Reports accessible to parents during custodial period
- Age-appropriate report formats for adolescents in shared-authority phase

### F-011: Handle retrospective report requests after burn
**Priority:** P1
**Category:** Clinical
**Description:** A clinician requests a report for a period whose raw data has already been burned. The system must clearly communicate that the report already generated is the only available analysis, and direct the clinician to the patient's portable record for raw data if available.
**Acceptance Criteria:**
- Clear system response: "Raw data for this period has been processed and removed. Available report: [link]"
- Redirect to patient's portable record if patient has retained raw data
- Clinician education on the burn model
- Audit trail of retrospective requests (for assessing whether burn schedules are too aggressive)

### F-012: Define minimum report retention before burn
**Priority:** P0
**Category:** Clinical
**Description:** Reports must persist in the manufacturer relay long enough for both the clinician and the portable record to receive them. Define minimum retention for generated reports in the manufacturer system.
**Acceptance Criteria:**
- Minimum retention: until confirmed delivery to both clinician EMR AND portable record
- Maximum retention: 30 days after generation (burn even without confirmation, but escalate)
- Failed deliveries flagged for manual intervention
- Reports cannot be burned before delivery confirmation

### F-013: Handle clinical reports during manufacturer system outages
**Priority:** P1
**Category:** Clinical
**Description:** If the manufacturer cloud is down during a scheduled clinical report generation, raw data burn timers must pause until the report is generated and delivered.
**Acceptance Criteria:**
- Burn timers paused during manufacturer system outages
- Outage does not trigger premature burn
- Backlog of report generation processed after outage resolution
- Patient and clinician notified of delays

### F-014: Specify report format for insurance/disability documentation
**Priority:** P2
**Category:** Clinical
**Description:** Patients sometimes need glucose management documentation for insurance claims, disability applications, or workplace accommodations. Define whether the standard clinical report meets these needs or whether a separate documentation format is required.
**Acceptance Criteria:**
- Standard clinical reports reviewed for insurance/disability documentation adequacy
- If insufficient: define supplementary report format
- Documentation reports generated during retention window (cannot be generated after burn)
- Patient can request documentation reports at any time during retention window

---

## G. Paediatric Custodial Transitions

### G-001: Define graduated authority model specification
**Priority:** P1
**Category:** Paediatric
**Description:** Formally specify the three phases of custodial authority: (1) Parent full authority, (2) Shared parent-adolescent authority, (3) Young adult exclusive authority. Define transition triggers, permission changes, and data access modifications at each transition.
**Acceptance Criteria:**
- Phase 1→2 trigger: configurable age (13–16 range) OR developmental milestone
- Phase 2→3 trigger: age of majority (jurisdictionally variable: 18 in most US states, 16 in some EU countries)
- Permission matrix for each phase
- Transition protocol: who initiates, who approves, what changes

### G-002: Design shared-authority permission model
**Priority:** P1
**Category:** Paediatric
**Description:** During shared authority (Phase 2), the adolescent can restrict parental access to historical data while the parent retains access to real-time safety alerts. This requires fine-grained, time-scoped permissions that no current system implements.
**Acceptance Criteria:**
- Adolescent can mark specific historical data as "restricted from parent"
- Parent continues to receive real-time alerts (glucose highs/lows, pump failures)
- Restriction is applied retroactively to existing data, not just new data
- Conflict resolution: if adolescent restricts data that parent believes is safety-critical

### G-003: Implement right to historical data restriction at majority
**Priority:** P1
**Category:** Paediatric
**Description:** When the young adult assumes exclusive custody, they must be able to burn historical data from the parental-management period. A 20-year-old should not be bound by persistence choices their parents made when they were 8.
**Acceptance Criteria:**
- Young adult can view all data from parental-management period
- Young adult can selectively burn any or all parental-era data
- Burn is complete and irreversible
- No notification to former custodial parent about burns (the data is now exclusively the young adult's)

### G-004: Handle custody disputes and divorce scenarios
**Priority:** P1
**Category:** Paediatric
**Description:** In divorce/separation, which parent retains custodial authority over the child's health data? If one parent set up the account and the other has custody, data access must follow legal custody, not account ownership.
**Acceptance Criteria:**
- Custody authority follows legal custody documentation, not account creation
- Support for: sole custody, joint custody, split custody arrangements
- Court-ordered data access/restriction supported
- Account transfer mechanism when custody changes

### G-005: Define paediatric consent for research data
**Priority:** P1
**Category:** Paediatric
**Description:** If a parent consented to their child's data being used for research, does that consent carry over to adulthood? The young adult should be able to withdraw consent upon assuming exclusive authority.
**Acceptance Criteria:**
- Parental research consent marked as "custodial consent" (not patient consent)
- Upon Phase 3 transition: young adult must re-consent or data exits Research World
- Data already contributed to completed research: cannot be recalled (documented limitation)
- Active research participation: suspended pending young adult re-consent

### G-006: Design account transition workflow
**Priority:** P1
**Category:** Paediatric
**Description:** The technical process of transitioning a manufacturer account from parental management to young adult ownership. This involves: credential transfer, access control changes, notification preferences, and linked app reauthorisation.
**Acceptance Criteria:**
- Step-by-step account transition protocol
- Parent receives transition notice
- Young adult sets new credentials
- All existing third-party app authorisations reviewed by young adult (re-authorise or revoke)
- Portable record custody transfers

### G-007: Handle siblings and multi-child families
**Priority:** P2
**Category:** Paediatric
**Description:** A parent managing CGM data for two children with T1D must have separate custodial authority for each child, with independent transition timelines. Ensure the system doesn't conflate siblings' data governance.
**Acceptance Criteria:**
- Each child has independent data custody
- Independent transition timelines per child
- Parent can manage multiple custodial relationships simultaneously
- No data leakage between siblings' records

### G-008: Define age verification mechanism
**Priority:** P1
**Category:** Paediatric
**Description:** Transition triggers based on age require age verification. Define how the system verifies the patient's age at transition points.
**Acceptance Criteria:**
- Age established at account creation (parent-provided, clinician-verified)
- Age verification at Phase 2 transition (may require re-verification)
- Handling of incorrect age on original account
- System cannot refuse transition if age is verified by official documentation

### G-009: Specify paediatric emergency access by parent after transition
**Priority:** P1
**Category:** Paediatric
**Description:** After transition to exclusive adult authority, a parent may need emergency access if the young adult is incapacitated. Define whether this is possible and under what conditions (separate from the general emergency access in E-013).
**Acceptance Criteria:**
- Young adult can designate emergency contacts (may include parents)
- Designation is the young adult's choice, not automatic
- Emergency access limited to recent data (same as E-013)
- No automatic reversion to parental authority

### G-010: Handle paediatric patients who are legally emancipated
**Priority:** P2
**Category:** Paediatric
**Description:** Some minors are legally emancipated before age of majority. The system must support early transition to exclusive authority for emancipated minors.
**Acceptance Criteria:**
- Emancipation documentation triggers early Phase 3 transition
- All Phase 3 rights granted upon emancipation verification
- No minimum age for emancipation-triggered transition (varies by jurisdiction)

### G-011: Define foster care and institutional custodial scenarios
**Priority:** P2
**Category:** Paediatric
**Description:** Children in foster care or institutional settings have custodial arrangements that change frequently. Define data governance for: foster parents, group homes, residential treatment facilities, and custody changes.
**Acceptance Criteria:**
- Institutional custodian can manage data with limited authority
- Custody changes trigger authority transfer (not data burn)
- Data history preserved across custody changes
- Young adult receives full custody history at majority

### G-012: Specify international custody and cross-border data issues
**Priority:** P2
**Category:** Paediatric
**Description:** A child diagnosed in one country may move to another with different age-of-majority laws and data protection regulations. Define how custody transitions handle jurisdictional changes.
**Acceptance Criteria:**
- Custody transition age follows jurisdiction where child is currently domiciled
- Data protection applies per current jurisdiction
- Cross-border data transfer governed by applicable laws (GDPR, etc.)
- System supports multiple jurisdictional profiles

### G-013: Handle school and camp CGM data sharing
**Priority:** P2
**Category:** Paediatric
**Description:** Parents often share real-time CGM data with school nurses or diabetes camp staff. Define how these temporary, role-limited sharing authorisations work within the framework.
**Acceptance Criteria:**
- Temporary access grants: time-limited (e.g., school hours, camp duration)
- Access limited to real-time alerts and current glucose only
- No historical data access for school/camp staff
- Access automatically expires at defined end time
- Audit trail of all temporary access

### G-014: Define adolescent data literacy education requirements
**Priority:** P2
**Category:** Paediatric
**Description:** Before assuming shared or exclusive authority, adolescents should understand what data sovereignty means, what burn implies, and what they're taking responsibility for. Define educational requirements.
**Acceptance Criteria:**
- Age-appropriate educational materials
- Interactive onboarding at Phase 2 transition
- Comprehensive education at Phase 3 transition
- Education covers: what data exists, where it lives, what burn means, what happens if portable record is lost

### G-015: Specify grandparent and extended family caregiver access
**Priority:** P2
**Category:** Paediatric
**Description:** Many children spend time with grandparents or extended family who may need access to real-time glucose data for safety. Define limited caregiver access roles beyond parent.
**Acceptance Criteria:**
- Parent can grant limited access to designated caregivers
- Caregiver access limited to real-time safety alerts
- No historical data access for extended caregivers
- Access revocable by parent (Phase 1) or adolescent (Phase 2) or young adult (Phase 3)
- Maximum number of active caregivers

---

## H. Consumer Wellness

### H-001: Implement zero-default-retention for consumer wellness CGM
**Priority:** P1
**Category:** Consumer Wellness
**Description:** For non-diabetic consumers using CGM as a wellness tool (e.g., Dexcom Stelo), all manufacturer data retention defaults to zero. No glucose data persists in manufacturer cloud unless consumer explicitly opts in.
**Acceptance Criteria:**
- Consumer wellness account type with zero-retention default
- Real-time display functions without cloud persistence
- Historical review available only through patient-controlled portable record
- Consumer clearly classified as non-patient at account creation

### H-002: Design consumer opt-in persistence mechanism
**Priority:** P1
**Category:** Consumer Wellness
**Description:** Consumers who want manufacturer-held historical data must explicitly opt in. Define the opt-in flow: what information is disclosed, how granular is the choice, how easy is it to opt out later.
**Acceptance Criteria:**
- Opt-in flow requires at minimum 3 affirmative actions (not a single checkbox)
- Disclosure includes: what data, how long, what purposes, who may access
- Granular opt-in: consumer can opt in for some data types but not others
- Opt-out: immediate, triggering burn of all manufacturer-held data

### H-003: Distinguish consumer wellness users from patients in the same system
**Priority:** P1
**Category:** Consumer Wellness
**Description:** The same Dexcom cloud infrastructure serves both diabetic patients and wellness consumers using Stelo. The system must enforce different retention defaults for different user types using the same infrastructure.
**Acceptance Criteria:**
- Account classification: patient vs. consumer wellness
- Different default retention policies per classification
- Classification cannot be changed by manufacturer without user action
- Same data format and security regardless of classification

### H-004: Handle consumer wellness users who become patients
**Priority:** P1
**Category:** Consumer Wellness
**Description:** A consumer wellness CGM user may be diagnosed with diabetes and transition to patient status. Define the transition: does their historical data (if retained via opt-in) retroactively get clinical governance? Do burn defaults change?
**Acceptance Criteria:**
- Reclassification from consumer to patient supported
- Historical data (if opted-in) transitions to Clinical Review world governance
- New burn schedules apply from reclassification date forward
- Historical data from consumer period: governed by patient's portable record

### H-005: Define business model disclosure requirements
**Priority:** P1
**Category:** Consumer Wellness
**Description:** The paper states: if a manufacturer cannot sustain a consumer wellness CGM product without indefinite data retention, this confirms the business model depends on data monetisation. This fact must be disclosed to consumers.
**Acceptance Criteria:**
- Manufacturer must disclose whether the product's business model includes data monetisation
- Disclosure in plain language, not buried in terms of service
- Consumer informed before purchase/subscription
- If monetisation changes (introduced or removed), consumer notified

### H-006: Handle consumer wellness data shared with fitness platforms
**Priority:** P1
**Category:** Consumer Wellness
**Description:** Consumer wellness CGM users commonly share glucose data with fitness apps (Apple Health, Google Fit, Strava, MyFitnessPal). These integrations often have even weaker data governance than medical apps. Define burn-propagation for fitness integrations.
**Acceptance Criteria:**
- Same burn-propagation requirements apply to fitness apps as to medical apps
- Fitness apps must implement burn endpoints
- Consumer wellness data in fitness platforms subject to same revocation rights
- Acknowledged limitation: fitness platform compliance may be harder to enforce than medical app compliance

### H-007: Address regulatory classification of consumer wellness CGM data
**Priority:** P2
**Category:** Consumer Wellness
**Description:** Consumer wellness CGM data may not be classified as medical data under HIPAA or equivalent laws. Define the framework's position on governance regardless of regulatory classification.
**Acceptance Criteria:**
- Framework governance applies regardless of regulatory classification
- Consumer wellness data treated with same security as medical data
- Regulatory gap documented and flagged for legislative action
- Framework does not depend on regulatory classification for enforcement

### H-008: Handle consumer wellness children/adolescents
**Priority:** P2
**Category:** Consumer Wellness
**Description:** Non-diabetic adolescents may use consumer wellness CGMs (e.g., for athletic performance). Define whether paediatric custodial transition requirements apply to non-patient minors.
**Acceptance Criteria:**
- Paediatric governance applies to all minors regardless of patient/consumer status
- Graduated authority model applies
- Consumer wellness minor has same rights at majority as patient minor
- Parent cannot retain wellness data against young adult's wishes

### H-009: Define consumer wellness data for insurance risk
**Priority:** P1
**Category:** Consumer Wellness
**Description:** A core harm vector: consumer wellness glucose data used for insurance risk modelling. Even without formal sharing, pattern-of-life data (sleep, diet, alcohol) is inferrable from glucose traces. Define protections.
**Acceptance Criteria:**
- Consumer wellness data may not be shared with insurers under any circumstance (framework position)
- Technical enforcement: API access denied for entities classified as insurers
- Contractual prohibition on re-sharing with insurance entities
- Acknowledged limitation: enforcement is imperfect once data leaves manufacturer

### H-010: Handle international consumer wellness markets
**Priority:** P2
**Category:** Consumer Wellness
**Description:** Consumer wellness CGMs may be regulated differently in different markets (FDA-cleared in US, CE-marked in EU, unregulated in some markets). Define framework applicability across markets.
**Acceptance Criteria:**
- Framework applies regardless of market regulatory status
- Local regulations override framework minimums where more protective
- Framework provides baseline where no local regulation exists
- Manufacturer cannot use favourable jurisdiction to avoid governance

### H-011: Define consumer wellness research participation
**Priority:** P2
**Category:** Consumer Wellness
**Description:** Consumer wellness users may be invited to participate in research (e.g., population glucose response studies). Define consent requirements for non-patient research participation.
**Acceptance Criteria:**
- Same research consent requirements as patient users
- IRB/ethics review required
- Defined retention periods
- Consent withdrawal triggers burn
- Consumer clearly informed they are contributing to research, not receiving clinical benefit

---

## I. Cybersecurity

### I-001: Conduct threat model for Chambers architecture
**Priority:** P0
**Category:** Security
**Description:** Develop a comprehensive threat model covering: BLE interception, manufacturer cloud breach, third-party app compromise, portable record theft, burn mechanism manipulation, real-time stream corruption, and custodial authority hijacking.
**Acceptance Criteria:**
- STRIDE or equivalent threat model for each component
- Threat severity and likelihood assessment
- Mitigation strategy for each identified threat
- Residual risk acceptance documented

### I-002: Define BLE encryption requirements for all device pairs
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Security
**Description:** Mandate authenticated encryption for all BLE communications: CGM↔phone, pump↔phone, pump↔CGM (in direct-communication AID systems). Published research shows these channels are currently vulnerable.
**Acceptance Criteria:**
- BLE 5.0+ with Secure Connections mandatory
- AES-CCM or equivalent encryption for all data
- MITM protection via numeric comparison or OOB pairing
- No fallback to legacy pairing modes

### I-003: Address radio frequency insulin pump command interception
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Security
**Description:** Published research demonstrates insulin pump commands can be intercepted and replayed over unencrypted radio frequencies. Require cryptographic authentication of all pump commands.
**Acceptance Criteria:**
- All pump commands cryptographically authenticated
- Replay attack prevention (nonce/sequence number)
- Command integrity verification
- Unauthorized command rejection with alert

### I-004: Harden manufacturer cloud for reduced data footprint
**Priority:** P1
**Category:** Security
**Description:** With burn semantics reducing the volume of data in the manufacturer cloud, the remaining data (current clinical window + device maintenance) must be hardened. Less data means a smaller target, but the remaining data is concentrated and high-value.
**Acceptance Criteria:**
- Encryption at rest for all stored data
- Encryption in transit for all data flows
- Access control: principle of least privilege
- Regular penetration testing
- Incident response plan specific to medical device data

### I-005: Secure the burn mechanism itself
**Priority:** P0
**Category:** Security
**Description:** The burn mechanism is a high-value attack target. An attacker who can trigger unauthorized burns can destroy patient data. An attacker who can prevent burns can ensure data persists for exfiltration. Secure the burn mechanism against both attack vectors.
**Acceptance Criteria:**
- Burn operations require authentication and authorization
- Patient-initiated burns: multi-factor authentication
- System-initiated burns: signed burn schedules, tamper-evident
- Burn mechanism availability: cannot be DoS'd to prevent scheduled burns
- Unauthorized burn attempts logged and alerted

### I-006: Define portable record encryption and key management
**Priority:** P0
**Category:** Security
**Description:** The portable record contains the patient's complete health data history. It must be encrypted at rest with patient-controlled keys. Define the key management system: key generation, storage, rotation, recovery, and destruction.
**Acceptance Criteria:**
- AES-256 or equivalent encryption at rest
- Keys generated on patient's device (never transmitted to manufacturer)
- Key backup mechanism (recovery phrase, secondary device, trusted contact)
- Key rotation without full re-encryption
- Key destruction = data destruction (cryptographic erasure)

### I-007: Address smartphone as critical therapeutic node
**Priority:** P0
**Category:** Security
**Description:** The smartphone is a critical node in the therapeutic chain (receives CGM data, runs AID algorithm, commands pump). A compromised smartphone can: corrupt glucose readings, send incorrect pump commands, exfiltrate data, prevent burns. Define smartphone security requirements.
**Acceptance Criteria:**
- OS-level security requirements (minimum OS version, no jailbreak/root)
- App-level integrity verification
- Sandboxing of therapeutic app from other apps
- Malware detection integration
- Backup therapeutic path if phone is compromised (pump-based standalone operation)

### I-008: Secure third-party API access
**Priority:** P1
**Category:** Security
**Description:** Third-party apps access patient data via manufacturer APIs. Secure the API layer: authentication, authorization, rate limiting, data minimisation in API responses, and logging.
**Acceptance Criteria:**
- OAuth 2.0 or equivalent authentication for all API access
- Scoped tokens (app only receives data types it needs)
- Rate limiting to prevent bulk data extraction
- API access logging with anomaly detection
- Regular API security audit

### I-009: Define incident response plan for real-time stream compromise
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Security
**Description:** A real-time stream compromise (corrupted glucose readings, hijacked pump commands) is the highest-severity security incident. Define the incident response: detection, containment, patient notification, regulatory reporting.
**Acceptance Criteria:**
- Automated detection of anomalous real-time data patterns
- Immediate containment: switch to safe mode (suspend automation)
- Patient notification within minutes
- Manufacturer notification within 1 hour
- Regulatory reporting per device incident reporting requirements
- Forensic investigation protocol

### I-010: Address data re-identification risk in aggregated pools
**Priority:** P1
**Category:** Security
**Description:** Aggregated/de-identified CGM data pools may be vulnerable to re-identification attacks. Continuous glucose traces are highly individual (like fingerprints). Assess re-identification risk and define mitigation.
**Acceptance Criteria:**
- Re-identification risk assessment for CGM data
- Minimum k-anonymity threshold for aggregated datasets
- Differential privacy consideration for research data releases
- Prohibition on linking aggregate data with external datasets

### I-011: Secure paediatric custody transition against social engineering
**Priority:** P1
**Category:** Security
**Description:** Custody transitions are vulnerable to social engineering: a non-custodial parent attempting to gain data access, an abuser attempting to maintain surveillance via CGM data. Define identity verification and abuse prevention measures.
**Acceptance Criteria:**
- Custody transition requires legal documentation
- Identity verification for all parties
- Abuse detection: monitor for access patterns consistent with surveillance
- Young adult can initiate emergency lockout of former custodians

### I-012: Define security requirements for portable record backup
**Priority:** P1
**Category:** Security
**Description:** Portable record backups are copies of the patient's complete health history. If a backup is stolen, compromised, or leaked, the patient's entire data sovereignty is violated. Define backup security.
**Acceptance Criteria:**
- Backups encrypted with patient-controlled keys (same or derived from primary)
- Backup at rest: encryption required regardless of storage medium
- Backup in transit: encryption required
- Backup access: same authentication as primary
- Backup destruction: same burn semantics as primary

### I-013: Address supply chain security for CGM/pump hardware
**Priority:** P2
**Category:** Security
**Description:** Hardware supply chain attacks could introduce compromised sensors or pumps that exfiltrate data or manipulate readings. While outside the burn framework's scope, it affects the threat model.
**Acceptance Criteria:**
- Hardware integrity verification (secure boot, firmware signing)
- Supply chain audit requirements for manufacturers
- Tamper-evident packaging and device sealing
- Firmware update authentication (only manufacturer-signed updates)

### I-014: Define security monitoring and logging requirements
**Priority:** P1
**Category:** Security
**Description:** Comprehensive security monitoring across the ecosystem: device-level, app-level, API-level, cloud-level, and burn-mechanism-level. Define what is logged, how long logs are retained, and who reviews them.
**Acceptance Criteria:**
- Log categories: authentication events, data access, burn operations, API calls, anomalies
- Log retention: sufficient for incident investigation (90 days operational, 1 year archived)
- Automated alerting on high-severity events
- Regular log review (automated + manual)
- Logs themselves subject to burn schedule (no indefinite log retention)

### I-015: Handle vulnerability disclosure and patching for burn mechanism
**Priority:** P1
**Category:** Security
**Description:** If a vulnerability is discovered in the burn mechanism (data not actually destroyed, burn can be bypassed), define the vulnerability disclosure process and patching timeline.
**Acceptance Criteria:**
- Responsible disclosure programme for burn mechanism vulnerabilities
- Critical vulnerability patch: within 48 hours
- Affected patients notified: within 72 hours
- Forensic assessment: was the vulnerability exploited?
- Retrospective burn verification for affected data

### I-016: Secure inter-manufacturer data transfer during device switching
**Priority:** P1
**Category:** Security
**Description:** When a patient switches manufacturers (e.g., Dexcom to Abbott), data in the portable record must transfer securely. The old manufacturer must burn their copy. Define the secure transition protocol.
**Acceptance Criteria:**
- No data transferred directly between manufacturers (goes through patient's portable record)
- Old manufacturer burns all data per standard schedule
- New manufacturer receives data only from patient's portable record
- No back-channel data sharing between manufacturers about the patient

### I-017: Define penetration testing requirements for the complete architecture
**Priority:** P1
**Category:** Security
**Description:** The full Chambers architecture must undergo regular penetration testing. Define scope, frequency, and pass/fail criteria.
**Acceptance Criteria:**
- Annual penetration test of: manufacturer cloud, portable record, burn mechanism, API layer, BLE communications
- Test scenarios include: unauthorized burn, burn prevention, data exfiltration, world boundary violation, custody hijacking
- Findings remediated within defined SLAs (critical: 48h, high: 7d, medium: 30d, low: 90d)
- Test reports available to regulator upon request

---

## J. Regulatory & Legal Infrastructure

### J-001: Analyse HIPAA applicability to manufacturer-held CGM data
**Priority:** P1
**Category:** Regulatory
**Description:** The paper identifies that CGM manufacturers may not qualify as HIPAA covered entities or business associates in all contexts. Commission a formal legal analysis of HIPAA applicability across different manufacturer-patient relationships.
**Acceptance Criteria:**
- Legal analysis from qualified health privacy counsel
- Scenarios analysed: direct-to-consumer sale, prescribed device, employer wellness programme
- Gap assessment: what data falls outside HIPAA protection?
- Recommendations for framework enforcement mechanisms that don't depend on HIPAA

### J-002: Assess GDPR and EU MDR applicability
**Priority:** P1
**Category:** Regulatory
**Description:** The EU has stronger data protection (GDPR) and medical device regulation (EU MDR). Assess how the framework interacts with: GDPR right to erasure, GDPR data minimisation principle, EU MDR post-market surveillance requirements, and GDPR data portability rights.
**Acceptance Criteria:**
- GDPR alignment assessment: where does the framework exceed GDPR? Where does it fall short?
- EU MDR post-market surveillance data retention vs. burn schedule conflict analysis
- GDPR portability right vs. portable record mapping
- Recommendations for EU-specific framework calibration

### J-003: Define contractual enforcement mechanism for burn semantics
**Priority:** P1
**Category:** Regulatory
**Description:** Without legislative data property rights, contractual obligations embedded in device purchase/subscription terms are the most immediately available enforcement mechanism. Draft model contract terms.
**Acceptance Criteria:**
- Model contract language for manufacturer-patient agreement
- Burn schedule obligations explicitly stated
- Breach remedies defined
- Third-party API access agreement template with burn-propagation obligations
- Legal review in major jurisdictions (US, EU, UK, Canada, Australia)

### J-004: Propose regulatory mandate for medical device data minimisation
**Priority:** P2
**Category:** Regulatory
**Description:** The paper identifies that regulatory mandates for data minimisation (not depending on ownership) are a plausible enforcement mechanism. Draft a regulatory proposal for submission to FDA and/or EMA.
**Acceptance Criteria:**
- Regulatory proposal document
- Evidence base: theory of harm, counterargument analysis, proposed architecture
- Precedent analysis: existing data minimisation mandates in other sectors
- Stakeholder feedback from: device manufacturers, patient advocates, clinicians, regulators

### J-005: Address FDA post-market surveillance vs. burn schedule conflict
**Priority:** P1
**Category:** Regulatory
**Description:** FDA requires post-market surveillance for medical devices, which may require retention of certain data. Define how burn schedules accommodate FDA surveillance requirements without becoming a loophole for indefinite retention.
**Acceptance Criteria:**
- FDA post-market surveillance data requirements mapped
- Minimum retention defined per surveillance requirement
- Surveillance data classified into Device Maintenance or Research worlds
- Surveillance does not require identified raw patient data (de-identified may suffice)

### J-006: Analyse state-level health privacy laws (US)
**Priority:** P2
**Category:** Regulatory
**Description:** Several US states have enacted health privacy laws beyond HIPAA (e.g., Washington My Health My Data Act, California CCPA health data provisions). Assess framework compatibility with state laws.
**Acceptance Criteria:**
- Survey of state health privacy laws applicable to CGM data
- Framework compliance assessment per state
- Identification of states where framework exceeds legal requirements
- Identification of states where additional calibration is needed

### J-007: Define patient data property rights proposal
**Priority:** P2
**Category:** Regulatory
**Description:** The paper acknowledges that without a property baseline, the framework's governance claim is weaker. Draft a position paper on patient data property rights for medical device data.
**Acceptance Criteria:**
- Legal scholarship review on data property rights
- Proposed property rights framework for medical device data
- Analysis of: ownership vs. custodial rights, practical implications, enforcement mechanisms
- Comparison with existing property frameworks (GDPR data subject rights, California consumer rights)

### J-008: Address international data transfer requirements
**Priority:** P1
**Category:** Regulatory
**Description:** Manufacturer clouds may store data in different jurisdictions than the patient resides. International data transfer rules (GDPR Chapter V, Privacy Shield successor) interact with burn semantics. Define compliance requirements.
**Acceptance Criteria:**
- Data residency requirements mapped per jurisdiction
- Burn semantics apply regardless of data location
- International transfer does not create burn-exempt copies
- Patient informed of where their data is stored geographically

### J-009: Define manufacturer reporting obligations for burn compliance
**Priority:** P1
**Category:** Regulatory
**Description:** Manufacturers should report burn compliance metrics to regulators. Define what metrics, how often, and in what format.
**Acceptance Criteria:**
- Annual burn compliance report: total data items burned, pending burns, failed burns, average burn latency
- Aggregate patient opt-in/opt-out statistics
- Third-party burn-propagation compliance rates
- Report format standardised for regulatory submission

### J-010: Address class action and collective action mechanisms
**Priority:** P2
**Category:** Regulatory
**Description:** If a manufacturer fails to comply with burn obligations, what legal remedies are available to affected patients? Define potential class action and collective action mechanisms.
**Acceptance Criteria:**
- Legal analysis of available remedies per jurisdiction
- Mandatory arbitration clause concerns (common in manufacturer ToS)
- Regulatory enforcement vs. private action comparison
- Model complaint/petition for regulatory agencies

### J-011: Define liability framework for burn-related data loss
**Priority:** P1
**Category:** Regulatory
**Description:** If a patient experiences harm because data was burned (e.g., clinician couldn't access a historical record that would have changed treatment), who is liable? Define the liability framework.
**Acceptance Criteria:**
- Liability analysis: manufacturer, portable record provider, patient
- Informed consent documentation requirements (patient understood burn implications)
- Medical malpractice implications for clinicians relying on reports vs. raw data
- Insurance/indemnification framework

### J-012: Address antitrust implications of data portability
**Priority:** P2
**Category:** Regulatory
**Description:** The portable record reduces manufacturer data lock-in, which has antitrust implications. Assess whether the framework's portability requirements could be supported by or conflict with antitrust enforcement.
**Acceptance Criteria:**
- Antitrust analysis of current manufacturer data lock-in
- Portable record as pro-competitive intervention
- Assessment of potential manufacturer pushback arguments
- Regulatory pathways for mandating data portability

---

## K. Data Classification & Governance

### K-001: Classify all CGM data types into worlds
**Priority:** P1
**Category:** Governance
**Description:** Every data type generated by every supported CGM (Dexcom G7, Abbott FreeStyle Libre 3, Medtronic Guardian 4, Senseonics Eversense 365) must be classified into exactly one world. Some types are straightforward (glucose reading → Clinical Review → burn after report); others are ambiguous (calibration algorithm parameters → Device Maintenance? Research?).
**Acceptance Criteria:**
- Complete classification table for each CGM manufacturer
- Ambiguous classifications flagged with rationale for chosen world
- Clinical stakeholder validation of classifications
- Annual review schedule for reclassification

### K-002: Classify all insulin pump data types into worlds
**Priority:** P1
**Category:** Governance
**Description:** Same as K-001 for insulin pump data: basal rates, bolus events, correction factors, carb ratios, user settings, alarm logs, reservoir levels, infusion set changes, etc.
**Acceptance Criteria:**
- Complete classification table for each pump manufacturer
- Separate classification for pump-only vs. AID-integrated data
- Clinical stakeholder validation

### K-003: Classify AID algorithm data types into worlds
**Priority:** P1
**Category:** Governance
**Description:** AID algorithm data is the "hardest case" per the paper. Classify: predicted glucose values, adjustment magnitudes, automated mode exits/entries, learning parameters, insulin sensitivity factors derived by algorithm, target range modifications. Distinguish clinically useful summary metrics from commercially valuable raw decision logs.
**Acceptance Criteria:**
- Summary metrics → Clinical Review world
- Raw decision logs → Research world (consent-gated)
- Learning parameters → Device Maintenance world (operational state)
- Classification validated with AID algorithm engineers AND endocrinologists
- Acknowledged tension: algorithm engineers may argue the distinction is artificial

### K-004: Classify connected insulin pen data types into worlds
**Priority:** P1
**Category:** Governance
**Description:** Connected pens generate: injection timestamps, dose amounts, cartridge serial numbers, pen serial numbers, temperature logs. Classify each into a world.
**Acceptance Criteria:**
- Complete classification table for NovoPen 6, Echo Plus, Lilly Tempo
- Injection data classified similarly to bolus data from pumps
- Device metadata classified into Device Maintenance world

### K-005: Classify meal, activity, and lifestyle logging data
**Priority:** P1
**Category:** Governance
**Description:** The paper identifies meal/activity/lifestyle data as "plausibly commercially beneficial beyond demonstrated safety necessity." Classify these user-entered data types. Consider: meal photos, carb counts, exercise logs, sleep data, stress ratings, menstrual cycle tracking.
**Acceptance Criteria:**
- Meal/activity data classified as: short-term Clinical Review (14–90 day window) for pattern recognition, then burn
- Lifestyle data (sleep, stress, menstrual cycle): no clinical safety justification for manufacturer retention
- User-entered data: patient retains in portable record; manufacturer burns after clinical window
- Consumer wellness users: zero retention of lifestyle data

### K-006: Define data classification governance process
**Priority:** P1
**Category:** Governance
**Description:** Data classifications are tentative and must be revisited as clinical practice evolves, new devices emerge, and analytical capabilities change. Define the governance process for classification review and change.
**Acceptance Criteria:**
- Annual classification review with multi-stakeholder panel
- Change proposal mechanism (any stakeholder can propose reclassification)
- Impact assessment required for reclassification
- Patient notification when classifications change (if retention changes)

### K-007: Handle new data types from future devices
**Priority:** P1
**Category:** Governance
**Description:** New devices will generate new data types not anticipated by the current classification. Define the default classification for unclassified data types and the process for formal classification.
**Acceptance Criteria:**
- Default: unclassified data receives the most restrictive burn schedule
- New data types flagged for classification within 30 days of device launch
- No unclassified data persists in manufacturer cloud beyond 90 days without classification
- Manufacturer cannot unilaterally classify new data types into permissive worlds

### K-008: Define purpose limitation enforcement mechanism
**Priority:** P1
**Category:** Governance
**Description:** Data classified in one world must not be used for purposes of another world (e.g., Clinical Review data must not be used for commercial analytics). Define the technical and policy enforcement mechanism.
**Acceptance Criteria:**
- Access controls enforce world boundaries
- Cross-world data queries logged and reviewed
- Violation alerts triggered by unauthorized cross-world access
- Annual purpose limitation audit

### K-009: Classify app metadata and usage telemetry
**Priority:** P1
**Category:** Governance
**Description:** Manufacturer apps generate metadata beyond health data: app usage patterns, screen time, feature usage, crash logs, device identifiers, IP addresses. Classify these into worlds or exclude from the framework.
**Acceptance Criteria:**
- App crash logs: Device Maintenance world (needed for app stability)
- Usage telemetry: no clinical safety justification; burn after analysis window (30 days)
- Device identifiers: minimum necessary for Device Maintenance world
- IP addresses: no retention beyond session
- Location data: no retention unless patient explicitly opts in

### K-010: Define data classification for retrospective analysis requests
**Priority:** P2
**Category:** Governance
**Description:** A clinician may request a non-standard analysis (e.g., "overlay glucose with pump suspension events for the last 6 months"). This requires raw data that may have been burned. Define how retrospective analysis requests interact with the classification system.
**Acceptance Criteria:**
- Standard clinical reports cover most clinical needs (validated per F-001)
- Non-standard analyses require raw data from portable record
- Manufacturer cannot fulfill non-standard retrospective requests after burn
- Clinician education on available analyses within and beyond burn window

### K-011: Handle de-identification standards for research data
**Priority:** P1
**Category:** Governance
**Description:** Research World data may be de-identified for broader use. Define de-identification standards that account for the re-identification risks specific to CGM data (unique glucose patterns serving as biometric identifiers).
**Acceptance Criteria:**
- HIPAA Safe Harbor and Expert Determination methods assessed for CGM data
- CGM-specific re-identification risk assessment (glucose patterns as biometric)
- Additional protections if CGM data is deemed high re-identification risk
- De-identification verified by qualified expert before release

### K-012: Define data classification for device-generated alerts and alarms
**Priority:** P1
**Category:** Governance
**Description:** CGMs and pumps generate alerts (high glucose, low glucose, rapid rate of change, sensor error, pump occlusion). Classify these: are alerts the same as glucose readings? Do they have different burn schedules?
**Acceptance Criteria:**
- Alert metadata (timestamp, type, severity): Clinical Review world
- Alert context (glucose reading that triggered alert): same as underlying glucose reading
- Alert response data (user acknowledged, user took action): short-term Clinical Review
- Clinically significant alerts (severe hypo/hyper): extended retention within clinical window

### K-013: Address patient-generated notes and annotations
**Priority:** P2
**Category:** Governance
**Description:** Patients can add notes to their glucose data ("felt dizzy," "forgot medication," "ate pizza"). These are user-generated content with clinical value but also privacy sensitivity. Classify and define burn schedules.
**Acceptance Criteria:**
- Patient notes: owned by patient, stored in portable record
- Notes shared with clinician: subject to Clinical Review world burn
- Notes shared with manufacturer: no clinical safety justification for retention
- Notes may contain sensitive information (mental health, substance use): handle with heightened privacy

### K-014: Define classification dispute resolution
**Priority:** P2
**Category:** Governance
**Description:** Manufacturers and patients may disagree on data classification (manufacturer wants data in Research world; patient believes it should burn from Clinical Review). Define a dispute resolution process.
**Acceptance Criteria:**
- Independent review panel for classification disputes
- Panel composition: clinicians, patients, privacy experts, engineers
- Decision binding on manufacturer
- Patient's right to apply more restrictive classification to their own data

---

## L. Manufacturer Counterargument Accommodation

### L-001: Design governed research repository for safety signal detection
**Priority:** P1
**Category:** Counterargument
**Description:** Create a specification for a dedicated research repository (separate from operational cloud) that serves safety signal detection needs without requiring indefinite identified retention in the operational system.
**Acceptance Criteria:**
- Repository architecture specification
- Governance model: who controls access, what research is permitted
- Data contributions: consent-gated, time-bounded
- Safety signal detection methodology that works with governed data
- Comparison with current approach: does governed access meaningfully impair signal detection?

### L-002: Conduct empirical study on algorithm training with time-bounded data
**Priority:** P1
**Category:** Counterargument
**Description:** The strongest counterargument for indefinite retention is AID algorithm training. Commission an empirical study: can algorithms of equivalent quality be trained with time-bounded data access (e.g., 2-year rolling window) vs. indefinite archives?
**Acceptance Criteria:**
- Study design with statistical power to detect meaningful quality differences
- Collaboration with AID algorithm teams (Tandem, Insulet, Medtronic, Tidepool)
- Results published in peer-reviewed venue
- If time-bounded access degrades quality: quantify the trade-off; define acceptable degradation threshold

### L-003: Design patient-elected persistence experience
**Priority:** P1
**Category:** Counterargument
**Description:** Patients who value manufacturer-held continuity can elect persistence. Design the user experience: how is the option presented? When? How does the patient understand what they're choosing?
**Acceptance Criteria:**
- Election offered at account setup and periodically thereafter
- Clear explanation of what persistence means (manufacturer retains, governance applies)
- Comparison with portable record option
- Election is granular (choose which data types, choose duration)
- Revocation available at any time with immediate burn

### L-004: Define governed retention window for value extraction
**Priority:** P1
**Category:** Counterargument
**Description:** Manufacturers may extract training value during the permitted retention window. Define what "governed extraction" looks like: what analyses are permitted, what reporting is required, what limitations apply.
**Acceptance Criteria:**
- Permitted analyses enumerated (algorithm training, safety analysis, clinical report generation)
- Prohibited analyses enumerated (marketing, insurance, advertising)
- Audit trail of all analyses performed during retention window
- Report to patient on what analyses were performed on their data

### L-005: Address care continuity without manufacturer retention
**Priority:** P1
**Category:** Counterargument
**Description:** Define how care continuity is maintained when a patient sees a new clinician and the manufacturer no longer holds historical data. The portable record is the primary mechanism, but backup pathways must exist.
**Acceptance Criteria:**
- Portable record as primary care continuity mechanism
- Patient can share portable record with new clinician in <5 minutes
- If portable record unavailable: clinician accesses reports in previous clinician's EMR (standard medical records process)
- If no prior records available: clinician begins fresh (no worse than pre-CGM era)

### L-006: Design manufacturer transition assistance programme
**Priority:** P2
**Category:** Counterargument
**Description:** Manufacturers transitioning from indefinite retention to burn semantics need a migration plan. Define a phased transition programme.
**Acceptance Criteria:**
- Phase 1: Notify existing patients of data governance change (6 months notice)
- Phase 2: Offer data export to portable record (3 months)
- Phase 3: Begin burn schedules for existing data (with patient consent or after export window)
- Phase 4: New data governed by burn-default from day one
- Manufacturer support resources for patient education

### L-007: Quantify cybersecurity benefit of reduced data footprint
**Priority:** P2
**Category:** Counterargument
**Description:** To support the framework's value proposition, quantify the cybersecurity benefit: how much does the attack surface shrink when historical data is burned? Model the breach impact reduction.
**Acceptance Criteria:**
- Current state: estimate data volume in major manufacturer clouds
- Post-burn state: estimate remaining data volume
- Breach impact modelling: current vs. post-burn
- Cost-benefit analysis: implementation cost vs. breach risk reduction

### L-008: Define manufacturer compliance incentive structure
**Priority:** P2
**Category:** Counterargument
**Description:** Voluntary manufacturer adoption is unlikely without incentives. Define potential incentive mechanisms: regulatory fast-track, liability safe harbor, certification mark, patient preference signals.
**Acceptance Criteria:**
- Incentive catalogue with feasibility assessment
- Regulatory engagement strategy
- Patient demand signalling mechanism
- Competitive advantage analysis for early adopters

### L-009: Address algorithm training data for new market entrants
**Priority:** P2
**Category:** Counterargument
**Description:** If established manufacturers have historical data for algorithm training but burn-default prevents new entrants from accumulating equivalent datasets, this could entrench incumbents. Address the competitive fairness concern.
**Acceptance Criteria:**
- Analysis of algorithmic training data advantage
- Collaborative data commons proposal (consented data pooled for all algorithm developers)
- Open-source training dataset possibility
- Regulatory consideration of data advantage as barrier to entry

---

## M. Operational Preconditions & Failure Modes

### M-001: Zero-interference proof for burn mechanism on therapeutic stream
**Priority:** P0 (SAFETY-CRITICAL)
**Category:** Operations
**Description:** Provide formal or empirical proof that the burn mechanism cannot interfere with the real-time therapeutic data stream under any circumstances, including: system failure, resource exhaustion, software bugs, simultaneous operation.
**Acceptance Criteria:**
- Architectural isolation proof (separate processes, separate hardware if necessary)
- Stress testing: burn mechanism under maximum load does not affect therapeutic stream latency
- Failure mode analysis: every burn mechanism failure mode evaluated for therapeutic impact
- Independent safety review by qualified medical device safety assessor

### M-002: Define system behavior during burn mechanism outage
**Priority:** P1
**Category:** Operations
**Description:** If the burn mechanism is unavailable (maintenance, failure, attack), what happens? Data that should be burned accumulates. Define the accumulation limit, the monitoring, and the recovery procedure.
**Acceptance Criteria:**
- Burn backlog queue with monitoring
- Alert when backlog exceeds threshold (suggest: 24 hours of pending burns)
- Recovery procedure: process backlog in order, verify all burns
- No manual intervention required for recovery (fully automated)
- Therapeutic operation unaffected during burn outage

### M-003: Handle manufacturer cloud migration or acquisition
**Priority:** P1
**Category:** Operations
**Description:** If a manufacturer migrates cloud providers (AWS → Azure) or is acquired by another company, all burn schedules, pending burns, and data classifications must transfer seamlessly.
**Acceptance Criteria:**
- Burn state is portable between cloud providers
- Acquisition: data governance obligations transfer to acquiring entity
- No burn-exempt window during migration/acquisition
- Patient notified of cloud migration or acquisition

### M-004: Define performance requirements for burn at scale
**Priority:** P1
**Category:** Operations
**Description:** A manufacturer like Dexcom has millions of patients generating 288+ readings daily. The burn mechanism must operate at this scale. Define performance requirements.
**Acceptance Criteria:**
- Burn throughput: millions of data items per hour
- Burn latency: within SLA (see C-003) even at peak load
- Resource consumption: burn mechanism uses <5% of total cloud resources
- Scalability: linear scaling with patient count

### M-005: Handle sensor replacement transitions without data loss or premature burn
**Priority:** P0
**Category:** Operations
**Description:** CGM sensors are replaced every 7–365 days. During transition: warmup period on new sensor, potential overlap with old sensor, calibration events. Ensure no clinically relevant data is lost or prematurely burned during sensor transitions.
**Acceptance Criteria:**
- Sensor transition event explicitly tracked
- Data from expiring sensor retained until confirmed in portable record
- New sensor warmup data flagged and handled per B-005
- Transition gap in reports handled per F-004

### M-006: Define rollback capability for incorrectly applied burns
**Priority:** P1
**Category:** Operations
**Description:** If a burn was triggered incorrectly (software bug, misconfigured schedule), can it be rolled back? By definition, burns are irreversible — but there should be safeguards against accidental burns.
**Acceptance Criteria:**
- Pre-burn verification: data confirmed delivered to portable record
- Pre-burn staging: data marked for burn, waiting for grace period
- Grace period: configurable (suggest: 24 hours for scheduled burns)
- After grace period: irreversible burn, no rollback
- Incorrectly burned data: patient notified, incident report filed

### M-007: Define monitoring and observability for the complete architecture
**Priority:** P1
**Category:** Operations
**Description:** The Chambers architecture adds significant complexity to manufacturer systems. Define monitoring requirements for: burn execution, burn propagation, portable record delivery, world boundary enforcement, custody transitions.
**Acceptance Criteria:**
- Dashboard for each operational component
- SLA tracking for each burn type
- Anomaly detection for unusual patterns (mass burns, burn failures, access spikes)
- Capacity planning based on patient growth projections

### M-008: Handle data sovereignty during manufacturer insolvency
**Priority:** P1
**Category:** Operations
**Description:** If a manufacturer goes bankrupt, what happens to patient data in their cloud? The portable record mitigates this, but data in transit, pending burns, and Research World data need a wind-down protocol.
**Acceptance Criteria:**
- Wind-down protocol: export all patient data to portable records
- Pending burns: execute all pending burns during wind-down
- Research World data: transfer to designated research repository or burn
- Patient notification: minimum 90 days before data destruction
- Regulatory notification per device decommissioning requirements

### M-009: Define capacity planning for portable record infrastructure
**Priority:** P1
**Category:** Operations
**Description:** If millions of patients adopt portable records, the infrastructure (whether distributed or centralised) must handle the load. Define capacity planning requirements.
**Acceptance Criteria:**
- Capacity model: storage, compute, bandwidth per patient
- Growth projections: 1M, 10M, 100M patients
- Cost model per patient per year
- Infrastructure resilience requirements (availability, durability)

### M-010: Handle burn semantics during clinical trials
**Priority:** P1
**Category:** Operations
**Description:** Patients participating in clinical trials may have regulatory data retention requirements that conflict with burn schedules. Define clinical trial data handling.
**Acceptance Criteria:**
- Clinical trial data retention per regulatory requirements (often 15+ years)
- Trial data classified into Research World with trial-specific retention override
- Patient informed of retention obligations before trial enrollment
- Trial data burn after retention obligation expires

### M-011: Define testing and quality assurance programme for burn mechanism
**Priority:** P1
**Category:** Operations
**Description:** The burn mechanism is safety-critical infrastructure. Define the QA programme: test types, coverage requirements, release criteria, regression testing.
**Acceptance Criteria:**
- Unit tests: >95% code coverage for burn mechanism
- Integration tests: every inter-world transfer and burn trigger
- Stress tests: burn at 10x expected load
- Chaos engineering: fault injection to verify graceful degradation
- Release criteria: zero tolerance for burn mechanism defects rated critical or high
- Medical device software quality standards (IEC 62304) compliance

---

## N. Validation & Stakeholder Review

### N-001: Endocrinologist validation of data classifications
**Priority:** P1
**Category:** Validation
**Description:** All data classifications (Sections K-001 through K-005) must be validated by a panel of endocrinologists. Classifications are the foundation of the framework — if clinicians disagree with what is "clinically necessary," the framework fails.
**Acceptance Criteria:**
- Panel of ≥10 endocrinologists across subspecialties
- Structured review of each data classification
- Disagreements documented and resolved or escalated
- Consensus report published

### N-002: Patient advocate review of portable record design
**Priority:** P1
**Category:** Validation
**Description:** Patient advocacy organisations (JDRF, ADA, DiabetesUK, #WeAreNotWaiting community) must review the portable record design for: usability, accessibility, equity, and alignment with patient values.
**Acceptance Criteria:**
- Structured review with ≥3 patient advocacy organisations
- Usability testing with diverse patient populations
- Feedback incorporated into design
- Ongoing advisory relationship established

### N-003: Manufacturer feasibility assessment
**Priority:** P1
**Category:** Validation
**Description:** At least one major manufacturer (Dexcom, Medtronic, Abbott, Tandem, or Insulet) must provide a feasibility assessment of the proposed architecture changes: cost, timeline, technical blockers, regulatory concerns.
**Acceptance Criteria:**
- Manufacturer assessment from ≥1 major manufacturer
- Technical feasibility evaluation
- Cost and timeline estimate
- Identified blockers and proposed mitigations
- Good-faith engagement (not just a list of objections)

### N-004: Security researcher review of threat model
**Priority:** P1
**Category:** Validation
**Description:** Independent security researchers (preferably from medical device security community) must review the threat model and security requirements for completeness and realism.
**Acceptance Criteria:**
- Review by ≥2 independent security researchers
- Red team exercise on proposed architecture
- Vulnerability assessment of burn mechanism design
- Report published with findings and recommendations

### N-005: Legal review of enforcement mechanisms
**Priority:** P1
**Category:** Validation
**Description:** Health privacy law specialists must review the proposed enforcement mechanisms (contractual, regulatory, legislative) for: legal sufficiency, enforceability, jurisdictional coverage, and gaps.
**Acceptance Criteria:**
- Legal review by qualified health privacy counsel in US and EU
- Enforceability assessment per jurisdiction
- Gap analysis: what the framework requires but current law does not support
- Recommended legal reforms prioritised by impact and feasibility

### N-006: Paediatric diabetes specialist review of custody model
**Priority:** P1
**Category:** Validation
**Description:** Paediatric endocrinologists and adolescent medicine specialists must review the graduated custody model for clinical appropriateness, age thresholds, and practical implementability.
**Acceptance Criteria:**
- Review by ≥5 paediatric diabetes specialists
- Age threshold recommendation with clinical justification
- Edge case review: developmental delays, cognitive impairments, family dynamics
- Feedback on shared-authority permission model

### N-007: Regulatory body pre-submission meeting
**Priority:** P2
**Category:** Validation
**Description:** Seek pre-submission feedback from FDA (CDRH) and/or EMA on the framework's implications for medical device data governance. Understand regulatory appetite for data minimisation mandates.
**Acceptance Criteria:**
- Pre-submission meeting request filed
- Briefing document prepared
- Regulatory feedback documented
- Framework adjusted based on regulatory guidance

### N-008: Pilot implementation with single device/manufacturer
**Priority:** P1
**Category:** Validation
**Description:** Before full ecosystem deployment, pilot the framework with a single device-manufacturer combination (e.g., Tidepool Loop + Dexcom, given Tidepool's open-source orientation). Validate: burn mechanism, portable record, clinical report sufficiency, patient experience.
**Acceptance Criteria:**
- Pilot scope defined (specific device, specific manufacturer, specific patient cohort)
- Pilot duration: minimum 6 months
- Success metrics: burn compliance, clinical data availability, patient satisfaction, adverse events
- Pilot report with go/no-go recommendation for broader deployment

### N-009: Health economist assessment of framework costs and benefits
**Priority:** P2
**Category:** Validation
**Description:** Commission a health economics analysis: what does implementation cost (manufacturer infrastructure changes, portable record development, regulatory compliance) vs. what are the benefits (reduced breach costs, reduced data liability, improved patient trust)?
**Acceptance Criteria:**
- Cost model: implementation, ongoing operation, transition period
- Benefit model: risk reduction, liability reduction, patient acquisition/retention
- Net present value analysis over 10-year horizon
- Sensitivity analysis for key assumptions

### N-010: #WeAreNotWaiting community review
**Priority:** P1
**Category:** Validation
**Description:** The DIY diabetes technology community (#WeAreNotWaiting) has deep technical expertise and strong opinions on data sovereignty. Their review is critical for: technical feasibility, community adoption, and identification of edge cases the professional community may miss.
**Acceptance Criteria:**
- Engagement with Loop, AndroidAPS, and OpenAPS communities
- Technical review of portable record and burn mechanism designs
- Community feedback on practical usability
- Assessment of framework compatibility with DIY systems

### N-011: Insurance industry response assessment
**Priority:** P2
**Category:** Validation
**Description:** Assess how the insurance industry (health, life, disability) would respond to the framework. Specifically: does burn-default threaten current data access practices? Would insurers lobby against it? Are there alignment opportunities?
**Acceptance Criteria:**
- Insurance industry stakeholder interviews
- Impact assessment on current insurance data practices
- Potential opposition mapped
- Potential alignment opportunities identified (e.g., reduced breach liability)

### N-012: International regulatory harmonisation assessment
**Priority:** P2
**Category:** Validation
**Description:** Assess framework compatibility with regulatory frameworks across: US (FDA, HIPAA, state laws), EU (MDR, GDPR), UK (UKCA, UK GDPR), Canada (Health Canada, PIPEDA), Australia (TGA, Privacy Act), Japan (PMDA, APPI).
**Acceptance Criteria:**
- Regulatory mapping for each jurisdiction
- Framework calibration requirements per jurisdiction
- Harmonisation opportunities identified
- Jurisdictional conflicts documented with proposed resolution

### N-013: Clinical workflow impact assessment
**Priority:** P1
**Category:** Validation
**Description:** Assess how the framework changes clinical workflows: clinician access to data, report availability, patient interaction during visits, time-to-data, and workflow efficiency.
**Acceptance Criteria:**
- Current workflow documentation (how clinicians access CGM/pump data today)
- Proposed workflow documentation (how it changes with the framework)
- Workflow efficiency comparison
- Clinician training requirements identified
- No workflow change that increases risk of clinical error

### N-014: Accessibility and equity impact assessment
**Priority:** P1
**Category:** Validation
**Description:** Assess whether the framework creates equity gaps: does the portable record disadvantage low-income patients, elderly patients, patients with disabilities, patients without smartphones, or patients with limited literacy? Define mitigations.
**Acceptance Criteria:**
- Equity impact assessment across: income, age, disability, literacy, technology access
- Identified gaps with mitigation strategies
- Accessible alternatives for every framework component
- Cost barriers assessed and mitigated
- No patient should receive worse care because they cannot manage a portable record

---

## O. Local Simulation Environment

### O-001: Build CGM physiological glucose trace engine
**Priority:** P0
**Category:** Simulation — Patient Devices
**Description:** Implement a CGM engine that generates synthetic glucose traces using physiological models: meal absorption (Dalla Man/UVA-Padova model or simplified equivalent), insulin action curves (exponential decay), dawn phenomenon, exercise response, and sensor noise. Must produce 288+ readings/day at 5-min intervals. Configurable patient archetypes: child T1D, adolescent T1D, adult T1D well-controlled, adult T1D poorly-controlled, adult T2D, gestational diabetes, elderly T2D, consumer wellness (non-diabetic). Traces must be physiologically plausible — no glucose < 20 or > 600, rate-of-change within physiological limits (~4 mg/dL/min max sustained). Validate synthetic traces against published CGM datasets (Ohio T1DM, REPLACE-BG) for statistical similarity (mean, SD, TIR distribution).
**Acceptance Criteria:**
- Generates 288 readings/day per simulated patient
- 8 configurable patient archetypes with distinct glucose profiles
- Sensor noise model calibrated per manufacturer MARD specs (Dexcom G7 ~8.2%, Libre 3 ~7.9%, Guardian 4 ~8.7%)
- Sensor failure injection: signal loss, compression lows, early termination at configurable rates
- Sensor warmup simulation (30 min – 24 hr depending on model)
- Sensor drift over wear period
- Deterministic output given same random seed
- Runs entirely in-process, no external dependencies beyond NumPy/SciPy

### O-002: Build insulin pump engine
**Priority:** P0
**Category:** Simulation — Patient Devices
**Description:** Implement a pump engine generating insulin delivery events: basal rates (programmed and temporary), bolus deliveries (normal, extended, correction), reservoir tracking, infusion set changes, occlusions, and alarms. Configurable pump models: Tandem t:slim X2 (300U reservoir, 0.001U increment), Omnipod 5 (200U pod, 72h wear), MiniMed 780G (300U, auto mode). Pump responds to AID algorithm commands in closed-loop mode and manual inputs in open-loop mode.
**Acceptance Criteria:**
- Generates all event types: basal, temp basal, bolus (normal/extended/correction), suspend, resume, reservoir change, set change, occlusion, alarm
- Reservoir depletion tracked realistically
- Occlusion and failure injection at configurable rates
- Delivery delay modelling (bolus delivery takes time proportional to dose)
- Deterministic given same seed

### O-003: Build AID algorithm stub
**Priority:** P0
**Category:** Simulation — Patient Devices
**Description:** Implement a simplified closed-loop algorithm that receives glucose readings, calculates insulin-on-board (IOB), adjusts basal rates, and recommends corrections. Not production-grade — sufficient to generate realistic algorithm decision data: predicted glucose (30/60/90 min horizons), basal adjustment magnitude, auto-bolus amounts, mode transitions (auto→manual→auto), and IOB tracking. Configurable aggressiveness, target range (e.g., 100–120 mg/dL), and insulin sensitivity factor.
**Acceptance Criteria:**
- Processes each CGM reading within simulated time constraints
- Generates all AID output data types: predictions, adjustments, mode changes, IOB
- Responds to meals (increased insulin demand) and exercise (decreased demand)
- Mode exit on safety conditions (prolonged high glucose, sensor loss)
- Algorithm state persists across simulated device disconnections

### O-004: Build connected insulin pen engine
**Priority:** P1
**Category:** Simulation — Patient Devices
**Description:** Implement a pen engine generating injection events: dose amount, timestamp, pen serial number, cartridge info, temperature. Configurable pen models: NovoPen 6 (basal), Echo Plus (rapid-acting), Lilly Tempo. Injections timed around meals and corrections per patient profile.
**Acceptance Criteria:**
- Injection events at meal times and correction times
- Dose amounts realistic per patient profile (e.g., 4–15U bolus, 10–40U basal)
- Pen serial and cartridge tracking
- Missed dose simulation at configurable rate

### O-005: Build simulated phone/app layer
**Priority:** P0
**Category:** Simulation — Phone/App
**Description:** Implement the phone/app layer that receives data from simulated devices via in-process message passing (simulating BLE), runs the AID algorithm stub, maintains a local cache with configurable retention, and uploads data to the simulated manufacturer relay via localhost HTTP. Must simulate: app restart (cache recovery), phone reboot (state recovery), and connectivity loss (offline queuing with batch upload on reconnect).
**Acceptance Criteria:**
- Receives device data via in-process messaging (no actual BLE)
- Local cache persists across simulated app restarts
- Configurable upload schedule: immediate, batched (5 min, 1 hr)
- Offline mode: data queues locally, batch uploads on reconnect
- Real-time therapeutic stream isolation: burn commands from relay never affect app-layer therapeutic data
- Upload to relay via REST on localhost

### O-006: Build manufacturer relay — local HTTP server
**Priority:** P0
**Category:** Simulation — Manufacturer Relay
**Description:** Implement the manufacturer relay as a local HTTP server (FastAPI or Flask on localhost, configurable port). Receives data uploads from simulated phone/app via REST API. API shape compatible with Dexcom API v3 request/response format as reference model. Serves as the hub connecting World Classifier, Report Generator, Burn Scheduler, Burn Executor, and Audit Logger.
**Acceptance Criteria:**
- Runs on localhost, configurable port (default 8080)
- REST API: POST /api/v1/upload (receive data), GET /api/v1/status (burn queue status), POST /api/v1/burn/propagate (send burn signal to third-party)
- No external network calls — fails loudly if any component attempts external access
- Startup in <2 seconds
- Handles concurrent uploads from multiple simulated patients

### O-007: Build World Classifier
**Priority:** P0
**Category:** Simulation — Manufacturer Relay
**Description:** Implement the World Classifier that receives incoming data items and classifies each into exactly one of the six Typed Worlds based on data type. Classification rules defined in a YAML policy file, hot-reloadable without restart. Every classification decision logged with rationale. Unclassifiable items default to most restrictive burn schedule and generate a warning.
**Acceptance Criteria:**
- Classifies every data item within 100ms of receipt
- Policy file (YAML) maps data types to worlds
- Hot-reload: change policy file → classifier picks up changes without restart
- Unclassified data → most restrictive burn + warning in audit log
- Classification audit trail: item ID, data type, assigned world, policy rule matched, timestamp

### O-008: Build Typed World data stores
**Priority:** P0
**Category:** Simulation — Manufacturer Relay
**Description:** Implement six physically separate data stores (one per Typed World) using SQLite. Each world has its own database file in a dedicated directory. Physical separation ensures world isolation is architectural, not just logical. Schema per world tailored to its data types.
**Acceptance Criteria:**
- Six separate SQLite database files: rt_therapeutic.db, clinical_review.db, device_maintenance.db, research.db, patient.db, third_party.db
- Each DB in its own subdirectory
- Schema per world: columns match the data types that world accepts
- Insert into wrong world rejected by classifier (not just by schema)
- DB files inspectable with standard SQLite tools for debugging

### O-009: Build Report Generator
**Priority:** P0
**Category:** Simulation — Manufacturer Relay
**Description:** Implement a report generator that produces AGP-style clinical reports from raw glucose data in the Clinical Review world. Report includes: median glucose, GMI, CV, time-in-range breakdown (very low <54, low 54–69, in-range 70–180, high 181–250, very high >250 mg/dL), daily glucose profiles (percentile curves). Reports output as JSON (machine-readable) and optionally HTML (human-readable). Reports delivered to both simulated clinician endpoint and simulated portable record. Report delivery must be confirmed before raw data becomes burn-eligible.
**Acceptance Criteria:**
- AGP report from 14 days of CGM data
- All standard CGM metrics computed correctly
- Report delivered to clinician endpoint + portable record
- Delivery confirmation received before raw data burn eligibility
- Report output: JSON primary, HTML optional
- Sensor gaps correctly handled (no interpolation across gaps >30 min)

### O-010: Build Burn Scheduler
**Priority:** P0
**Category:** Simulation — Manufacturer Relay
**Description:** Implement the burn scheduling engine that tracks every data item's lifecycle: received → classified → stored → (report generated if applicable) → delivery confirmed → burn eligible → burn queued → burn executed → burn verified. Burn eligibility rules per world defined in config: Clinical Review = 14–90 days after receipt AND portable record delivery confirmed; Device Maintenance = on device replacement event; Research = on consent withdrawal or programme completion. Dashboard-queryable state for every item.
**Acceptance Criteria:**
- Tracks millions of data items (at scale scenario: 100 patients × 365 days × 288 readings = ~10.5M items)
- Burn eligibility check runs every simulation tick
- Eligibility requires: world classification + world-specific trigger satisfied + no holds/blocks
- States: pending_classification, classified, report_pending, delivery_pending, delivery_confirmed, burn_eligible, burn_queued, burn_executing, burn_complete, burn_failed
- Per-item state queryable via API and dashboard
- Legal hold flag suspends burn without losing queue position

### O-011: Build Burn Executor
**Priority:** P0
**Category:** Simulation — Manufacturer Relay
**Description:** Implement the burn executor that performs actual data destruction from world data stores. Supports multiple configurable mechanisms: simple DELETE, overwrite-then-delete, and cryptographic erasure (per-item encryption key destruction). After burn, verification step attempts to read the data — must fail. Generates audit log entry with: item ID, world, trigger, mechanism, timestamp, verification result (but NOT data content). Failed burns retried with exponential backoff (3 attempts max), then marked failed with alert.
**Acceptance Criteria:**
- Burns data from the correct world database
- Post-burn read verification (must return empty/error)
- Audit record for every burn (success or failure)
- Retry: 3 attempts with exponential backoff
- After max retries: mark failed, generate alert
- Burn executor isolated from real-time therapeutic data (separate process/thread)

### O-012: Build Audit Logger
**Priority:** P0
**Category:** Simulation — Manufacturer Relay
**Description:** Implement an append-only, hash-chained audit log recording every significant event: data receipt, classification, world storage, report generation, delivery attempt, delivery confirmation, burn scheduling, burn execution, burn verification, third-party propagation, custody changes. Each entry includes SHA-256 hash of previous entry. Log stored as JSON Lines file. Queryable by: data item ID, world, event type, time range, patient ID.
**Acceptance Criteria:**
- Append-only: no modification or deletion of entries during simulation
- Hash chain: each entry includes hash of previous entry
- Hash chain verifiable end-to-end
- Query API: filter by item ID, world, event type, time range, patient ID
- Log file human-readable (JSON Lines)
- Tamper detection: if any entry modified, hash chain breaks

### O-013: Build simulated third-party apps (3 stubs)
**Priority:** P1
**Category:** Simulation — Third-Party
**Description:** Implement three third-party app stubs, each running as a separate Flask micro-instance on different localhost ports:
- **App A (Fitness):** Receives glucose data via GET from relay API, stores in local SQLite, re-shares with a simulated sub-processor (4th party). Implements burn endpoint.
- **App B (Clinical):** Receives glucose + insulin data, generates simple recommendations (e.g., "consider lower basal"), stores in local SQLite. Implements burn endpoint.
- **App C (Aggregator):** Receives data from multiple simulated patients, produces population statistics. Implements burn endpoint.
Each app has configurable burn compliance behaviour: compliant (burns on signal), delayed (burns after configurable delay), non-compliant (refuses to burn — for testing escalation).
**Acceptance Criteria:**
- Three independent processes on different ports
- Each has its own SQLite data store
- Each implements POST /burn endpoint
- App A re-shares to sub-processor; burn must propagate through chain
- Configurable compliance: instant, delayed, or refuse
- Data stores inspectable to verify burn
- Non-compliant app triggers escalation in relay

### O-014: Build simulated portable record (Patient Vault)
**Priority:** P0
**Category:** Simulation — Portable Record
**Description:** Implement the portable record as an encrypted local directory. Receives data deliveries from manufacturer relay. Data encrypted at rest with AES-256-GCM using a patient-specific key. Sends signed delivery confirmations back to relay (hash of received data + patient key signature). Supports: browse data, export (JSON/CSV), share with simulated clinician, patient-initiated selective burn of own data. Simulates "loss" scenario (directory deleted) to test relay behavior (should queue, not burn undelivered data).
**Acceptance Criteria:**
- Encrypted local directory per patient (AES-256-GCM)
- Delivery confirmation: signed hash sent to relay
- Browse/query via CLI or local web UI
- Patient-initiated burn: select data by type/date range, confirm, irreversible delete + key destruction
- Loss simulation: delete directory → relay detects missing confirmation → queues data → patient creates new record → data re-delivered
- Export to JSON and CSV

### O-015: Build simulation clock controller
**Priority:** P0
**Category:** Simulation — Control Plane
**Description:** Implement a virtual clock that drives all simulation time. All components must derive timestamps from this clock, never from the system clock. Configurable acceleration: 1x (real-time), 60x (1 hour = 1 minute), 1440x (1 day = 1 minute), 10080x (1 week = 1 minute), up to 10000x. Controls: pause, resume, step-forward (advance by N ticks), jump-to-time. All components register with the clock and advance synchronously — no component gets ahead or behind.
**Acceptance Criteria:**
- All timestamps in all components from virtual clock
- Acceleration up to 10,000x without skipping events (every CGM reading generated)
- Pause mid-simulation without data loss or state corruption
- Step-forward: advance exactly N ticks, then pause
- Jump-to-time: advance to specific timestamp, processing all intermediate events
- Clock drift between components: zero (synchronous advancement)

### O-016: Build scenario runner engine
**Priority:** P0
**Category:** Simulation — Control Plane
**Description:** Implement a scenario runner that loads declarative YAML scenario files and orchestrates the simulation. Each scenario specifies: patient profiles, device configurations, event schedule (meals, sensor changes, consent changes, failures), simulation duration, time acceleration, and expected outcomes (assertions). Runner initializes all components, starts the clock, injects events at scheduled times, and runs assertion engine at completion. Produces pass/fail report with detailed failure diagnostics.
**Acceptance Criteria:**
- Loads YAML scenario files
- Initializes all simulation components per scenario config
- Injects events at scheduled simulation times
- Runs to completion or timeout
- Executes all assertions and produces pass/fail report
- Deterministic: same YAML + same seed = identical results
- Custom scenarios composable from primitives
- Exit code 0 on pass, 1 on fail (CI-compatible)

### O-017: Implement SCN-001 — Happy Path scenario
**Priority:** P0
**Category:** Simulation — Scenarios
**Description:** Single patient (adult T1D, well-controlled), Dexcom G7 CGM + Tandem t:slim X2 pump with Control-IQ AID. 90 simulated days. Normal operation: glucose readings generated, insulin delivered, data uploaded to relay, classified into worlds, AGP report generated at day 14/28/42/56/70/84, reports delivered to portable record, raw data burned after delivery confirmation, no third-party sharing. Assertions: all burns executed on schedule, portable record contains all reports + raw data, zero data remains in relay Clinical Review world after burn, audit log complete and hash-chain intact.
**Acceptance Criteria:**
- Scenario completes without errors at max acceleration in <5 minutes
- All assertions pass
- Portable record contains: 6 AGP reports + all raw glucose data + all insulin delivery data
- Relay Clinical Review world: empty after all burns
- Audit log: unbroken hash chain, every data item traceable from receipt to burn

### O-018: Implement SCN-002 — Sensor Transition scenario
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** Patient replaces CGM sensor at day 10 of 14-day simulation. Warmup period on new sensor (2 hours for G7). Verify: data gap during warmup represented correctly in reports, no data loss during transition, sensor metadata (old sensor serial, new sensor serial) correctly tracked in Device Maintenance world, old sensor metadata burns on replacement.
**Acceptance Criteria:**
- Warmup gap visible in AGP report
- No interpolation across warmup gap
- Old sensor metadata burned from Device Maintenance world
- New sensor metadata stored correctly
- Continuous glucose trace resumes after warmup

### O-019: Implement SCN-003 — Consent Revocation scenario
**Priority:** P0
**Category:** Simulation — Scenarios
**Description:** Patient shares glucose data with App A (fitness) for 30 days. At day 15, patient revokes consent. Burn-propagation signal sent from relay to App A. App A burns data and sends confirmation. App A's sub-processor also burns. Verify: App A data store empty for this patient, sub-processor data store empty, relay audit log records propagation chain, remaining data in relay unaffected.
**Acceptance Criteria:**
- Burn-propagation signal sent within 1 simulated hour of revocation
- App A confirms burn within 72 simulated hours
- Sub-processor confirms burn within 72 simulated hours after App A propagation
- All data stores verified empty for this patient at these apps
- Data in relay (other worlds) unaffected

### O-020: Implement SCN-004 — Non-Compliant App scenario
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** Same as SCN-003, but App A is configured to refuse burn. Verify escalation: relay detects non-compliance after SLA timeout, warning issued, API access rate-limited, second notice, API access revoked. Audit log records full escalation chain.
**Acceptance Criteria:**
- App A refuses burn endpoint
- Relay detects SLA violation (72 simulated hours)
- Escalation sequence: warning → rate limit → revocation
- Audit log records each escalation step
- Patient notified of non-compliance

### O-021: Implement SCN-005 — Portable Record Loss scenario
**Priority:** P0
**Category:** Simulation — Scenarios
**Description:** At day 30 of 60-day simulation, patient's portable record directory is deleted. Relay attempts delivery confirmation for new data — no response. Relay queues data (does NOT burn unconfirmed data). At day 35, patient creates new portable record. Relay re-delivers queued data to new record. New record sends confirmations. Burns resume for confirmed data.
**Acceptance Criteria:**
- Relay detects missing confirmation
- Data queued, not burned, during record outage (days 30–35)
- New portable record receives all queued data
- Confirmations received; burns resume
- No data lost during outage period
- Audit log records the entire outage/recovery sequence

### O-022: Implement SCN-006 — Offline Period scenario
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** Patient goes offline for 48 simulated hours (phone in airplane mode). CGM data accumulates on simulated phone (576 readings). Patient reconnects. Batch upload to relay. Burn timers start from upload time (not from reading generation time). Reports generated from the full dataset including offline period.
**Acceptance Criteria:**
- 576 readings queued on phone during offline
- Batch upload completes on reconnect
- Burn timers based on upload receipt, not reading timestamp
- Reports include offline-period data seamlessly
- No data loss during offline period

### O-023: Implement SCN-007 — Paediatric Transition scenario
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** Simulates 10 years (accelerated). Child patient starts at age 8 with parent as full custodian. At age 14 (simulated year 6), transitions to Phase 2 (shared authority): adolescent can restrict parent access to historical data, parent retains real-time alerts. At age 18 (simulated year 10), transitions to Phase 3 (exclusive authority): young adult gains full control. Young adult burns all data from ages 8–14. Verify: access controls change correctly at each phase, parent loses historical access at Phase 2, parent loses all access at Phase 3, parental-era data successfully burned.
**Acceptance Criteria:**
- Phase 1→2 transition at configured age (14)
- Parent access restricted to real-time only at Phase 2
- Phase 2→3 transition at configured age (18)
- Parent access fully revoked at Phase 3
- Young adult burns parental-era data → data irrecoverable
- Audit log records all transitions and burns

### O-024: Implement SCN-008 — Consumer Wellness scenario
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** Non-diabetic consumer using Dexcom Stelo. Zero-retention default. CGM data flows to relay, is displayed (simulated), then immediately burned from relay. No data persists in manufacturer relay. Portable record receives data only if consumer opted in (in this scenario: no opt-in). After 30 days, verify: relay holds zero data for this consumer, no reports generated, no third-party sharing.
**Acceptance Criteria:**
- Relay receives data → immediately burns (no world classification needed beyond burn)
- Zero data in any relay world after each burn cycle
- No reports generated (no clinical relationship)
- No third-party data sharing
- Consumer's real-time display unaffected by burn

### O-025: Implement SCN-009 — Emergency Burn scenario
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** At day 5 of 7-day simulation, patient triggers emergency burn. All data across all worlds in relay burned within 1 simulated hour. Burn-propagation signals sent to all third-party apps simultaneously. Verify: complete data destruction across all relay worlds, all third-party apps confirm burn, audit log records emergency event, real-time therapeutic stream unaffected.
**Acceptance Criteria:**
- Emergency burn completes within 1 simulated hour
- All six world databases empty for this patient
- All third-party apps receive propagation signal
- Compliant apps confirm burn
- Real-time therapeutic stream continues uninterrupted
- Audit log records emergency trigger, execution, and verification

### O-026: Implement SCN-010 — Multi-Device Patient scenario
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** Patient using Dexcom G7 (CGM) + Tandem t:slim X2 (pump) + NovoPen 6 (pen). Data from three device engines flows through phone/app layer to relay. Relay classifies data from all three sources. Integrated report generated combining CGM + pump + pen data. All sources subject to burn schedules independently.
**Acceptance Criteria:**
- Three device engines running concurrently for one patient
- All data correctly classified regardless of source
- Integrated report shows glucose + insulin delivery (pump + pen combined)
- Burn schedules applied per data type, not per device
- Portable record receives integrated dataset

### O-027: Implement SCN-015 — Concurrent Multi-Patient scenario
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** 100 simulated patients generating data simultaneously for 30 days. Mixed device profiles. Verify burn scheduler handles load without skipping, delaying, or misattributing burns. Each patient's data isolated — no cross-contamination.
**Acceptance Criteria:**
- 100 patients × 30 days × 288 readings = ~864,000 CGM data items
- All burns executed within SLA
- Zero cross-patient data contamination
- System completes in <15 minutes on standard laptop
- Memory usage stays bounded (no leaks)

### O-028: Implement SCN-020 — Full Lifecycle Stress Test
**Priority:** P1
**Category:** Simulation — Scenarios
**Description:** 50 patients, 365 simulated days, all device types, all event types interleaved randomly: sensor changes, consent grants/revocations, offline periods, third-party sharing, paediatric transitions, emergency burns, legal holds, burn failures. Random event injection from seed. Comprehensive assertion suite covering all 10 assertion types.
**Acceptance Criteria:**
- Completes in <30 minutes on standard laptop
- All 10 assertion types pass
- Zero data leakage
- Zero cross-patient contamination
- Audit log hash chain intact across 365 days
- Burn scheduler performance: no items overdue by >1 simulated day

### O-029: Build simulation dashboard (local web UI)
**Priority:** P1
**Category:** Simulation — Control Plane
**Description:** Implement a local web UI served on localhost (static HTML/JS, no npm/webpack/framework dependency) providing real-time visualization of the simulation. Views: (1) live data flow (readings → classification → storage → report → delivery → burn), (2) per-data-item lifecycle (click to see full journey), (3) world occupancy over time (line chart per world — should trend downward as burns execute), (4) burn queue (pending, next, overdue, failed), (5) third-party app state (data held, pending propagation, compliance), (6) portable record state (received, confirmed, patient-initiated burns), (7) audit log viewer with filter/search.
**Acceptance Criteria:**
- Served by Python HTTP server, no external CDN or API
- Vanilla JS + lightweight charting library (bundled locally)
- Auto-refreshes during simulation (WebSocket or polling)
- Responsive to time acceleration (updates faster at higher acceleration)
- All views functional with 100-patient simulation data
- Dashboard is read-only (does not modify simulation state)

### O-030: Build validation and assertion engine
**Priority:** P0
**Category:** Simulation — Control Plane
**Description:** Implement the automated assertion engine that validates simulation correctness after each scenario. Ten core assertion types:
1. **Burn completeness:** every burn-eligible item has been burned (query all data stores)
2. **Portable record completeness:** every patient-destined item delivered and present
3. **No data resurrection:** no burned item reappears anywhere at any later time
4. **Burn-propagation completeness:** every propagation signal resulted in confirmed burn or documented escalation
5. **World isolation:** no item ever stored in wrong world
6. **Real-time stream isolation:** zero burn-caused latency or data loss in therapeutic stream
7. **Audit chain integrity:** hash chain unbroken first-to-last
8. **Timing:** all burns within SLA
9. **Report delivery:** every report delivered to clinician + portable record before raw data burn
10. **Custody transition:** access controls correct at each phase (paediatric scenarios)
**Acceptance Criteria:**
- All 10 assertions implemented as composable pytest fixtures
- Each assertion produces structured pass/fail output with failure details
- Assertions run in <30 seconds even for stress test scenarios
- Any single assertion can be run independently
- CI-compatible exit codes

### O-031: Define YAML scenario specification format
**Priority:** P0
**Category:** Simulation — Control Plane
**Description:** Design and document the declarative YAML format for scenario files. Must support: patient profiles (demographics, device config, condition), event schedule (timestamped events: meals, sensor changes, consent changes, failures, custody transitions), simulation parameters (duration, acceleration, seed), third-party app configuration (which apps, compliance mode), and expected outcomes (which assertions to run, custom thresholds).
**Acceptance Criteria:**
- YAML schema documented with JSON Schema for validation
- All 20 pre-built scenarios expressible in this format
- Custom scenarios composable from documented primitives
- Schema validates before simulation starts (fail-fast on invalid scenario)
- Example scenarios included as reference

### O-032: Implement network isolation enforcement
**Priority:** P0
**Category:** Simulation — Infrastructure
**Description:** The simulation must enforce that zero external network calls are made by any component. Implement a network isolation layer that intercepts and blocks any non-localhost network access, failing loudly with a descriptive error. This ensures the simulation is fully local and prevents accidental data leakage to real manufacturer APIs.
**Acceptance Criteria:**
- All non-localhost network calls blocked
- Blocked calls raise an exception with: component name, destination, and explanation
- Enforcement works on macOS, Linux, and Windows
- Cannot be silently bypassed by simulation components
- Enforcement active by default, disable only via explicit flag (for integration testing)

### O-033: Implement simulation reproducibility guarantees
**Priority:** P0
**Category:** Simulation — Infrastructure
**Description:** Same scenario YAML + same random seed must produce identical outputs across runs, across platforms (macOS/Linux/Windows), and across Python versions (3.11+). All sources of non-determinism must be controlled: random number generation, dictionary ordering, thread scheduling, floating-point precision, file system ordering.
**Acceptance Criteria:**
- Reproducibility test: run SCN-001 twice with same seed → byte-identical audit logs
- Cross-platform: same outputs on macOS and Linux (Windows best-effort)
- All randomness via seeded numpy.random.Generator
- No reliance on dict ordering, filesystem ordering, or thread scheduling for correctness
- Floating-point: deterministic rounding strategy documented

### O-034: Build simulation CLI
**Priority:** P1
**Category:** Simulation — Infrastructure
**Description:** Implement the command-line interface for the simulation: `python -m chamber_sentinel_sim run <scenario.yaml> [--seed N] [--acceleration N] [--output-dir DIR] [--dashboard] [--verbose]`. Also: `python -m chamber_sentinel_sim list-scenarios` (list pre-built scenarios), `python -m chamber_sentinel_sim validate <scenario.yaml>` (validate scenario file without running), `python -m chamber_sentinel_sim report <output-dir>` (generate assertion report from completed simulation output).
**Acceptance Criteria:**
- `pip install -e .` installs the package
- `python -m chamber_sentinel_sim run SCN-001.yaml` runs the happy path
- `--seed` sets random seed for reproducibility
- `--acceleration` overrides scenario's default acceleration
- `--output-dir` specifies where simulation state and logs are written
- `--dashboard` launches local web UI during simulation
- Exit code 0 = all assertions pass, 1 = any assertion fails

### O-035: Implement per-world burn verification testing
**Priority:** P0
**Category:** Simulation — Testing
**Description:** For each of the six Typed Worlds, implement specific burn verification tests: (1) Real-Time Therapeutic: verify data never persists in relay cloud, never subject to burn (it was never there). (2) Clinical Review: verify raw data burns after report delivery confirmation, report itself persists in portable record. (3) Device Maintenance: verify data burns on device replacement event. (4) Research: verify data burns on consent withdrawal. (5) Patient: verify patient controls retention/burn. (6) Third-Party: verify burn-propagation cascade.
**Acceptance Criteria:**
- Dedicated test suite per world (6 test modules)
- Each test creates data, triggers burn condition, verifies destruction
- Cross-world contamination checked in every test
- Tests run in <60 seconds total

### O-036: Implement cryptographic erasure burn mechanism
**Priority:** P1
**Category:** Simulation — Burn
**Description:** Implement the cryptographic erasure burn mechanism as an option alongside simple deletion. Each data item encrypted with a unique key (or per-patient-per-world key). Burn = destroy the key. Verify: encrypted data remains on disk but is irrecoverable without key. This demonstrates the most secure burn mechanism for the architecture.
**Acceptance Criteria:**
- Per-patient-per-world encryption key hierarchy
- Data encrypted at rest with derived key
- Burn operation: delete key from key store
- Post-burn verification: data file exists but decryption fails
- Key store separate from data store
- Key destruction logged in audit trail

### O-037: Implement legal hold simulation
**Priority:** P1
**Category:** Simulation — Burn
**Description:** Implement legal hold functionality in the burn scheduler. A hold is placed on specific data items or a patient's entire dataset. While held, burn is suspended — items remain in burn queue but execution is blocked. Hold can be time-limited or indefinite. When hold is lifted, burns resume from where they left off. Verify: held data not burned during hold, burns execute correctly after hold lifted, hold does not become a mechanism for indefinite retention (alerts if hold exceeds threshold, e.g., 1 simulated year).
**Acceptance Criteria:**
- Hold placed via API: POST /api/v1/hold {patient_id, scope, reason, duration}
- Burn suspended for held items
- Hold status visible in dashboard and audit log
- Hold lifted: burns resume within next burn cycle
- Alert if hold exceeds 1 simulated year
- Hold cannot be placed on Real-Time Therapeutic world (nothing to hold)

### O-038: Implement burn-propagation protocol between relay and third-party stubs
**Priority:** P0
**Category:** Simulation — Third-Party
**Description:** Implement the full burn-propagation protocol: relay sends POST /burn to third-party app with {patient_id, data_scope, burn_deadline, verification_required}. App acknowledges receipt, executes burn, sends confirmation with burn verification hash. Relay tracks: signal sent, acknowledged, burn confirmed, or SLA violated. For App A's sub-processor: App A must propagate burn downstream and collect sub-processor confirmation before confirming to relay.
**Acceptance Criteria:**
- Protocol fully implemented between relay and all 3 apps
- Full chain: relay → App A → sub-processor, with confirmations flowing back
- SLA tracking per propagation signal
- Non-compliance detection and escalation
- Audit log records full propagation chain
- Protocol specification documented (reusable for real implementation)

### O-039: Implement simulation output directory structure
**Priority:** P1
**Category:** Simulation — Infrastructure
**Description:** Define and implement a standardized output directory structure for each simulation run. All state, logs, data stores, reports, and assertion results written to a single output directory that can be archived, shared, or re-analyzed.
**Acceptance Criteria:**
- Output directory structure:
  ```
  output/<run-id>/
    config/          # Copy of scenario YAML + config
    relay/           # Relay world databases
    portable_record/ # Patient vault(s)
    third_party/     # App A/B/C databases
    audit/           # Audit log (JSON Lines)
    reports/         # Generated clinical reports
    assertions/      # Assertion results (pass/fail + details)
    dashboard/       # Dashboard snapshot (optional)
    metadata.json    # Run metadata (seed, acceleration, timestamps, git hash)
  ```
- Entire directory self-contained and portable
- metadata.json includes everything needed to reproduce the run

### O-040: Implement glucose physiological model validation
**Priority:** P1
**Category:** Simulation — Validation
**Description:** Validate that synthetic glucose traces produced by the CGM engine are statistically comparable to real-world CGM data. Compare distributions of: mean glucose, SD, CV, TIR, time below range, time above range, and rate-of-change distribution against published CGM population studies. This is not a requirement for exact replication — it is a sanity check that the simulation produces physiologically plausible data.
**Acceptance Criteria:**
- Statistical comparison against ≥1 published CGM dataset
- Key metrics (mean, SD, TIR) within 2 standard deviations of published population means
- No physiologically impossible values (glucose <20 or >600, rate >8 mg/dL/min sustained)
- Rate-of-change distribution visually comparable to published distributions
- Validation report generated as part of simulation output

### O-041: Implement simulation performance benchmarking
**Priority:** P2
**Category:** Simulation — Infrastructure
**Description:** Benchmark simulation performance across scenarios and configurations. Establish baseline performance on reference hardware (M1 MacBook Air, 16GB RAM). Track performance across code changes to detect regressions.
**Acceptance Criteria:**
- Benchmark suite covering: SCN-001 (single patient, 90 days), SCN-015 (100 patients, 30 days), SCN-020 (50 patients, 365 days)
- Metrics: wall-clock time, peak memory, disk I/O, CPU utilization
- Performance targets: SCN-001 <5 min, SCN-015 <15 min, SCN-020 <30 min
- Benchmark results tracked in version control
- Regression detection: >20% slowdown triggers alert

### O-042: Implement multi-patient data isolation verification
**Priority:** P0
**Category:** Simulation — Testing
**Description:** In multi-patient scenarios, verify that no data from Patient A ever appears in Patient B's world stores, portable record, third-party app data, or audit trail. Cross-contamination would be a critical framework failure.
**Acceptance Criteria:**
- After multi-patient scenario, for each patient: query all data stores for data belonging to other patients → must return empty
- Portable records contain only their patient's data
- Third-party apps correctly partition data by patient
- Audit log entries correctly attributed to originating patient
- Test runs automatically in every multi-patient scenario

### O-043: Implement failure injection framework
**Priority:** P1
**Category:** Simulation — Testing
**Description:** Build a configurable failure injection framework that can introduce failures at any point in the data lifecycle: device failure, BLE drop, app crash, upload failure, classification error, storage failure, burn failure, delivery failure, propagation failure, portable record corruption. Failures configurable in scenario YAML: type, probability, duration, and recovery behavior.
**Acceptance Criteria:**
- Failure types: device_fail, ble_drop, app_crash, upload_fail, classify_error, storage_fail, burn_fail, delivery_fail, propagation_fail, vault_corrupt
- Each failure configurable: probability (0–1), duration (simulation ticks), recovery (auto/manual)
- Failures injected at runtime per scenario schedule
- System behavior during failure matches expected (graceful degradation, no data loss, no premature burn)
- Failures logged in audit trail

### O-044: Write simulation developer documentation
**Priority:** P1
**Category:** Simulation — Documentation
**Description:** Write developer documentation covering: architecture overview, component descriptions, how to run the simulation, how to author custom scenarios, how to add new device engines, how to add new assertion types, how to extend the dashboard, and how to interpret simulation output. Include architecture diagram, data flow diagrams, and example scenario walkthroughs.
**Acceptance Criteria:**
- README.md in simulation package root
- Architecture diagram (text-based, no external tool dependency)
- Getting started guide: install → run first scenario → view results in <5 minutes
- Scenario authoring guide with annotated examples
- Extension guide: adding a new device engine, adding a new assertion
- API reference for simulation control plane
- Troubleshooting section for common issues

---

*This issue list is derived from the Chamber Sentinel position paper (April 2026, Revised Draft) and the local simulation environment specification. Issues are analytical — they represent engineering requirements, validation needs, unresolved questions, and acknowledged gaps identified in the source document. Priorities are suggested and require stakeholder validation.*
