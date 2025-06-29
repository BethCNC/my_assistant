# Notion Database Schema for Chronic Illness Tracking

## Core Databases

### 1. Medical Calendar (Primary Database)
This is the central timeline database that will contain all medical events, appointments, and daily tracking entries.

**Properties:**
- **Name**: Title of the entry
- **Date**: Date of the event/entry
- **Type**: Select [Doctor Visit, Lab Test, Imaging, Procedure, Daily Journal, Medication Change, Hospitalization, Other]
- **Doctor**: Relation to Medical Team database
- **Related Diagnoses**: Relation to Diagnoses database (multi-select)
- **Symptoms**: Relation to Symptoms database (multi-select)
- **Medications**: Relation to Medications database (multi-select)
- **Pain Level**: Number (1-10)
- **Energy Level**: Number (1-10)
- **Stress Level**: Number (1-10)
- **Sleep Quality**: Number (1-10)
- **Doctor's Notes**: Text (for medical provider notes)
- **Personal Notes**: Text (for your own observations)
- **Lab Results**: Text (formatted summary of lab results)
- **Follow-up Required**: Checkbox
- **Follow-up Date**: Date
- **File Attachments**: File & Media
- **Tags**: Multi-select [Flare, Important, Medication Reaction, Research, Insurance]

### 2. Diagnoses Database
This database tracks all diagnoses, both active and resolved.

**Properties:**
- **Name**: Name of diagnosis/condition
- **Status**: Select [Active, Resolved, Suspected, Ruled Out]
- **Date Diagnosed**: Date
- **Date Resolved**: Date (if applicable)
- **Diagnosing Doctor**: Relation to Medical Team database
- **Related Symptoms**: Relation to Symptoms database (multi-select)
- **Treatments**: Relation to Treatments database (multi-select)
- **Medications**: Relation to Medications database (multi-select)
- **Medical Documentation**: File & Media
- **Notes**: Text
- **Category**: Select [Autoimmune, Endocrine, Neurological, Musculoskeletal, Psychiatric, Gastrointestinal, Other]
- **Severity**: Select [Mild, Moderate, Severe]

### 3. Symptoms Database
This database tracks all symptoms you experience.

**Properties:**
- **Name**: Name of symptom
- **Status**: Select [Active, Intermittent, Resolved]
- **First Noted**: Date
- **Related Diagnoses**: Relation to Diagnoses database (multi-select)
- **Body Location**: Select [Head, Neck, Shoulder, Arm, Hand, Chest, Back, Abdomen, Hip, Leg, Foot, Multiple, Systemic]
- **Pattern**: Select [Constant, Intermittent, Cyclical, Flare-based, Progressive, Regressive]
- **Severity**: Number (1-10)
- **Triggers**: Multi-select [Weather, Stress, Food, Activity, Medication, Unknown]
- **Relieving Factors**: Multi-select [Rest, Medication, Heat, Cold, Exercise, Diet]
- **Notes**: Text

### 4. Medications Database
This database tracks all medications, supplements, and treatments.

**Properties:**
- **Name**: Medication name (with generic name)
- **Type**: Select [Prescription, OTC, Supplement, Topical, Injectable, Infusion, Other]
- **Status**: Select [Current, Past, As Needed, Not Started]
- **Start Date**: Date
- **End Date**: Date (if applicable)
- **Prescribing Doctor**: Relation to Medical Team database
- **Dosage**: Text (e.g., "20mg")
- **Frequency**: Select [Daily, BID, TID, QID, Weekly, Monthly, As Needed, Other]
- **Schedule**: Text (specific times or instructions)
- **Purpose**: Text
- **For Conditions**: Relation to Diagnoses database (multi-select)
- **For Symptoms**: Relation to Symptoms database (multi-select)
- **Side Effects**: Multi-select [custom list based on your experience]
- **Effectiveness**: Number (1-5)
- **Notes**: Text
- **Refill Due**: Date
- **Pharmacy**: Text

### 5. Medical Team Database
This database tracks all healthcare providers.

**Properties:**
- **Name**: Provider name
- **Specialty**: Select [Rheumatology, Neurology, Primary Care, Endocrinology, Psychiatry, Other]
- **Facility**: Text (hospital, clinic, or practice name)
- **Address**: Text
- **Phone**: Phone number
- **Email**: Email
- **First Visit**: Date
- **Last Visit**: Date
- **Next Appointment**: Date
- **Patient Portal**: URL
- **Notes**: Text
- **Current**: Checkbox

### 6. Lab Results Database (Linked View)
This is a specialized view of the Medical Calendar focused on lab results.

**Properties:**
- **Name**: Test name
- **Date**: Date of test
- **Type**: Select [Blood, Urine, CSF, Synovial, Imaging, Other]
- **Ordering Doctor**: Relation to Medical Team database
- **Test Lab**: Text
- **Results Available**: Checkbox
- **Value**: Text
- **Reference Range**: Text
- **Flag**: Select [Normal, Low, High, Critical]
- **Previous Value**: Text
- **Notes**: Text

### 7. Treatments & Procedures Database
This database tracks all treatments and procedures.

**Properties:**
- **Name**: Treatment/procedure name
- **Date**: Date
- **Type**: Select [Surgery, Physical Therapy, Injection, Infusion, Alternative, Other]
- **Provider**: Relation to Medical Team database
- **Facility**: Text
- **For Conditions**: Relation to Diagnoses database (multi-select)
- **For Symptoms**: Relation to Symptoms database (multi-select)
- **Results**: Text
- **Effectiveness**: Number (1-5)
- **Follow-up Required**: Checkbox
- **Follow-up Date**: Date
- **Notes**: Text
- **Medical Documentation**: File & Media

## Specialized Templates

### 1. Daily Health Journal Template
```
# Daily Health Journal - [Date]

## Medications
- [ ] Morning medications taken
- [ ] Afternoon medications taken
- [ ] Evening medications taken
- [ ] As-needed medications: [list if taken]

## Pain & Symptoms
- Pain level (1-10): 
  - Neck: 
  - Right shoulder: 
  - Lower back: 
  - Other areas: 

- Symptom tracking:
  - Fatigue (1-10): 
  - Brain fog (1-10): 
  - Joint stiffness (1-10): 
  - Other symptoms: 

## Wellness Metrics
- Sleep quality (1-10): 
- Sleep duration: 
- Energy level (1-10): 
- Stress level (1-10): 
- Exercise/activity: 
- Diet notes: 

## Notes & Observations
- Triggers noticed: 
- Helpful activities/remedies: 
- Questions for next appointment:
- Other observations:
```

### 2. Doctor Visit Template
```
# Doctor Visit - [Doctor Name] - [Date]

## Visit Information
- Provider: [Relation]
- Specialty: 
- Facility: 
- Reason for visit: 

## Discussion Points
- Main concerns addressed:
- New symptoms discussed:
- Medication changes:
- Tests ordered:
- Questions asked:

## Assessment & Plan
- Doctor's assessment:
- Diagnosis updates:
- Treatment plan:
- Medication changes:
  - New prescriptions:
  - Discontinued medications:
  - Modified dosages:

## Follow-up
- Follow-up needed: [Yes/No]
- Next appointment date:
- Tests to complete before next visit:
- Referrals:

## Notes
- Personal observations:
- Questions for next time:
```

### 3. Lab Results Template
```
# Lab Results - [Test Name] - [Date]

## Test Information
- Test name:
- Ordering doctor: [Relation]
- Collection date:
- Lab/facility:

## Results
- Value: 
- Reference range:
- Flag: [Normal/Low/High]
- Previous value: [if available]
- Change from previous: [Improved/Worsened/No change]

## Clinical Significance
- Related diagnoses: [Relations]
- Related symptoms: [Relations]
- Doctor's notes:
- Personal notes:

## Follow-up
- Actions required:
- Follow-up tests needed:
- Questions for doctor:
```

### 4. Medication Review Template
```
# Medication Review - [Date]

## Current Medications
[List of all active medications with dosages and purposes]

## Effectiveness Assessment
[For each medication]:
- Name:
- Taking as prescribed: [Yes/No]
- Effectiveness (1-5):
- Side effects experienced:
- Concerns:

## Interactions & Issues
- Potential interactions identified:
- Administration issues:
- Refill status:

## Questions for Providers
- Questions for next appointment:
- Medications to discuss changing:

## Notes
- Personal observations:
- Strategies for improving adherence:
```

## Database Relationships Diagram

```
Medical Calendar (Primary)
│
├─── Related to ─── Medical Team
│
├─── Related to ─── Diagnoses ─── Related to ─── Symptoms
│                         │
│                         └─── Related to ─── Treatments
│
├─── Related to ─── Medications
│
└─── Related to ─── Symptoms
```

## Dashboard Views

### 1. Daily Tracking Dashboard
- Today's health status summary
- Medication checklist
- Symptom tracker
- Quick entry form
- Recent entries (past 7 days)

### 2. Medical Overview Dashboard
- Active diagnoses
- Current medications
- Upcoming appointments
- Recent test results
- Important medical documents

### 3. Timeline View
- Chronological view of all medical events
- Filter by category, diagnosis, or doctor
- Highlight important events

### 4. Symptom Analysis Dashboard
- Symptom tracking over time
- Correlation with medications, weather, stress
- Pattern identification
- Trend analysis

### 5. Medication Management Dashboard
- Current medication schedule
- Effectiveness tracking
- Side effect monitoring
- Refill tracking
- Discontinued medications history

## Implementation Phases

### Phase 1: Database Setup (Week 1)
- Create all core databases with properties
- Set up relationship links
- Create templates

### Phase 2: Historical Data Import (Weeks 2-4)
- Import major events and diagnoses
- Import medical team information
- Import medication history
- Import relevant lab results and imaging

### Phase 3: Daily Tracking System (Week 5)
- Set up daily journal template
- Create mobile-friendly quick entry system
- Establish notification and reminder system

### Phase 4: Dashboard Creation (Week 6)
- Create all dashboard views
- Set up filters and sorting
- Create visualization tools
- Build reporting templates

### Phase 5: Testing & Refinement (Week 7-8)
- Test all systems for usability
- Refine templates based on daily use
- Optimize workflows
- Train on regular usage patterns
