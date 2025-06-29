// Visit Notes Parser
// Specialized parser for extracting structured data from medical visit notes

/**
 * Extract key information from medical visit notes
 * @param {string} content - The full text content of the visit note
 * @returns {Object} Structured visit data
 */
function parseVisitNotes(content) {
  // Initialize result object
  const result = {
    visitType: null,
    visitDate: null,
    provider: null,
    facility: null,
    patientInfo: {},
    chiefComplaint: null,
    vitalSigns: {},
    historyOfPresentIllness: null,
    pastMedicalHistory: null,
    medications: [],
    allergies: [],
    physicalExam: null,
    assessment: null,
    diagnoses: [],
    plan: null,
    followUp: null,
    procedures: [],
    labOrders: []
  };
  
  // Extract visit type
  const visitTypeRegex = /(?:Visit Type|Appointment Type|Encounter Type):?\s*([^\n]+)/i;
  const visitTypeMatch = content.match(visitTypeRegex);
  if (visitTypeMatch) {
    result.visitType = visitTypeMatch[1].trim();
  } else {
    // Try to infer from headers
    if (content.match(/(?:annual|yearly|wellness|physical) (?:exam|examination|checkup|visit)/i)) {
      result.visitType = "Annual Physical";
    } else if (content.match(/follow[\s-]*up/i)) {
      result.visitType = "Follow-up Visit";
    } else if (content.match(/(?:new patient|initial) (?:consultation|consult|visit|eval)/i)) {
      result.visitType = "New Patient Visit";
    } else if (content.match(/urgent|emergency/i)) {
      result.visitType = "Urgent Care Visit";
    } else if (content.match(/telemedicine|telehealth|virtual|video/i)) {
      result.visitType = "Telemedicine Visit";
    } else if (content.match(/office visit/i)) {
      result.visitType = "Office Visit";
    }
  }
  
  // Extract visit date
  const visitDateRegex = /(?:Visit Date|Date of Visit|Encounter Date|Date of Service|DOS):?\s*([^\n]+)/i;
  const visitDateMatch = content.match(visitDateRegex);
  if (visitDateMatch) {
    result.visitDate = parseDate(visitDateMatch[1].trim());
  } else {
    // Try alternative date extraction if direct match fails
    const dateRegex = /(?:Date|Service Date):?\s*([^\n]+)/i;
    const dateMatch = content.match(dateRegex);
    if (dateMatch) {
      result.visitDate = parseDate(dateMatch[1].trim());
    }
  }
  
  // Extract provider information
  const providerRegex = /(?:Provider|Physician|Doctor|Clinician|Attending):?\s*([^,\n]*(?:MD|DO|NP|PA)?[^,\n]*)/i;
  const providerMatch = content.match(providerRegex);
  if (providerMatch) {
    result.provider = providerMatch[1].trim();
  }
  
  // Extract facility information
  const facilityRegex = /(?:Facility|Clinic|Location|Practice|Hospital):?\s*([^\n]+)/i;
  const facilityMatch = content.match(facilityRegex);
  if (facilityMatch) {
    result.facility = facilityMatch[1].trim();
  }
  
  // Extract patient information
  const nameRegex = /(?:Patient Name|Name):?\s*([^\n]+)/i;
  const nameMatch = content.match(nameRegex);
  if (nameMatch) {
    result.patientInfo.name = nameMatch[1].trim();
  }
  
  const dobRegex = /(?:DOB|Date of Birth):?\s*([^\n]+)/i;
  const dobMatch = content.match(dobRegex);
  if (dobMatch) {
    result.patientInfo.dateOfBirth = parseDate(dobMatch[1].trim());
  }
  
  const mrnRegex = /(?:MRN|Medical Record Number|Chart Number|Patient ID):?\s*([^\n]+)/i;
  const mrnMatch = content.match(mrnRegex);
  if (mrnMatch) {
    result.patientInfo.mrn = mrnMatch[1].trim();
  }
  
  // Extract chief complaint
  const chiefComplaintRegex = /(?:Chief Complaint|CC|Reason for Visit|Presenting Complaint):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
  const chiefComplaintMatch = content.match(chiefComplaintRegex);
  if (chiefComplaintMatch) {
    result.chiefComplaint = chiefComplaintMatch[1].trim();
  }
  
  // Extract vital signs
  extractVitalSigns(content, result);
  
  // Extract history of present illness
  const hpiRegex = /(?:History of Present Illness|HPI|Present Illness|History):?\s*([^]*?)(?:\n\n|\n[A-Z]|Past Medical History|PMH|Medications|$)/i;
  const hpiMatch = content.match(hpiRegex);
  if (hpiMatch) {
    result.historyOfPresentIllness = hpiMatch[1].trim();
  }
  
  // Extract past medical history
  const pmhRegex = /(?:Past Medical History|PMH|Medical History):?\s*([^]*?)(?:\n\n|\n[A-Z]|Medications|Social History|$)/i;
  const pmhMatch = content.match(pmhRegex);
  if (pmhMatch) {
    result.pastMedicalHistory = pmhMatch[1].trim();
  }
  
  // Extract medications
  extractMedications(content, result);
  
  // Extract allergies
  const allergiesRegex = /(?:Allergies|Medication Allergies|Drug Allergies):?\s*([^]*?)(?:\n\n|\n[A-Z]|Vitals|Physical Exam|$)/i;
  const allergiesMatch = content.match(allergiesRegex);
  if (allergiesMatch) {
    const allergiesText = allergiesMatch[1].trim();
    
    // Check for "No known allergies" or similar
    if (allergiesText.match(/no known|nka|none|denied/i)) {
      result.allergies = ["No Known Allergies"];
    } else {
      // Split by line breaks or commas
      const allergiesLines = allergiesText.split(/[,\n]/);
      
      for (const line of allergiesLines) {
        const trimmedLine = line.trim();
        if (trimmedLine && trimmedLine.length > 1) {
          result.allergies.push(trimmedLine);
        }
      }
    }
  }
  
  // Extract physical exam
  const examRegex = /(?:Physical Exam|Physical Examination|Examination|Exam|PE):?\s*([^]*?)(?:\n\n|\n[A-Z]|Assessment|Plan|Diagnosis|$)/i;
  const examMatch = content.match(examRegex);
  if (examMatch) {
    result.physicalExam = examMatch[1].trim();
  }
  
  // Extract assessment
  const assessmentRegex = /(?:Assessment|Assessment and Plan|Impression|Diagnosis):?\s*([^]*?)(?:\n\n|\n[A-Z]|Plan|Treatment Plan|Recommendations|$)/i;
  const assessmentMatch = content.match(assessmentRegex);
  if (assessmentMatch) {
    result.assessment = assessmentMatch[1].trim();
    
    // Try to extract structured diagnoses from assessment
    extractDiagnoses(result.assessment, result);
  }
  
  // Extract plan
  const planRegex = /(?:Plan|Treatment Plan|Recommendations|Disposition):?\s*([^]*?)(?:\n\n|\n[A-Z]|Follow|Return|$)/i;
  const planMatch = content.match(planRegex);
  if (planMatch) {
    result.plan = planMatch[1].trim();
    
    // Try to extract procedures and lab orders from plan
    extractProceduresAndLabs(result.plan, result);
  }
  
  // Extract follow-up instructions
  const followUpRegex = /(?:Follow-up|Follow Up|Return to Office|Next Appointment):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
  const followUpMatch = content.match(followUpRegex);
  if (followUpMatch) {
    result.followUp = followUpMatch[1].trim();
  }
  
  return result;
}

/**
 * Extract vital signs from the content
 * @param {string} content - The full text content
 * @param {Object} result - The result object to populate
 */
function extractVitalSigns(content, result) {
  // Try to find vitals section
  const vitalsSectionRegex = /(?:Vital Signs|Vitals):?\s*([^]*?)(?:\n\n|\n[A-Z]|History|Physical|$)/i;
  const vitalsSectionMatch = content.match(vitalsSectionRegex);
  
  if (vitalsSectionMatch) {
    const vitalsText = vitalsSectionMatch[1].trim();
    
    // Extract blood pressure
    const bpRegex = /(?:BP|Blood Pressure):?\s*(\d{2,3}\/\d{2,3})/i;
    const bpMatch = vitalsText.match(bpRegex);
    if (bpMatch) {
      result.vitalSigns.bloodPressure = bpMatch[1];
    }
    
    // Extract pulse/heart rate
    const pulseRegex = /(?:Pulse|Heart Rate|HR):?\s*(\d{2,3})/i;
    const pulseMatch = vitalsText.match(pulseRegex);
    if (pulseMatch) {
      result.vitalSigns.pulse = pulseMatch[1];
    }
    
    // Extract respiratory rate
    const respRegex = /(?:Resp|Respiratory Rate|RR):?\s*(\d{1,2})/i;
    const respMatch = vitalsText.match(respRegex);
    if (respMatch) {
      result.vitalSigns.respiratoryRate = respMatch[1];
    }
    
    // Extract temperature
    const tempRegex = /(?:Temp|Temperature):?\s*((?:\d{2,3}\.?\d*))/i;
    const tempMatch = vitalsText.match(tempRegex);
    if (tempMatch) {
      result.vitalSigns.temperature = tempMatch[1];
      
      // Try to determine if Celsius or Fahrenheit
      if (parseFloat(tempMatch[1]) > 45) {
        result.vitalSigns.temperatureUnit = "F";
      } else {
        result.vitalSigns.temperatureUnit = "C";
      }
    }
    
    // Extract SpO2 (oxygen saturation)
    const spo2Regex = /(?:SpO2|O2 Sat|Oxygen Saturation):?\s*(\d{1,3}%?)/i;
    const spo2Match = vitalsText.match(spo2Regex);
    if (spo2Match) {
      result.vitalSigns.oxygenSaturation = spo2Match[1];
    }
    
    // Extract height
    const heightRegex = /(?:Height):?\s*(\d+'\s*\d+"|(?:\d+\.?\d*)\s*(?:cm|in))/i;
    const heightMatch = vitalsText.match(heightRegex);
    if (heightMatch) {
      result.vitalSigns.height = heightMatch[1];
    }
    
    // Extract weight
    const weightRegex = /(?:Weight):?\s*((?:\d+\.?\d*)\s*(?:kg|lbs?))/i;
    const weightMatch = vitalsText.match(weightRegex);
    if (weightMatch) {
      result.vitalSigns.weight = weightMatch[1];
    }
    
    // Extract BMI
    const bmiRegex = /(?:BMI):?\s*((?:\d+\.?\d*))/i;
    const bmiMatch = vitalsText.match(bmiRegex);
    if (bmiMatch) {
      result.vitalSigns.bmi = bmiMatch[1];
    }
  }
}

/**
 * Extract medications from the content
 * @param {string} content - The full text content
 * @param {Object} result - The result object to populate
 */
function extractMedications(content, result) {
  // Try to find medications section
  const medsSectionRegex = /(?:Medications|Current Medications|Meds|Prescription Medications):?\s*([^]*?)(?:\n\n|\n[A-Z]|Allergies|Past Medical|Vitals|$)/i;
  const medsSectionMatch = content.match(medsSectionRegex);
  
  if (medsSectionMatch) {
    const medsText = medsSectionMatch[1].trim();
    
    // Check for "no medications" or similar
    if (medsText.match(/no medications|none|denied/i)) {
      result.medications.push({
        name: "No Current Medications",
        dosage: null,
        frequency: null,
        route: null
      });
      return;
    }
    
    // Split medications by line
    const medsLines = medsText.split('\n');
    
    for (const line of medsLines) {
      const trimmedLine = line.trim();
      if (!trimmedLine || trimmedLine.length < 3) continue;
      
      // Try to extract structured medication info
      // Pattern: [Medication Name] [Dosage] [Route] [Frequency]
      const medInfo = {
        name: null,
        dosage: null,
        frequency: null,
        route: null
      };
      
      // Complex regex to catch various medication formats
      const medRegex = /([A-Za-z\s\-]+(?:\s+XR|\s+SR|\s+ER|\s+CR)?)(?:\s+(\d+\.?\d*\s*(?:mg|mcg|g|mL|mg\/mL)))?(?:\s+(PO|IV|IM|SC|SQ|PR|SL|topical|inhaled|intranasal))?(?:\s+(daily|BID|TID|QID|once daily|twice daily|three times daily|four times daily|every \d+ hours|PRN|as needed))?/;
      
      const medMatch = trimmedLine.match(medRegex);
      
      if (medMatch) {
        medInfo.name = medMatch[1]?.trim() || trimmedLine;
        medInfo.dosage = medMatch[2]?.trim() || null;
        medInfo.route = medMatch[3]?.trim() || null;
        medInfo.frequency = medMatch[4]?.trim() || null;
      } else {
        // If regex fails, just use the whole line as the medication name
        medInfo.name = trimmedLine;
      }
      
      result.medications.push(medInfo);
    }
  }
}

/**
 * Extract diagnoses from assessment section
 * @param {string} assessmentText - The assessment section text
 * @param {Object} result - The result object to populate
 */
function extractDiagnoses(assessmentText, result) {
  if (!assessmentText) return;
  
  // Look for numbered or bulleted diagnoses
  const diagnosesList = assessmentText.split(/\n/).filter(line => line.trim().length > 0);
  
  for (const line of diagnosesList) {
    // Remove numbers, bullets, or other prefixes
    const cleanLine = line.replace(/^[\d\.\-\•\*]+\s*/, '').trim();
    
    // Skip lines that are too short or don't look like diagnoses
    if (cleanLine.length < 3 || 
        cleanLine.match(/^(plan|treatment|assessment|recomm|follow|vital|exam|history)/i)) {
      continue;
    }
    
    // Look for ICD-10 codes
    const icdMatch = cleanLine.match(/\(([A-Z]\d+\.?\d*)\)/);
    let diagnosis = {
      name: cleanLine,
      icdCode: icdMatch ? icdMatch[1] : null
    };
    
    // If an ICD code was found, clean up the diagnosis name
    if (icdMatch) {
      diagnosis.name = cleanLine.replace(/\s*\([A-Z]\d+\.?\d*\)/, '').trim();
    }
    
    result.diagnoses.push(diagnosis);
  }
  
  // If no structured diagnoses were found, try to extract based on common diagnosis keywords
  if (result.diagnoses.length === 0) {
    const diagnosisKeywords = [
      "diagnosed with", "assessment of", "impression of", 
      "consistent with", "suggestive of", "confirming", 
      "indicates", "presenting with", "suffering from"
    ];
    
    for (const keyword of diagnosisKeywords) {
      const regex = new RegExp(`${keyword}\\s+([^,.;:\\n]+)`, 'gi');
      let match;
      
      while ((match = regex.exec(assessmentText)) !== null) {
        const possibleDiagnosis = match[1].trim();
        
        // Check if it's a substantial diagnosis (not just a few characters)
        if (possibleDiagnosis.length > 3) {
          result.diagnoses.push({
            name: possibleDiagnosis,
            icdCode: null
          });
        }
      }
    }
  }
}

/**
 * Extract procedures and lab orders from plan section
 * @param {string} planText - The plan section text
 * @param {Object} result - The result object to populate
 */
function extractProceduresAndLabs(planText, result) {
  if (!planText) return;
  
  // Look for procedure keywords
  const procedureKeywords = [
    "scheduled for", "will undergo", "planned", "procedure", 
    "surgery", "surgical", "operation", "performed", 
    "MRI", "CT", "scan", "X-ray", "ultrasound", "biopsy",
    "endoscopy", "colonoscopy", "injection"
  ];
  
  for (const keyword of procedureKeywords) {
    const regex = new RegExp(`(.*?${keyword}[^,.;:\\n]*)`, 'gi');
    let match;
    
    while ((match = regex.exec(planText)) !== null) {
      const possibleProcedure = match[1].trim();
      
      // Check if it's a substantial procedure (not just a few characters)
      if (possibleProcedure.length > 5 && 
          !result.procedures.includes(possibleProcedure)) {
        result.procedures.push(possibleProcedure);
      }
    }
  }
  
  // Look for lab order keywords
  const labKeywords = [
    "lab", "test", "CBC", "metabolic panel", "BMP", "CMP",
    "thyroid", "lipid", "A1C", "urinalysis", "culture",
    "ordered", "blood work", "bloodwork"
  ];
  
  for (const keyword of labKeywords) {
    const regex = new RegExp(`(.*?${keyword}[^,.;:\\n]*)`, 'gi');
    let match;
    
    while ((match = regex.exec(planText)) !== null) {
      const possibleLabOrder = match[1].trim();
      
      // Check if it's a substantial lab order (not just a few characters)
      if (possibleLabOrder.length > 5 && 
          !result.labOrders.includes(possibleLabOrder)) {
        result.labOrders.push(possibleLabOrder);
      }
    }
  }
}

/**
 * Parse various date formats into a standardized date object
 * @param {string} dateString - The date string to parse
 * @returns {Date|null} Parsed date or null if invalid
 */
function parseDate(dateString) {
  if (!dateString) return null;
  
  // Try various date formats
  const formats = [
    // MM/DD/YYYY
    str => {
      const match = str.match(/(\d{1,2})\/(\d{1,2})\/(\d{4})/);
      if (match) {
        return new Date(`${match[3]}-${match[1].padStart(2, '0')}-${match[2].padStart(2, '0')}`);
      }
      return null;
    },
    // MM-DD-YYYY
    str => {
      const match = str.match(/(\d{1,2})-(\d{1,2})-(\d{4})/);
      if (match) {
        return new Date(`${match[3]}-${match[1].padStart(2, '0')}-${match[2].padStart(2, '0')}`);
      }
      return null;
    },
    // YYYY-MM-DD
    str => {
      const match = str.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
      if (match) {
        return new Date(`${match[1]}-${match[2].padStart(2, '0')}-${match[3].padStart(2, '0')}`);
      }
      return null;
    },
    // Month DD, YYYY
    str => {
      const match = str.match(/([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})/);
      if (match) {
        const monthMap = {
          january: 0, february: 1, march: 2, april: 3, may: 4, june: 5,
          july: 6, august: 7, september: 8, october: 9, november: 10, december: 11,
          jan: 0, feb: 1, mar: 2, apr: 3, jun: 5, jul: 6, aug: 7, sep: 8, sept: 8, oct: 9, nov: 10, dec: 11
        };
        
        const month = monthMap[match[1].toLowerCase()];
        if (month !== undefined) {
          return new Date(parseInt(match[3]), month, parseInt(match[2]));
        }
      }
      return null;
    },
    // Direct parsing (fallback)
    str => {
      const date = new Date(str);
      return isNaN(date.getTime()) ? null : date;
    }
  ];
  
  // Try each format until one succeeds
  for (const format of formats) {
    const date = format(dateString);
    if (date) return date;
  }
  
  return null;
}

/**
 * Format visit notes data into a structured summary
 * @param {Object} visitData - The parsed visit notes data
 * @returns {string} Formatted summary text
 */
function formatVisitSummary(visitData) {
  let summary = "";
  
  // Visit title and date
  if (visitData.visitType) {
    if (visitData.visitDate) {
      const formattedDate = formatDate(visitData.visitDate);
      summary += `# ${visitData.visitType} - ${formattedDate}\n\n`;
    } else {
      summary += `# ${visitData.visitType}\n\n`;
    }
  } else if (visitData.visitDate) {
    summary += `# Office Visit - ${formatDate(visitData.visitDate)}\n\n`;
  } else {
    summary += `# Medical Visit\n\n`;
  }
  
  // Add provider and facility info
  if (visitData.provider) {
    summary += `**Provider:** ${visitData.provider}\n`;
  }
  
  if (visitData.facility) {
    summary += `**Facility:** ${visitData.facility}\n`;
  }
  
  summary += "\n";
  
  // Add chief complaint
  if (visitData.chiefComplaint) {
    summary += `## Chief Complaint\n\n${visitData.chiefComplaint}\n\n`;
  }
  
  // Add vital signs
  if (Object.keys(visitData.vitalSigns).length > 0) {
    summary += "## Vital Signs\n\n";
    
    if (visitData.vitalSigns.bloodPressure) {
      summary += `**Blood Pressure:** ${visitData.vitalSigns.bloodPressure}\n`;
    }
    
    if (visitData.vitalSigns.pulse) {
      summary += `**Pulse:** ${visitData.vitalSigns.pulse} bpm\n`;
    }
    
    if (visitData.vitalSigns.respiratoryRate) {
      summary += `**Respiratory Rate:** ${visitData.vitalSigns.respiratoryRate} breaths/min\n`;
    }
    
    if (visitData.vitalSigns.temperature) {
      summary += `**Temperature:** ${visitData.vitalSigns.temperature}°${visitData.vitalSigns.temperatureUnit || ""}\n`;
    }
    
    if (visitData.vitalSigns.oxygenSaturation) {
      summary += `**Oxygen Saturation:** ${visitData.vitalSigns.oxygenSaturation}\n`;
    }
    
    if (visitData.vitalSigns.height) {
      summary += `**Height:** ${visitData.vitalSigns.height}\n`;
    }
    
    if (visitData.vitalSigns.weight) {
      summary += `**Weight:** ${visitData.vitalSigns.weight}\n`;
    }
    
    if (visitData.vitalSigns.bmi) {
      summary += `**BMI:** ${visitData.vitalSigns.bmi}\n`;
    }
    
    summary += "\n";
  }
  
  // Add history of present illness
  if (visitData.historyOfPresentIllness) {
    summary += `## History of Present Illness\n\n${visitData.historyOfPresentIllness}\n\n`;
  }
  
  // Add allergies
  if (visitData.allergies.length > 0) {
    summary += "## Allergies\n\n";
    
    for (const allergy of visitData.allergies) {
      summary += `- ${allergy}\n`;
    }
    
    summary += "\n";
  }
  
  // Add current medications
  if (visitData.medications.length > 0) {
    summary += "## Current Medications\n\n";
    
    if (visitData.medications.length === 1 && visitData.medications[0].name === "No Current Medications") {
      summary += "No current medications reported.\n\n";
    } else {
      for (const med of visitData.medications) {
        let medText = `- ${med.name}`;
        
        if (med.dosage) {
          medText += ` ${med.dosage}`;
        }
        
        if (med.route) {
          medText += ` ${med.route}`;
        }
        
        if (med.frequency) {
          medText += ` ${med.frequency}`;
        }
        
        summary += `${medText}\n`;
      }
      
      summary += "\n";
    }
  }
  
  // Add past medical history
  if (visitData.pastMedicalHistory) {
    summary += `## Past Medical History\n\n${visitData.pastMedicalHistory}\n\n`;
  }
  
  // Add physical exam findings
  if (visitData.physicalExam) {
    summary += `## Physical Examination\n\n${visitData.physicalExam}\n\n`;
  }
  
  // Add assessment and diagnoses
  if (visitData.assessment || visitData.diagnoses.length > 0) {
    summary += "## Assessment\n\n";
    
    if (visitData.diagnoses.length > 0) {
      for (const diagnosis of visitData.diagnoses) {
        if (diagnosis.icdCode) {
          summary += `- ${diagnosis.name} (${diagnosis.icdCode})\n`;
        } else {
          summary += `- ${diagnosis.name}\n`;
        }
      }
      summary += "\n";
    }
    
    if (visitData.assessment) {
      summary += `${visitData.assessment}\n\n`;
    }
  }
  
  // Add plan
  if (visitData.plan) {
    summary += `## Plan\n\n${visitData.plan}\n\n`;
  }
  
  // Add procedures
  if (visitData.procedures.length > 0) {
    summary += "## Procedures\n\n";
    
    for (const procedure of visitData.procedures) {
      summary += `- ${procedure}\n`;
    }
    
    summary += "\n";
  }
  
  // Add lab orders
  if (visitData.labOrders.length > 0) {
    summary += "## Laboratory Orders\n\n";
    
    for (const labOrder of visitData.labOrders) {
      summary += `- ${labOrder}\n`;
    }
    
    summary += "\n";
  }
  
  // Add follow-up instructions
  if (visitData.followUp) {
    summary += `## Follow-up Instructions\n\n${visitData.followUp}\n\n`;
  }
  
  return summary;
}

/**
 * Format a date object to a readable string
 * @param {Date} date - The date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
  if (!date) return "Unknown Date";
  
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}

module.exports = {
  parseVisitNotes,
  formatVisitSummary
}; 