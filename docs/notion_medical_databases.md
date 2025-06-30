# Notion Medical Databases Documentation

## Overview

This document provides a comprehensive overview of the interconnected medical databases in Notion that track health information, appointments, symptoms, conditions, and providers.

## Medical Calendar Database

**ID**: `17b86edc-ae2c-81c1-83e0-e0a19a035932`
**Title**: Medical Calendar

### Description

The Medical Calendar database serves as the central timeline for all medical events, appointments, and daily health tracking. It connects medical providers, symptoms, conditions, and medications into a comprehensive health management system.

### Properties

| Property Name | Type | Description |
|--------------|------|-------------|
| Name | Title | The name/title of the medical event |
| Date | Date | The date of the medical event |
| Type | Select | Classification of the event type |
| Doctor | Relation | Link to the healthcare provider in the Medical Team database |
| Related Diagnoses | Relation | Link to relevant conditions in the Medical Conditions database |
| Linked Symptoms | Relation | Connection to symptoms tracked in the Symptoms database |
| Medications | Relation | Medications related to this event |
| Purpose | Rich Text | Reason for the appointment or event |
| Personal Notes | Rich Text | Personal observations and notes |
| Doctors Notes | Rich Text | Notes from healthcare providers |
| Lab Result | Rich Text | Results from lab tests |
| Energy | Number | Energy level rating (likely 1-10) |
| Anxiety | Number | Anxiety level rating (likely 1-10) |
| Shoulder Pain | Number | Pain level rating (likely 1-10) |
| Sleep | Number | Sleep quality rating (likely 1-10) |
| Salt Tabs | Number | Salt tablet tracking |
| Glows | Rich Text | Positive health observations |
| Grows | Rich Text | Areas for improvement |
| Notes | Relation | Related notes or documents |
| Movement Work | Checkbox | Tracking physical therapy/exercise |
| Walk | Checkbox | Tracking walking activity |

#### Medication Tracking Checkboxes
The database includes multiple checkbox properties to track daily medication intake:
- Adderall - AM
- Adderall - 1PM
- Adderall - PM
- Pepcid - AM
- Pepcid - PM
- Zrytec - AM
- Zrytec - PM
- Quercetin

## Medical Team Database

**ID**: `17b86edc-ae2c-8155-8caa-fbb80647f6a9`
**Title**: Medical Team

### Description

This database maintains information about all healthcare providers involved in care, including contact details, specialties, and treatment relationships.

### Properties

| Property Name | Type | Description |
|--------------|------|-------------|
| Name | Title | Provider's name |
| Role | Select | Medical specialty or role (e.g., Rheumatologist, GP) |
| Active | Select | Current status (Currently Treating, Previous Provider, Future Provider) |
| Office Name | Rich Text | Name of the medical practice or facility |
| Address | Rich Text | Physical address information |
| Phone | Phone Number | Contact number |
| Email | Email | Email address |
| URL | URL | Website or portal link |
| Treating | Relation | Conditions being treated by this provider |
| Prescribing | Relation | Medications prescribed by this provider |
| Date Started Care | Date | When the provider relationship began |
| Notes | Rich Text | Additional information about the provider |
| Affiliation | Select | Healthcare network/system affiliation |
| Image | Files | Provider photo or logo |

### Provider Roles

The database includes a comprehensive list of medical specialties including:
- General Practitioner
- Rheumatologist
- Endocrinologist
- Cardiologist
- Neurologist
- Physiotherapist
- OBGYN
- Orthopedic Surgeon
- Allergy/Immunology
- Gastroenterology
- Hand Specialist
- Spine Specialist
- Vascular Surgery
- Physiatrist
- Neuro-Ophthalmology

### Affiliations

Tracks healthcare systems and networks including:
- Atrium
- Novant
- CENTA
- UNC Health
- UNC School of Medicine
- Carolina Asthma & Allergy Center
- Charlotte Gastroenterology
- Brown Neurosurgery
- Carolina Digestive Health Associates

## Medical Conditions Database

**ID**: `17b86edc-ae2c-8167-ba15-f9f03b49795e`
**Title**: Medical Conditions

### Description

This database catalogs medical diagnoses, conditions, and disorders, with their relationships to symptoms, treatments, and healthcare providers.

### Properties

This database connects diagnosed conditions with:
- Related symptoms
- Treating physicians
- Relevant medications
- Related medical events

## Symptoms Database

**ID**: `17b86edc-ae2c-81c6-9077-e55a68cf2438`
**Title**: Symptoms

### Description

A comprehensive tracking system for symptoms, their onset, active status, and relationships to diagnoses and medical events.

### Properties

| Property Name | Type | Description |
|--------------|------|-------------|
| Name | Title | Symptom name |
| Active | Checkbox | Whether the symptom is currently present |
| Related Diagnosis | Relation | Connected diagnosed conditions |
| Related Events | Relation | Medical events where this symptom was noted |
| First Onset | Rollup | Earliest date this symptom was recorded (from Related Events) |

## Medications Database

**ID**: `17b86edc-ae2c-81a7-b28a-e9fbcc7e7b62`
**Title**: Medications

### Description

Tracks current and past medications, including dosages, prescribers, and conditions being treated.

### Properties

| Property Name | Type | Description |
|--------------|------|-------------|
| Name | Title | Medication name (brand name) |
| Generic Name | Rich Text | Generic/chemical name |
| Dose (mg) | Number | Dosage amount |
| Frequency | Multi-select | When medication is taken (AM, Afternoon, PM, As Needed) |
| Active | Select | Status (Currently Taking, Previous Medication) |
| Date Commenced | Date | When medication was started |
| Prescribed Date | Date | When medication was prescribed |
| Prescribed by | Relation | Link to prescribing doctor |
| To Treat | Relation | Conditions being treated with this medication |
| Related Events | Relation | Medical events related to this medication |
| Last Collected | Rollup | Most recent refill date (from Related Events) |
| Notes | Rich Text | Additional information about the medication |

## Database Relationships

The Notion medical database system uses bidirectional relationships to create a comprehensive health tracking system:

### Primary Relationships

1. **Medical Events ↔ Medical Team**
   - Medical Events tracks appointments with doctors
   - Medical Team shows all events associated with each provider

2. **Medical Events ↔ Symptoms**
   - Medical Events records symptoms experienced at each event
   - Symptoms database tracks when symptoms occur across events
   - First Onset property uses rollup to determine earliest symptom occurrence

3. **Medical Events ↔ Conditions**
   - Medical Events links to relevant diagnoses
   - Conditions database shows all events related to each condition

4. **Medical Events ↔ Medications**
   - Medical Events tracks medication usage
   - Medications database shows events related to prescribing or refills
   - Last Collected property uses rollup to find most recent refill

5. **Conditions ↔ Symptoms**
   - Conditions database links to related symptoms
   - Symptoms database shows which diagnoses they're associated with

6. **Conditions ↔ Medical Team**
   - Conditions database tracks treating providers
   - Medical Team shows which conditions each provider treats

7. **Conditions ↔ Medications**
   - Conditions database links to relevant medications
   - Medications database shows which conditions they treat

8. **Medications ↔ Medical Team**
   - Medications database tracks prescribing doctors
   - Medical Team shows medications prescribed by each provider

## Use Cases

The integrated database system enables:

1. **Chronological Health Timeline**
   - View all medical events in sequence
   - Track symptom onset and progression over time
   - Monitor medication changes and effectiveness

2. **Provider Management**
   - Track which providers are treating which conditions
   - Maintain current contact information and appointment history
   - Document provider notes and recommendations

3. **Condition Tracking**
   - Monitor symptom associations with each diagnosis
   - Track treatment approaches by condition
   - Document the history and progression of each condition

4. **Medication Management**
   - Track current and previous medications
   - Monitor prescription refills and changes
   - Document effectiveness for specific conditions

5. **Symptom Analysis**
   - Track symptom frequency and patterns
   - Identify relationships between symptoms and diagnoses
   - Monitor symptom responses to treatments

6. **Daily Health Monitoring**
   - Track energy levels, pain, sleep, and anxiety
   - Monitor medication compliance
   - Document exercise and self-care activities

## Integration Points

The Notion medical database system provides integration opportunities with:

1. **Medical Data Processing Pipeline**
   - Extract structured data for analysis
   - Generate chronological medical timelines
   - Create visualization of symptom-condition relationships

2. **AI Analysis**
   - Identify patterns in symptom occurrence
   - Analyze effectiveness of treatments
   - Generate insights about condition relationships

3. **Medical Knowledge Base**
   - Link symptoms and conditions to medical references
   - Integrate with research about hypermobility disorders, ADHD, and other conditions
   - Support development of personalized treatment approaches 