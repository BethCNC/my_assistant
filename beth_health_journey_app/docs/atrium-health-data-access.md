# Atrium Health Data Access Guide

This document outlines the options for accessing your health data from Atrium Health and incorporating it into your health journey app.

## Available Methods

### 1. Individual PDF Exports (Available Now)

Atrium Health MyChart allows you to export individual records as PDFs:

1. **Log in** to your Atrium Health MyChart account at [my.atriumhealth.org](https://my.atriumhealth.org)
2. Navigate to each section (Lab Results, Medical Conditions, etc.)
3. For each record, look for the **Print/Download** option
4. Save each PDF to a folder on your computer
5. Use the `scripts/parse-atrium-pdfs.ts` script to organize these PDFs

```bash
# Organize your downloaded PDFs
npx ts-node scripts/parse-atrium-pdfs.ts
```

### 2. Complete Medical Record Request (Recommended)

To get your complete health record in an electronic format:

1. Use the record request generator:
```bash
npx ts-node scripts/request-atrium-records.ts
```

2. Follow the instructions to submit the request to Atrium Health
3. When received, the complete record can be imported into your app

### 3. MyChart "Share My Record" Feature

This option provides a standardized CCD/CDA health record file:

1. Log in to MyChart
2. Look for "Share My Record" or "Download My Record" options
3. Request a download of your record in CCD/CDA format (XML)
4. This format contains structured data that can be parsed

## Obtaining a FHIR API Token

Unlike Novant/Epic, Atrium Health does not currently provide patient-accessible FHIR API tokens through a public portal like fetch-my-epic-token.org. 

Options to pursue:

1. **Contact Technical Support**: Call Atrium Health technical support at 704-667-9405 and specifically ask about FHIR API access for patients, referencing the 21st Century Cures Act.

2. **Medical Records Department**: When requesting your complete medical record, specifically ask if they offer FHIR API access for patients.

3. **Health App Connection**: Some health apps (like Apple Health) may be able to connect to Atrium Health and act as intermediaries.

## Future Development Plans

The following scripts are available to help with Atrium Health data:

1. `scripts/parse-atrium-pdfs.ts`: Organizes downloaded PDFs by type
2. `scripts/request-atrium-records.ts`: Generates a medical records request letter
3. `scripts/extract-atrium-data.ts`: Interactive guide for manual data extraction

Future improvements will include:
- PDF text extraction to parse lab values and other structured data
- CCD/CDA XML parser for imported health records
- Web scraping tools to extract data from the MyChart portal

## Recommended Workflow

1. Request your complete record using the request generator
2. While waiting, export individual records as PDFs for immediate use
3. Use the PDF organizer to categorize your exports
4. Continue to check for patient FHIR API access options

## Technical Limitations

- No direct FHIR API access currently available
- MyChart session tokens can't access the internal API directly
- PDF exports require manual downloading for each record
- PDF data extraction requires OCR and text parsing

## Resources

- [Atrium Health MyChart](https://my.atriumhealth.org)
- [HIPAA Right of Access](https://www.hhs.gov/hipaa/for-individuals/right-to-access/index.html)
- [21st Century Cures Act Information Blocking Rules](https://www.healthit.gov/curesrule/) 