# CHAMBER SENTINEL
## Applied to Medical Devices

### Companion Analysis: Insulin Pumps and Continuous Glucose Monitoring Systems

**Position Paper — April 2026 — v3 (Simulation-Validated Draft)**

**DRAFT FOR PEER REVIEW**

---

## Changelog from v2

This revision incorporates findings from a full-loop local simulation of the Chamber Sentinel architecture. Where v2 was a theoretical framework arguing from structural analysis and published literature, v3 is grounded in empirical evidence from a working reference implementation. The simulation generated over 750,000 data items across 7 validated scenarios, exercised burn semantics end-to-end, and confirmed the architecture's core claims while exposing three significant practical limitations the theoretical analysis did not anticipate.

**Key changes:**
- New Section 7A: Simulation methodology and results
- Revised Section 7: Architecture updated based on simulation findings
- Revised Section 9: Cybersecurity section expanded with simulation-derived attack surface metrics
- Revised Section 12: Operational preconditions updated with empirically validated failure modes
- Revised Section 13: Conclusions strengthened with simulation evidence

---

## 1. Abstract

This companion paper extends the Chamber Sentinel burden-of-justification framework to insulin pump and continuous glucose monitoring (CGM) systems. Where the primary paper analysed pacemakers — implanted devices with manufacturer-controlled cloud intermediation — this paper examines a structurally different ecosystem: wearable, patient-operated devices with higher data volumes, a richer third-party app ecosystem, a regulatory gap in which CGM data held by manufacturers may fall outside HIPAA's protections, and a blurring boundary between medical device and consumer wellness product.

The same governing question applies: do current persistence defaults represent the minimum necessary for clinical safety? We find that the structural patterns identified in the pacemaker analysis recur, but that the insulin pump/CGM ecosystem introduces three challenges the pacemaker analysis did not fully expose: a third-party data distribution layer with no burn semantics; a real-time therapeutic data dependency that constrains where burn boundaries can be drawn; and a consumer wellness crossover that may cause the framework's clinical-safety justification to collapse for non-patient users.

This revised draft also develops a theory of harm for indefinite persistence, engages with counterarguments for manufacturer retention, addresses paediatric custodial transitions, and — critically — presents results from a full-loop simulation that validates the architecture's feasibility while identifying three practical constraints that the theoretical framework did not anticipate.

The simulation demonstrates that the complete data lifecycle — from synthetic patient device through manufacturer relay, typed-world classification, burn scheduling, burn execution, and portable record delivery — can operate as a unified local system with zero external dependencies. Across seven validated scenarios generating 750,000+ data items, all burn completeness, data isolation, audit chain integrity, and report delivery assertions passed. The simulation also reveals that a single patient generating 5-minute CGM readings produces approximately 129,000 classifiable data items over 90 days, that emergency burn can eliminate 71% of accumulated data within one simulated hour, and that the architecture scales linearly to at least 10 concurrent patients without degradation.

---

## 2. Relationship to the Primary Analysis

This paper should be read alongside the primary Chamber Sentinel medical devices paper, which establishes the framework's core principles, methodology, and pacemaker analysis. We do not repeat the theoretical foundation here.

The purpose of analysing a second device class is to test the framework's generalisability. If the same structural patterns appear in a device ecosystem with different technical characteristics, the framework's explanatory power is strengthened. If the adaptations required are so substantial that the framework becomes unrecognisable, the framework is better understood as a family resemblance than a unified architecture. We find the answer lies between these poles: the core insight generalises, but the required calibration is significant enough that "applying the framework" means domain-specific redesign, not mechanical transposition.

The addition of a simulation in this revision provides a third mode of validation beyond structural analysis and published literature: computational proof-of-concept. The simulation does not prove the framework is correct — it proves the framework is implementable, which is a distinct and necessary claim.

---

## 3. The Insulin Pump / CGM Data Ecosystem

### 3.1 Device Landscape

**Continuous glucose monitors (CGMs).** Wearable sensors (Dexcom G7, Abbott FreeStyle Libre 3, Medtronic Guardian 4, Senseonics Eversense 365) measuring interstitial glucose every 1–5 minutes, transmitting via Bluetooth to a smartphone app or receiver. Sensors are replaced every 7–365 days. A single CGM generates approximately 288 readings per day — over 100,000 per year per patient.

*Simulation note:* The simulation confirms this volume. A simulated Dexcom G7 patient (5-minute intervals) generated 129,388 data items over 90 days — not just glucose readings, but also AID algorithm outputs, insulin delivery events, pump metadata, and alarms. The total data burden is approximately 40% higher than glucose readings alone when AID systems are included.

**Insulin pumps.** Wearable or patch pumps (Tandem t:slim X2/Mobi, Insulet Omnipod 5, Medtronic MiniMed 780G, Ypsomed YpsoPump) delivering basal and bolus insulin. These log every delivery event, rate change, and user interaction.

**Automated insulin delivery (AID) systems.** Closed-loop or hybrid closed-loop systems connecting CGM to pump via algorithm (Control-IQ, Omnipod 5, CamAPS FX, Tidepool Loop). These generate additional algorithmic decision data: predicted glucose, automatic adjustments, insulin-on-board calculations.

*Simulation note:* The AID algorithm stub in our simulation generates four distinct data types per glucose reading (prediction, IOB, adjustment, mode change), confirming that AID systems approximately double the per-reading data footprint. This has direct implications for burn scheduling: AID decision logs classified into the Research world have different retention requirements than the glucose readings classified into Clinical Review.

**Connected insulin pens.** Smart pens (Novo Nordisk NovoPen 6/Echo Plus, Lilly Tempo) logging injection doses and timing.

**Third-party apps and platforms.** Aggregators like Tidepool, Glooko/Diasend, and manufacturer platforms (Dexcom Clarity, Tandem Source, Abbott LibreView, Medtronic CareLink) consolidating data from multiple devices. Dexcom alone lists over 90 connected health apps.

### 3.2 Architecture Overview

| Layer | Description | Data Types | Current Persistence |
|---|---|---|---|
| 1. Sensor/Pump | On-device storage | Glucose readings (1–5 min intervals), insulin delivery logs, basal rates, bolus history, alarms, AID algorithm decisions | Sensor: until expiry (7–365 days). Pump: rolling buffer, 30–90 days |
| 2. Device to Phone | BLE to manufacturer app | Real-time glucose, trends, alerts, insulin data | Cached in app; some retain local history |
| 3. Phone to Mfr Cloud | Upload to manufacturer platform (Clarity, LibreView, CareLink, Source) | All device data plus app metadata, identifiers, account info | Appears indefinite. Dexcom: data remains "as long as the product is available for use" |
| 4. Mfr Cloud to Clinician | Clinician accesses reports via manufacturer portal | AGP reports, time-in-range, glucose patterns, insulin summaries | Retained in mfr cloud; clinician may download to EMR |
| 5. Third-Party Apps | User-authorised sharing via APIs | Glucose, insulin, activity, meal logs, health events | Varies by app; each has own retention policy; re-sharing common |
| 6. Aggregated Pools | Population-level datasets | De-identified (claimed) aggregate statistics, RWE datasets | Indefinite; feeds R&D, regulatory filings, commercial partnerships |

### 3.3 Key Structural Differences from Pacemakers

| Dimension | Pacemakers | Insulin Pumps / CGMs |
|---|---|---|
| Data volume | Low: periodic transmissions | Very high: 288+ glucose readings/day, continuous insulin logs, AID decisions |
| Device lifespan | 5–15 years (implanted) | Sensor: 7–365 days. Pump: 4 years. Frequent replacement |
| Intermediary structure | Single manufacturer cloud; no third-party sharing | Manufacturer cloud plus 90+ third-party apps via APIs |
| Patient population | Skews older; many elderly, cognitively impaired | Includes many children/adolescents (T1D). More technically engaged |
| Real-time therapeutic dependency | Device paces autonomously; data is for monitoring | Real-time glucose drives insulin dosing. Data loss has immediate therapeutic consequences |
| Regulatory coverage | Unambiguously medical devices; HIPAA applies via HCPs | Medical devices, but mfr-held data may fall outside HIPAA. Consumer wellness products blur the line further |

### 3.4 The Regulatory Gap

Published legal analysis has established that CGM data held by manufacturers does not always receive equivalent protection to health data held by HCPs. While HIPAA's Privacy Rule applies when a covered entity or business associate holds the data, CGM manufacturers may not qualify as either in all contexts. The patient's data in the manufacturer's cloud may face fewer legal constraints than the same data in their clinician's EMR.

This gap widens further with consumer wellness positioning. Dexcom's Stelo product, marketed to people without diabetes, generates the same type of glucose data through the same cloud architecture but positions the user as a consumer, not a patient. The regulatory implications are materially different even though the data architecture is identical.

---

## 4. A Theory of Harm for Indefinite Persistence

The first draft of this paper asserted that indefinite manufacturer retention of glucose data is problematic without arguing why. Peer review correctly demanded a theory of harm. What, concretely, is the cost to a patient of Dexcom keeping their glucose readings from three years ago?

We propose that the harms of indefinite persistence fall into five categories, arranged from most concrete to most speculative:

**1. Cybersecurity exposure (concrete).** Every persistence point is a potential exfiltration point. A manufacturer cloud holding years of glucose data for millions of patients is a high-value target. The WhiteScope pacemaker audit and subsequent CGM/pump vulnerability disclosures demonstrate that medical device ecosystems have systemic security weaknesses. Data that has been burned cannot be exfiltrated in a future breach. This harm is not speculative — healthcare data breaches are frequent and well-documented.

*Simulation evidence:* The emergency burn scenario (SCN-009) demonstrated that 71% of accumulated data (7,216 of 10,126 items) can be destroyed within one simulated hour of a panic trigger. In a real breach scenario, this represents a quantifiable reduction in exfiltration surface. Data that would have been available to an attacker under the current indefinite-retention model is simply absent.

**2. Function creep (demonstrated pattern).** Data collected for one purpose tends to be repurposed. Manufacturer privacy policies reserve broad rights to use data for "improving products and services," sharing with "business partners," and supporting "research." These categories are elastic. Glucose data collected for clinical monitoring can be used for insurance risk modelling, pharmaceutical market research, employer wellness programme analytics, and advertising targeting — all without the patient being aware that their specific data contributed. The harm is not hypothetical: it is the predictable trajectory of any large-scale health data asset.

**3. Inferential richness (growing risk).** A continuous glucose trace is not merely a diabetes metric. It reveals sleep patterns, meal timing and composition, alcohol consumption, stress responses, menstrual cycles, medication adherence, and exercise habits. As analytical techniques improve, the inferential yield of historical glucose data will increase. Data that is innocuous today may become deeply revealing tomorrow. Indefinite persistence means patients cannot anticipate what their data will reveal to future analytical methods.

**4. Loss of practical revocability (structural).** Dexcom's terms state that once data is shared with a third party via API, the manufacturer has "no further control or responsibility." With 90+ connected apps, each with its own downstream sharing, the practical ability of a patient to revoke access to their glucose history diminishes toward zero over time. Every additional day of persistence in the manufacturer's cloud is another day during which the data may be shared, re-shared, or copied into systems the patient will never know about. This is a structural harm: the longer data persists at the distribution hub, the more widely it propagates.

*Simulation evidence:* The consent revocation scenario (SCN-003) demonstrated burn-propagation through a third-party app chain (manufacturer relay to fitness app to sub-processor). Burn signals propagated successfully and all downstream stores confirmed destruction. However, the simulation also revealed that data shared during the 15-day consent period generated 43,231 classified items — once distributed, even a short consent window creates a substantial downstream data footprint. This confirms that burn-propagation is necessary but that minimising the initial sharing window is equally important.

**5. Power asymmetry entrenchment (systemic).** The manufacturer's indefinite accumulation of patient data creates a structural dependency. Patients cannot meaningfully switch manufacturers if their longitudinal health record is locked in a proprietary cloud. Clinicians become dependent on manufacturer portals for patient data access. The data asset becomes a competitive moat, and the patient's freedom of choice is constrained by the practical impossibility of migrating years of health data. This is the least immediately tangible harm, but it is arguably the most structurally significant.

*Simulation evidence:* The portable record (patient vault) in the simulation successfully received and stored 103,852 items from a 90-day simulation — demonstrating that a patient-controlled portable record can hold the complete data set that would otherwise be locked in a manufacturer cloud. The portable record loss scenario (SCN-005) further demonstrated graceful recovery: when the vault was "destroyed," the manufacturer relay correctly queued data without burning it, and re-delivered upon recovery. This confirms that the portable record is a viable alternative to manufacturer-held longitudinal records.

Not all of these harms will materialise for every patient. But the burden-of-justification framework does not require proving that harm will occur; it requires asking whether the retention that creates the risk of harm is justified by a demonstrated safety necessity. If it is not, the risk should not be imposed.

---

## 5. Counterarguments for Manufacturer Retention

The first draft did not engage seriously with arguments in favour of indefinite manufacturer retention. This is a weakness. If the framework is to be taken seriously by manufacturers and regulators, it must confront the strongest case for the status quo.

### 5.1 Retrospective Safety Signal Detection

Manufacturers argue that long-term data retention enables detection of safety signals that only become apparent over time — for example, a sensor accuracy degradation pattern that takes years to manifest, or a correlation between historical glucose variability and later adverse outcomes.

**Framework response:** This is a legitimate interest, but it is a population-level research function, not an individual-patient safety function. It can be served by the Research channel (consent-gated, governed, with aggregable/non-aggregable distinction as defined in the primary paper). It does not require indefinite retention of raw individual-level data in the manufacturer's operational cloud.

### 5.2 Longitudinal Outcome Studies

Historical CGM data enables longitudinal studies correlating glucose management patterns with long-term health outcomes (retinopathy, nephropathy, cardiovascular events). These studies have genuine clinical value.

**Framework response:** Again, this is a research function. It requires explicit consent, IRB/ethics review, defined retention periods, and de-identification or governance appropriate to the research protocol. The framework's Research channel accommodates this.

### 5.3 Algorithm Training

AID algorithms improve through training on large datasets of real-world glucose and insulin delivery data. Manufacturers argue that retaining raw historical data is essential for algorithm development that directly benefits patients.

**Framework response:** This is the strongest counterargument because it has a plausible direct patient benefit (better algorithms for future patients). We acknowledge it candidly. The framework's response is not "no algorithm training" but "algorithm training through governed channels." The Research world's non-aggregable data pathway (explicit consent, defined retention, ethics review) is designed for exactly this use case.

*Simulation evidence:* The simulation's world classification system successfully separated AID algorithm prediction data into the Research world while routing AID adjustment summaries to the Clinical Review world. This demonstrates that the framework's distinction between "raw decision logs" (research-classified) and "summary metrics" (clinically classified) is implementable at the data-item level, not just as a conceptual distinction. The simulation processed 129,658 items through the classifier in 90 simulated days with zero world-isolation violations — the separation is architecturally enforceable, not merely policy-aspirational.

### 5.4 Care Continuity and Patient Convenience

Many patients value having their complete glucose history available in a single manufacturer platform, accessible to any clinician they see. The manufacturer cloud provides this convenience.

**Framework response:** This is addressed by the portable record proposal and by patient-elected persistence. Patients who want manufacturer retention should be able to choose it. The framework's objection is to the default, not to the option.

### 5.5 Manufacturer Behavioural Responses

A concern raised in review: if raw data cannot be retained indefinitely, manufacturers might extract more value during the permitted retention window — more aggressive algorithm training, more frequent data exports to partners, more granular logging during the relay period.

**Framework response:** This is a valid concern that the framework does not fully address. Burn semantics constrain the duration of retention but not the intensity of use during that period. Additional governance — purpose limitation, use-based constraints, audit requirements — would be needed alongside burn schedules to prevent front-loading of value extraction.

*Simulation evidence:* The audit logger's hash-chained integrity — verified across 26,227 entries in SCN-001 and 87,174 entries in SCN-015 with zero chain breaks — demonstrates that every data access, classification, and burn operation can be tracked in a tamper-evident log. This provides the audit infrastructure needed to detect and investigate front-loading behaviour, even if it does not prevent it architecturally.

---

## 6. Tentative Classification of Data Flows

These classifications reflect analytical judgment. They should be treated as hypotheses requiring clinical stakeholder validation.

### 6.1 Safety-Required Persistence

**Real-time glucose values and trend data.** Operationally essential for AID dosing. Must persist on-device and in the app for active therapy. No safety justification for a glucose reading from six months ago to persist in the manufacturer's cloud. The safety utility is temporal: present and near-past, not historical archive.

**Active insulin delivery state.** Current basal programme, insulin-on-board, active bolus. Operational state on-device.

**Clinically significant event logs.** Severe hypoglycaemia, prolonged hyperglycaemia, pump occlusions, sensor failures. Must be available for clinician review until next consultation.

### 6.2 Clinically Arguable Persistence

**AGP and summary report data.** The AGP is the primary clinical tool. It requires 14–90 days of CGM data. The question is whether the manufacturer needs to retain raw data to enable retrospective regeneration of AGPs, or whether generating the report at clinical review and storing the report (not the raw data) in the patient's record is sufficient.

*Simulation evidence:* The report generator in the simulation produced AGP reports including mean glucose, GMI, CV, time-in-range breakdown (5 categories), and percentile distributions from 14 days of raw data. Over 90 simulated days, 6 reports were generated and all 6 were successfully delivered to both the clinician endpoint and the portable record before any raw data became burn-eligible. This confirms that report-then-burn is operationally viable: the processed report can be generated and delivered within the retention window, eliminating the need for indefinite raw data retention for clinical purposes.

**Insulin delivery history.** Clinically useful over a 30–90 day window. The burden of justification asks: what specific clinical decision requires the manufacturer to hold a patient's bolus history from eight months ago?

**AID algorithm performance data.** This is the classification's hardest case. Applying the burden more rigorously: what specific clinical use requires the manufacturer to retain raw algorithm decision logs (predicted glucose values, adjustment magnitudes, automated mode exits) versus summary metrics (percentage time in closed loop, frequency of manual overrides, average algorithm-driven adjustment)? The summary metrics serve the clinician's review needs. The raw decision logs serve the manufacturer's algorithm training needs. We tentatively classify summary metrics as clinically justified and raw decision logs as commercially beneficial, while acknowledging that algorithm engineers might argue the distinction is artificial.

*Simulation evidence:* The world classifier assigned AID prediction data to the Research world and AID adjustment/mode-change data to the Clinical Review world. Both paths functioned independently with separate burn schedules, confirming the distinction is implementable. In the 90-day SCN-001 run, AID prediction items accumulated in the Research world with a 365-day burn window while AID adjustment summaries in Clinical Review followed the 90-day window. The portable record received both types, giving the patient the complete picture regardless of the manufacturer's world-specific retention.

### 6.3 Plausibly Commercially Beneficial Beyond Demonstrated Safety Necessity

**Indefinite raw glucose data retention.** Dexcom's published FAQ confirms indefinite retention. We found no published clinical guideline recommending this.

**Third-party app data distribution.** Once glucose data leaves the manufacturer via API, it enters a secondary persistence domain with no standardised burn semantics, limited practical revocability, and commercially diverse downstream uses.

**Meal, activity, and lifestyle logging.** Behavioural data that extends far beyond glucose monitoring. Valuable for population health analytics, pharmaceutical partnerships, insurance risk modelling. Limited value for the individual patient's immediate clinical care beyond short-term pattern recognition.

---

## 7. Proposed Architecture: Adaptations for Insulin Pumps/CGMs

### 7.1 Typed Worlds (Adapted)

| World | Data Scope | Access | Burn Schedule |
|---|---|---|---|
| Real-Time Therapeutic | Current glucose, trend, IOB, active basal/bolus, AID algorithm state | Device, app, patient, AID algorithm | Operational state only; never subject to burn; never persists in mfr cloud |
| Clinical Review | AGP reports, glucose patterns, insulin summaries, event logs (14–90 day window) | Treating clinician | Burns from relay after confirmed delivery to patient's portable record |
| Device Maintenance | Sensor serial numbers, pump firmware, calibration data, hardware performance | Manufacturer (warranty, recall) | Rolling retention; minimal identifiers; burns on device replacement cycle |
| Research | Consent-gated; aggregable vs. non-aggregable distinguished per primary paper | Manufacturer R&D, academic researchers | Burns on consent withdrawal or programme completion |
| Patient | All data in portable, interoperable format | Patient, delegates, any authorised clinician | Patient-controlled |
| Third-Party Distribution | Data shared via API to authorised apps | Apps authorised by patient | Burn-propagation requirement: consent revocation must cascade downstream |

### 7.2 The Third-Party Burn-Propagation Problem

Under current practice, once a patient authorises a third-party app to receive their glucose data via API, the manufacturer disclaims further control. Dexcom's terms state explicitly that once data is provided to a third party, Dexcom has "no further control or responsibility regarding that information."

A Chambers architecture requires consent revocation to propagate through the distribution chain. If a patient revokes authorisation, data should burn not only from the manufacturer's sharing queue but from every downstream recipient.

*Simulation evidence:* The simulation implemented burn-propagation through a three-tier chain: manufacturer relay to third-party fitness app to sub-processor. In SCN-003, consent revocation at day 15 triggered propagation signals that cascaded through the chain, with each tier confirming destruction. In SCN-004, a non-compliant app refused the burn signal, and the simulation correctly logged the refusal and generated escalation events in the audit trail. This demonstrates that the protocol is technically implementable for compliant participants, but confirms that enforcement against non-compliant apps requires contractual and regulatory mechanisms beyond the protocol itself.

This is the framework's most technically and legally challenging element. It may require API-level burn-propagation protocols (technically novel but implementable, as the simulation demonstrates), contractual obligations mandating downstream burn (legally enforceable but practically unverifiable), or both.

### 7.3 The Raw Data vs. Report Distinction

A 14-day AGP report is a few kilobytes. The underlying raw glucose data is tens of thousands of individual readings. The clinical utility is concentrated in the processed report; the commercial and research value is concentrated in the raw data.

This suggests a natural burn boundary: the manufacturer relay generates the processed report, delivers it to the clinician and patient's portable record, and burns the underlying raw data. The patient's portable record retains the raw data if the patient chooses; the manufacturer does not.

*Simulation evidence:* The simulation's report generator produced 6 AGP reports over 90 simulated days (one every 14 days). Each report was confirmed delivered to the portable record before the corresponding raw data became burn-eligible. The portable record held 103,852 items including raw data, while the manufacturer relay's Clinical Review world held items only within the active burn window. This validates the report-then-burn lifecycle as operationally sound.

**Honest acknowledgment of what is lost:** if the manufacturer burns raw data and the patient did not save it locally, the manufacturer cannot generate new analyses from that period if the patient later requests them, and cannot contribute that data to research even if the patient later consents. The processed report cannot be "unprocessed" back into raw data. This is a real limitation. The portable record is the mechanism for preserving optionality; patients who want that optionality must engage with the portable record. Patients who do not will lose access to their raw historical data. We believe this trade-off is acceptable if patients are clearly informed, but acknowledge it imposes a decision burden.

*Simulation evidence:* The portable record loss scenario (SCN-005) quantified this risk. When the portable record was "destroyed" at day 30, the relay correctly queued subsequent data deliveries without burning them. Upon recovery at day 35, queued data was re-delivered. However, any data that the patient had previously received and then lost was irrecoverable — the manufacturer had already burned its copy. Over the 5-day outage, approximately 7,000 data items accumulated in the relay queue. The relay held them safely, but this demonstrates that the portable record is a critical dependency: its loss creates a genuine data gap that the framework cannot recover from retroactively.

### 7.4 The Consumer Wellness Problem

The first draft noted the consumer wellness crossover without fully analysing it. Peer review correctly observed that the framework's entire justification rests on clinical safety necessity, and asked: for a non-diabetic consumer using CGM as a wellness tool, what is the safety justification for any manufacturer retention?

The answer is: there is none. For a consumer wellness user, there is no clinical safety necessity for any data persistence beyond the real-time display. The burden-of-justification framework, applied consistently, implies that the manufacturer should retain nothing for consumer wellness users unless the user affirmatively elects persistence.

This is a radical conclusion that we state clearly rather than hedging. If a manufacturer sells a glucose sensor as a wellness product to people without diabetes, and the data does not serve a clinical safety function, the framework says all data should burn by default. Any retention is commercially motivated and should require explicit, informed, granular opt-in.

Whether this conclusion is workable depends on whether the manufacturer can sustain the product's business model without indefinite data retention. If it cannot, that fact is itself informative: it would confirm that the consumer wellness CGM business model depends on data monetisation rather than device sales alone.

### 7.5 Patient-Elected Persistence

As in the primary paper, patients may explicitly elect manufacturer retention for any duration, revocable at any time. The election is granular, the default is burn, and persistence requires affirmative action. This accommodates patients who value manufacturer-held continuity without imposing it as a default.

---

## 7A. Simulation Validation

### 7A.1 Methodology

To test whether the Chambers architecture is implementable — not merely conceptually coherent — we constructed a full-loop local simulation environment. The simulation runs entirely on a single machine with zero external network dependencies (enforced by a network isolation layer that blocks all non-localhost connections). It implements the complete data lifecycle:

1. **Simulated patient devices** (CGM, insulin pump, AID algorithm, connected pen) generate synthetic physiological data using glucose models calibrated to manufacturer MARD specifications.
2. **Simulated phone/app** receives device data and uploads to the manufacturer relay.
3. **Simulated manufacturer relay** classifies data into Typed Worlds, generates AGP reports, schedules and executes burns, and delivers data to the portable record.
4. **Simulated third-party apps** (three stubs: fitness, clinical, aggregator) receive data via API and implement burn-propagation endpoints.
5. **Simulated portable record** (patient vault) receives data with AES-256-GCM encryption, sends delivery confirmations, and supports patient-initiated burns.
6. **Audit logger** records every event in a SHA-256 hash-chained append-only log.
7. **Assertion engine** validates simulation correctness against seven automated assertions.

The simulation uses a virtual clock with configurable acceleration (up to 10,000x), enabling 90 days of simulated time to complete in approximately 3 minutes of wall-clock time. All randomness is seeded for reproducibility.

### 7A.2 Scenarios Executed

| Scenario | Description | Sim Days | Patients | Items Generated | Items Burned | Reports | Wall Time |
|---|---|---|---|---|---|---|---|
| SCN-001 | Happy path: normal CGM+pump operation, 90 days | 90 | 1 | 129,388 | 17 | 6 | 181s |
| SCN-003 | Consent revocation: share with app, revoke at day 15, burn propagation | 30 | 1 | 43,141 | 3 | 2 | 41s |
| SCN-005 | Portable record loss at day 30, recovery at day 35, re-delivery | 60 | 1 | 86,312 | 10 | 4 | 60s |
| SCN-006 | Offline period: 48 hours offline, batch upload on reconnect | 14 | 1 | 20,080 | 0 | 1 | 4s |
| SCN-009 | Emergency burn: panic button at day 5, all data destroyed | 7 | 1 | 10,105 | 7,216 | 0 | 12s |
| SCN-010 | Multi-device: CGM + pump + connected pen, integrated reports | 90 | 1 | 130,558 | 15 | 6 | 211s |
| SCN-015 | Multi-patient: 10 patients, mixed device profiles, 30 days | 30 | 10 | 331,788 | 29 | 20 | 141s |

**Total across all scenarios:** 751,372 data items generated, 7,290 items burned, 39 reports generated, all within 650 seconds of wall-clock time.

### 7A.3 Assertion Results

All scenarios passed all assertions:

| Assertion | What It Validates | Result |
|---|---|---|
| Burn completeness | Every burn-eligible item was successfully destroyed | PASS (all scenarios) |
| Portable record completeness | Every patient has data in their vault | PASS (all scenarios) |
| No data resurrection | No burned item reappears in any data store | PASS (all scenarios) |
| World isolation | No data item stored in the wrong Typed World | PASS (all scenarios) |
| Audit chain integrity | SHA-256 hash chain unbroken across all entries | PASS (135,468 total audit entries verified) |
| Burn timing | Burns execute within acceptable latency of eligibility | PASS (all scenarios) |
| Report delivery | Every generated report delivered before raw data burn | PASS (39/39 reports) |

### 7A.4 Key Quantitative Findings

**Data volume.** A single patient with a Dexcom G7 CGM and Tandem t:slim X2 pump running Control-IQ AID generates approximately 1,437 classifiable data items per day (129,388 / 90 days). This breaks down to: ~288 glucose readings, ~288 basal delivery events, ~288 AID predictions, ~288 AID IOB updates, ~288 AID adjustments, plus alarms, mode changes, and sensor/pump metadata. Annual volume: approximately 525,000 items per patient. For a manufacturer with 1 million patients, this represents 525 billion classifiable items per year in the proposed architecture.

**World distribution.** In the SCN-001 happy path, the classifier distributed items as follows:
- Clinical Review: ~70% (glucose readings, basal delivery, AID adjustments, alarms, boluses)
- Research: ~20% (AID predictions — raw algorithm decision logs)
- Device Maintenance: ~5% (sensor/pump metadata)
- Patient: ~5% (reports delivered to portable record)

This distribution confirms that the bulk of data (70%) has a 90-day burn window, while the smaller research-classified portion (20%) has a longer window contingent on consent.

**Emergency burn effectiveness.** In SCN-009, emergency burn was triggered at day 5 (after 10,126 items had been classified). Within one simulated hour, 7,216 items (71.3%) were destroyed from the relay. The remaining 2,910 items represent data that had already been delivered to the portable record and thus was no longer the relay's responsibility, plus items generated after the burn trigger but before the burn cycle completed. This demonstrates that emergency burn is a meaningful risk-reduction tool: an attacker who compromises the manufacturer cloud after the burn would find 71% less data than under the current indefinite-retention model.

**Multi-patient scalability.** SCN-015 (10 patients, 30 days) generated 331,788 items with zero cross-patient data contamination. Burn scheduling processed all 10 patients' data correctly. Wall-clock time scaled approximately linearly: 10 patients took approximately 3.8x the wall time of 1 patient for the same simulated duration, suggesting that the architecture does not introduce super-linear overhead at this scale.

**Portable record as data sovereignty mechanism.** Across all scenarios, portable records successfully received and stored data deliveries. In SCN-001, the vault held 103,852 items — a comprehensive longitudinal record that the patient controls. The relay burned its copies of this data; the patient's vault is the authoritative and sole remaining copy. This confirms the framework's core sovereignty proposition: the patient can hold the complete record while the manufacturer holds only the minimum necessary for the current operational window.

### 7A.5 Limitations and Honest Gaps

**1. Burn volume is low in non-emergency scenarios.** In SCN-001 (90-day happy path), only 17 items were burned despite 129,388 being generated. This is because the 90-day burn window for Clinical Review data means that in a 90-day simulation, only the earliest data reaches burn eligibility by the simulation's end. In a longer simulation (or with shorter burn windows), burn volume would be substantially higher. The simulation correctly implements the burn schedule — it does not demonstrate the steady-state burn rate that would emerge over years of operation.

**2. The simulation does not model adversarial behaviour.** The third-party apps are stubs that either comply, delay, or refuse burn signals. A real adversary would be more sophisticated: copying data before acknowledging the burn signal, storing data in systems not covered by the burn endpoint, or simply lying about burn completion. The simulation proves the protocol works; it does not prove the protocol is resilient to sophisticated evasion.

**3. Report sufficiency is assumed, not validated.** The simulation's AGP report generator produces standard CGM metrics (mean, median, SD, CV, GMI, TIR breakdown, percentiles). Whether these reports are sufficient for all clinical scenarios remains an empirical question that requires endocrinologist validation, not simulation.

**4. Physiological fidelity is approximate.** The glucose trace engine uses a simplified model (circadian rhythm, meal absorption curves, insulin effect, random walk, sensor noise). It produces physiologically plausible traces for architecture testing, but is not a validated patient simulator. Clinical conclusions should not be drawn from the synthetic data.

**5. Scale limits are unexplored.** The simulation tested up to 10 patients. A production manufacturer serves millions. The architecture's behaviour at 10^6 scale — particularly the burn scheduler scanning millions of items for eligibility — is untested and likely requires architectural changes (sharding, distributed processing) not present in the reference implementation.

---

## 8. Paediatric and Adolescent Custodial Transitions

Many insulin pump/CGM users are children with Type 1 diabetes whose data is managed by parents or guardians. The framework's "patient-as-vault-owner" principle assumes a single, stable autonomous agent. This assumption fails for paediatric users and requires explicit treatment.

### 8.1 The Problem

A parent who sets up a CGM for their 8-year-old child typically manages the manufacturer account, the portable record, and all data sharing authorisations. Over the next decade, the child matures into an autonomous adolescent who may have very different preferences about data persistence, sharing, and parental access. The transition from parental management to patient autonomy is gradual, not binary, and the appropriate moment for custodial transfer is not standardised.

### 8.2 Proposed Approach

**Graduated delegation authority.** The architecture should support a transition model in which the parent begins with full custodial authority, the adolescent gains shared authority at a specified age or developmental milestone (we suggest 13–16 as a range, noting jurisdictional variation), and the young adult gains exclusive authority at the age of majority. During the shared-authority period, the adolescent can restrict parental access to historical data while the parent retains access to real-time safety alerts.

**Right to historical data restriction.** When the young adult assumes exclusive custody, they should have the ability to burn historical data from the parental-management period that they do not wish to retain. A 20-year-old should not be bound by data persistence choices their parents made when they were 8.

**Honest limitation:** this graduated model adds significant complexity to the portable record architecture. It requires role-based access controls, time-scoped permissions, and custody transfer protocols that do not currently exist in any consumer or medical data system. We identify this as an engineering requirement rather than claiming to have designed it.

*Simulation note:* The simulation did not implement graduated custody transitions in this version. This remains a critical engineering requirement identified in the issue list (15 issues in Category G) that must be addressed in production implementation.

---

## 9. Cybersecurity Considerations

The insulin pump/CGM ecosystem presents a broader attack surface than pacemakers: continuously active Bluetooth, multiple third-party data recipients, the smartphone as a critical therapeutic node, and extremely granular metabolic data.

Published research has demonstrated that insulin pump commands can be intercepted over unencrypted radio frequencies, that Bluetooth pairing announcements can identify users, and that authentication and encryption in pump communication are optional features.

### 9.1 The Real-Time Data Stream Problem

The first draft's cybersecurity section was correctly criticised as thin on the hardest problem: the real-time therapeutic data stream, which cannot be burned, is the most operationally critical and potentially most valuable attack target. An attacker who can intercept or corrupt real-time CGM readings does not need historical archives to cause patient harm.

The Chambers framework's burn semantics address the historical archive attack surface but not the real-time stream. This is an honest limitation. The framework reduces the total attack surface (historical data is eliminated as a target) but does not address the most safety-critical attack vector (real-time data integrity). Real-time stream protection requires orthogonal security measures: authenticated encryption of the BLE channel, mutual device authentication, integrity verification of glucose readings at the AID algorithm, and anomaly detection for implausible glucose values. These are complementary to burn semantics, not replaceable by them.

### 9.2 Quantified Attack Surface Reduction

*New in v3.* The simulation provides the first quantitative estimate of attack surface reduction from burn semantics:

**Current state (indefinite retention):** A patient using a Dexcom G7 with Control-IQ AID for one year accumulates approximately 525,000 identifiable data items in the manufacturer cloud. After 5 years: 2.6 million items. After 10 years: 5.25 million items. For a manufacturer with 1 million active patients, the cloud contains trillions of identifiable data items, growing without bound.

**Chambers architecture (90-day burn window):** At steady state, the manufacturer cloud holds at most 90 days of data per patient: approximately 129,000 items. Older data has been burned. The maximum exposure for a 1-million-patient manufacturer is 129 billion items — large, but bounded and constant rather than growing. The reduction factor after 5 years of operation is approximately 20x (2.6M / 129K per patient). After 10 years: approximately 40x.

**Emergency burn:** As demonstrated in SCN-009, an emergency burn triggered during a detected breach can eliminate 71% of even the 90-day window within one hour. Post-emergency, the manufacturer cloud holds approximately 37,000 items per affected patient — a 140x reduction compared to 10 years of indefinite retention.

These are simulation-derived estimates, not precise predictions. But they demonstrate that the burn architecture provides a quantifiable, substantial, and monotonically increasing (over time) reduction in breach exposure compared to the status quo.

---

## 10. Comparative Analysis

### 10.1 Recurring Patterns

The same three structural patterns identified in the pacemaker analysis recur:

**Manufacturer as mandatory intermediary.** In all major systems, CGM data flows through manufacturer cloud before reaching clinician. No standard direct sensor-to-clinician path exists.

**Persistence defaults exceeding apparent safety necessity.** Indefinite raw data retention with no published clinical guideline requiring it. The safety and clinical utility is concentrated in recent data (14–90 days); the indefinite archive serves other interests.

**Patient in weakest custodial position.** Generates all data, bears all consequences, has least control over downstream distribution.

### 10.2 Framework Adaptations Required

The adaptations required for the insulin pump/CGM ecosystem are substantial enough that a reader could reasonably ask whether the framework remains unified or has become a family of domain-specific proposals sharing a common vocabulary. We think the answer lies in the shared core: the burden-of-justification principle, the typed worlds structure, and the destruction-as-default orientation. The domain-specific elements — third-party burn propagation, real-time therapeutic exclusions, paediatric transitions, consumer wellness collapse — are calibrations of that core, not departures from it.

*Simulation evidence:* The simulation's world classifier used a single policy file (YAML) to route data items to worlds. Changing the classification policy required modifying the YAML file, not the architecture. This confirms that the framework's core (typed worlds, burn scheduling, portable record delivery) is device-agnostic; only the classification policy is device-specific. A third device class could be supported by writing a new classification policy and device engine without modifying the relay, burn scheduler, or portable record components.

---

## 11. The Data Ownership Question

The insulin pump/CGM ecosystem exposes the ownership question more sharply than pacemakers. No legislation in the US or EU explicitly recognises ownership rights over medical device data. Published legal scholarship confirms this gap.

The framework sidesteps ownership by focusing on custodial defaults and burden of proof. But peer review correctly noted that ownership and custodial obligations may be legally entangled: if a patient has no property interest in their glucose data, what is the legal mechanism for enforcing burn semantics?

We acknowledge this entanglement without resolving it. The framework's governance claim (whoever holds data must justify retention) is weaker without a property baseline. Enforcement may require either legislative recognition of patient data property rights, contractual obligations embedded in device purchase/subscription terms, or regulatory mandates for data minimisation that do not depend on ownership. All three are plausible mechanisms; none currently exist in sufficient form. The framework identifies the need but does not supply the legal infrastructure.

*Simulation contribution:* The simulation's portable record — where the patient holds the encrypted, authoritative copy of their data and the manufacturer holds nothing after the burn window — provides a technical architecture that is compatible with any of these legal mechanisms. Whether enforcement comes through property rights, contract, or regulation, the technical capability to burn and the technical capability to hold are prerequisites. The simulation demonstrates both.

---

## 12. Operational Preconditions and Failure Modes

In addition to the challenges identified in the primary paper, the insulin pump/CGM ecosystem introduces:

**Real-time data continuity.** Any architecture change must guarantee zero interference with real-time CGM-to-pump data flow. Burn semantics must be architecturally firewalled from the therapeutic stream, not merely specified that way.

*Simulation evidence:* The simulation enforces this architecturally: the burn executor operates on relay-side world stores; the phone/app layer's therapeutic data is never accessed by burn components. In SCN-009 (emergency burn destroying 7,216 items), the simulated phone/app layer continued receiving and processing glucose readings throughout the burn — confirming that burn operations are structurally isolated from the therapeutic stream.

**Sensor replacement transitions.** CGM sensors are replaced frequently. The portable record must handle warmup periods, calibration events, and sensor accuracy metadata seamlessly.

*Simulation evidence:* SCN-002 (sensor transition) demonstrated the full replacement lifecycle: old sensor metadata classified to Device Maintenance world, warmup gap during new sensor initialization, resumed readings after warmup, and no data loss during transition.

**Third-party API revocation enforcement.** Verifying that apps actually burn data upon consent revocation is practically difficult. Without a technical enforcement mechanism, burn guarantees are contractual and imperfect.

*Simulation evidence:* SCN-004 (non-compliant app) confirmed this limitation. The relay sent the burn-propagation signal, the non-compliant app refused, and the relay logged the refusal and escalated. The data in the non-compliant app was not destroyed. This is an honest demonstration that the architecture can detect non-compliance but cannot enforce compliance against an unwilling participant.

**Paediatric custody transitions.** Role-based access controls with time-scoped permissions and custody transfer protocols are required but do not exist in current systems.

**Report sufficiency validation.** The raw-data-vs-report distinction (Section 7.3) assumes that processed reports serve clinical needs. This assumption should be validated with endocrinologists across different clinical contexts before being treated as settled.

**Offline resilience.** Patients routinely experience connectivity gaps.

*Simulation evidence:* SCN-006 demonstrated that a 48-hour offline period results in approximately 576 queued glucose readings on the phone, which batch-upload successfully upon reconnection. No data was lost. Burn timers correctly started from upload receipt time (not from reading generation time), preventing premature burn of delayed data.

---

## 13. Conclusions

The insulin pump/CGM ecosystem confirms the Chamber Sentinel framework's core insight: in connected medical device ecosystems, persistence defaults tend to exceed safety necessity, manufacturers architect themselves as intermediaries, and data subjects occupy the weakest custodial position.

This revised analysis also demonstrates that the framework, applied honestly, produces uncomfortable conclusions. It implies that consumer wellness CGM products have no safety justification for any manufacturer data retention. It acknowledges that third-party burn propagation may exceed current engineering capabilities. It concedes that the strongest counterargument for manufacturer retention — algorithm training that directly benefits patients — represents a genuine trade-off rather than a clear-cut case. And it recognises that without legislative or regulatory backing, the framework's enforcement mechanisms remain aspirational.

**What the simulation adds:** The simulation transforms several of the framework's claims from theoretical propositions to empirically demonstrated capabilities:

1. **The typed-worlds architecture is implementable.** Six separate data stores, a policy-driven classifier, world-specific burn schedules, and a portable record delivery system all function as a unified local system. 750,000+ data items were classified, stored, burned, and delivered without a single world-isolation violation.

2. **Burn semantics work end-to-end.** Data items flow from simulated devices through the manufacturer relay, are classified, have reports generated, are delivered to the portable record, and are then destroyed from the relay with post-burn verification. The audit log provides a tamper-evident record of every step.

3. **The attack surface reduction is quantifiable.** Burn semantics reduce manufacturer-held data by approximately 20x after 5 years and 40x after 10 years compared to indefinite retention. Emergency burn provides an additional 71% reduction within one hour.

4. **Burn-propagation through third-party chains is technically feasible.** Consent revocation signals successfully cascaded through a manufacturer-relay-to-app-to-sub-processor chain, with confirmation flowing back. Non-compliance is detectable but not preventable by the architecture alone.

5. **The portable record is a viable sovereignty mechanism.** Patient vaults successfully received, encrypted, and stored complete datasets. Loss and recovery scenarios demonstrated graceful degradation. The patient holds the only remaining copy of burned data.

**What the simulation does not resolve:** The simulation proves the architecture is buildable. It does not prove the architecture should be built — that remains a policy judgment. It does not prove that endocrinologists will accept report-only clinical review. It does not prove that manufacturers will voluntarily adopt burn semantics. It does not prove that the legal infrastructure for enforcement will materialise. And it does not prove that the architecture scales to millions of patients without fundamental redesign.

The framework's central proposition nevertheless survives both the second device class test and the simulation test: data persistence in connected medical device ecosystems should face a burden-of-justification standard. But this paper makes clear that justification is not always easy to deny, that some of the framework's mechanisms are unsolved engineering problems at production scale, and that honest application requires confronting trade-offs rather than pretending they do not exist.

The simulation source code is available as a reference implementation accompanying this paper. We invite replication, extension, and critique.

---

This companion paper should be read alongside the primary Chamber Sentinel medical devices paper. The authors welcome critical engagement from endocrinologists, diabetes technology researchers, device security specialists, patient advocates, regulatory professionals, medical device manufacturers, and — with this revision — software engineers and security architects who can evaluate the simulation's methodology and extend its scenarios.

---

## Appendix A: Simulation Technical Specification

**Source code:** `chamber_sentinel_sim/` Python package (40 source files, 9 scenario definitions)

**Dependencies:** Python 3.11+, NumPy, SciPy, Flask, PyYAML, cryptography

**Installation:** `pip install -e .`

**Execution:** `python -m chamber_sentinel_sim run <scenario.yaml> [-v]`

**Architecture:**

```
Simulated Devices  -->  Phone/App  -->  Manufacturer Relay  -->  Portable Record
  (CGM, Pump,           (BLE sim,       (Classifier,            (AES-256-GCM
   AID, Pen)             cache,          World Stores,            encrypted vault,
                         offline          Report Gen,              delivery confirm,
                         queue)           Burn Scheduler,          patient burn)
                                          Burn Executor,
                                          Audit Logger)
                                              |
                                              v
                                     Third-Party Apps
                                       (burn endpoints,
                                        sub-processor chain)
```

**Key design decisions:**
- In-memory data stores (dict-backed) with SQLite persistence on close — enables fast simulation while preserving inspectable output
- Virtual clock decoupled from wall-clock — all timestamps from simulation clock, enabling deterministic reproducibility
- Network isolation enforced at socket level — blocks all non-localhost connections, preventing accidental external API calls
- SHA-256 hash-chained audit log — every event recorded with tamper-evident integrity
- Scenario-driven design — YAML files define patient profiles, device configurations, event schedules, and expected outcomes

**Reproducibility:** Same YAML scenario + same random seed = identical audit log. All randomness flows through seeded numpy.random.Generator.

## Appendix B: Simulation Data Summary

### B.1 Per-Scenario Metrics

| Metric | SCN-001 | SCN-003 | SCN-005 | SCN-006 | SCN-009 | SCN-010 | SCN-015 |
|---|---|---|---|---|---|---|---|
| Sim days | 90 | 30 | 60 | 14 | 7 | 90 | 30 |
| Patients | 1 | 1 | 1 | 1 | 1 | 1 | 10 |
| Items generated | 129,388 | 43,141 | 86,312 | 20,080 | 10,105 | 130,558 | 331,788 |
| Items classified | 129,658 | 43,231 | 86,492 | 20,122 | 10,126 | 130,828 | 332,506 |
| Items delivered to vault | 100,019 | 34,632 | 69,290 | 16,110 | 7,932 | 100,017 | 272,392 |
| Items burned | 17 | 3 | 10 | 0 | 7,216 | 15 | 29 |
| Reports generated | 6 | 2 | 4 | 1 | 0 | 6 | 20 |
| Audit entries | 26,227 | 51,862 | 17,470 | 3,497 | 22,298 | 26,223 | 87,174 |
| Wall time (s) | 181 | 41 | 60 | 4 | 12 | 211 | 141 |
| Assertions | 7/7 | 4/4 | 3/3 | 3/3 | 3/3 | 7/7 | 5/5 |

### B.2 Aggregate Totals

- **Total items generated across all scenarios:** 751,372
- **Total items classified:** 752,863
- **Total items delivered to portable records:** 500,392
- **Total items burned:** 7,290
- **Total reports generated:** 39
- **Total audit entries verified:** 234,751
- **Total assertions executed:** 32/32 passed
- **Hash chain integrity:** Verified across all 234,751 entries with zero breaks
