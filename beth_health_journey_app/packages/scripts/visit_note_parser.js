// Visit Note Parser
// Specialized parser for extracting structured data from doctor visit notes

/**
 * Extract key information from visit note text
 * @param {string} content - The full text content of the visit note
 * @returns {Object} Structured visit note data
 */
function parseVisitNote(content) {
  // Initialize result object
  const result = {
    visitType: null,
    visitDate: null,
    provider: null,
    facility: null,
    chiefComplaint: null,
    patientInfo: {},
    diagnoses: [],
    symptoms: [],
    medications: [],
    vitalSigns: {},
    plan: null,
    followUp: null,
  };
  
  // Extract visit type
  const visitTypeRegex = /(?:Visit Type|Appointment Type|Encounter Type):?\s*([^\n]+)/i;
  const visitTypeMatch = content.match(visitTypeRegex);
  if (visitTypeMatch) {
    result.visitType = visitTypeMatch[1].trim();
  } else {
    // Try to infer visit type from content
    if (content.includes('CONSULTATION') || content.includes('Initial Consult')) {
      result.visitType = 'Consultation';
    } else if (content.includes('FOLLOW-UP') || content.includes('Follow Up')) {
      result.visitType = 'Follow-Up';
    } else if (content.includes('PHYSICAL EXAM') || content.includes('Annual Physical')) {
      result.visitType = 'Annual Physical';
    } else {
      result.visitType = 'Office Visit';
    }
  }
  
  // Extract visit date
  const dateRegex = /(?:Date of Service|Visit Date|DOS|Date):?\s*([^\n]+)/i;
  const dateMatch = content.match(dateRegex);
  if (dateMatch) {
    result.visitDate = parseDate(dateMatch[1].trim());
  }
  
  // Extract provider information
  const providerRegex = /(?:Provider|Physician|Doctor|Attending|Seen By):?\s*([^,\n]*(?:MD|DO|NP|PA)?[^,\n]*)/i;
  const providerMatch = content.match(providerRegex);
  if (providerMatch) {
    result.provider = providerMatch[1].trim();
  }
  
  // Extract facility information
  const facilityRegex = /(?:Facility|Clinic|Location|Practice):?\s*([^\n]+)/i;
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
  
  const mrnRegex = /(?:MRN|Medical Record Number|Chart Number):?\s*([^\n]+)/i;
  const mrnMatch = content.match(mrnRegex);
  if (mrnMatch) {
    result.patientInfo.mrn = mrnMatch[1].trim();
  }
  
  // Extract chief complaint
  const chiefComplaintRegex = /(?:Chief Complaint|CC|Reason for Visit|Presenting Complaint):?\s*([^\n]+)/i;
  const chiefComplaintMatch = content.match(chiefComplaintRegex);
  if (chiefComplaintMatch) {
    result.chiefComplaint = chiefComplaintMatch[1].trim();
  }
  
  // Extract diagnoses
  // Look for sections that commonly list diagnoses
  const diagnosisRegex = /(?:Diagnosis|Assessment|Impression|Problem List):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
  const diagnosisMatch = content.match(diagnosisRegex);
  if (diagnosisMatch) {
    const diagnosisText = diagnosisMatch[1].trim();
    
    // Split by new lines or numbered items
    const diagnosisLines = diagnosisText.split(/\n|(?:\d+\.)/).filter(line => line.trim().length > 0);
    
    for (const line of diagnosisLines) {
      if (line.trim().length > 0 && !line.includes(':') && line.length < 100) {
        result.diagnoses.push(line.trim());
      }
    }
  }
  
  // Extract symptoms
  // Look for sections that commonly list symptoms
  const symptomsRegex = /(?:Symptoms|Subjective|History of Present Illness|HPI):?\s*([^]*?)(?:\n\n|\n[A-Z]|Review of Systems|Physical Exam|$)/i;
  const symptomsMatch = content.match(symptomsRegex);
  if (symptomsMatch) {
    const symptomsText = symptomsMatch[1].trim();
    
    // Common symptom keywords to look for
    const symptomKeywords = [
      'pain', 'ache', 'fatigue', 'tired', 'exhaustion', 'weakness', 'numbness', 
      'tingling', 'swelling', 'nausea', 'vomiting', 'diarrhea', 'constipation',
      'headache', 'dizziness', 'vertigo', 'rash', 'itching', 'cough', 'shortness of breath',
      'fever', 'chills', 'sweating', 'insomnia', 'trouble sleeping', 'anxiety', 'depression',
      'mood', 'irritability', 'concentration', 'memory', 'vision', 'hearing',
      'burning', 'stiffness', 'cramping', 'spasm'
    ];
    
    // Look for symptoms in the text
    for (const keyword of symptomKeywords) {
      const regex = new RegExp(`\\b(${keyword}[\\w\\s]*?)(?:\\.|,|\\n)`, 'gi');
      let match;
      
      while ((match = regex.exec(symptomsText)) !== null) {
        const symptom = match[1].trim();
        if (symptom.length > 3 && symptom.length < 50 && !result.symptoms.includes(symptom)) {
          result.symptoms.push(symptom);
        }
      }
    }
  }
  
  // Extract medications
  // Look for sections that commonly list medications
  const medicationsRegex = /(?:Medications|Current Medications|Prescription|Rx):?\s*([^]*?)(?:\n\n|\n[A-Z]|Assessment|Plan|$)/i;
  const medicationsMatch = content.match(medicationsRegex);
  if (medicationsMatch) {
    const medicationsText = medicationsMatch[1].trim();
    
    // Split by new lines or bullet points
    const medicationLines = medicationsText.split(/\n|•/).filter(line => line.trim().length > 0);
    
    for (const line of medicationLines) {
      const trimmedLine = line.trim();
      // Avoid short fragments and header lines
      if (trimmedLine.length > 5 && !trimmedLine.includes(':') && !trimmedLine.match(/^(home|current|prescription|medication)/i)) {
        result.medications.push(trimmedLine);
      }
    }
  }
  
  // Extract vital signs
  const vitalsRegex = /(?:Vital Signs|Vitals):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
  const vitalsMatch = content.match(vitalsRegex);
  if (vitalsMatch) {
    const vitalsText = vitalsMatch[1].trim();
    
    // Extract specific vital measurements
    const bpRegex = /(?:BP|Blood Pressure):?\s*(\d+\/\d+)/i;
    const bpMatch = vitalsText.match(bpRegex);
    if (bpMatch) {
      result.vitalSigns.bloodPressure = bpMatch[1];
    }
    
    const pulseRegex = /(?:Pulse|HR|Heart Rate):?\s*(\d+)/i;
    const pulseMatch = vitalsText.match(pulseRegex);
    if (pulseMatch) {
      result.vitalSigns.pulse = pulseMatch[1];
    }
    
    const tempRegex = /(?:Temp|Temperature):?\s*([\d\.]+)/i;
    const tempMatch = vitalsText.match(tempRegex);
    if (tempMatch) {
      result.vitalSigns.temperature = tempMatch[1];
    }
    
    const respRegex = /(?:Resp|Respiratory Rate|RR):?\s*(\d+)/i;
    const respMatch = vitalsText.match(respRegex);
    if (respMatch) {
      result.vitalSigns.respiratoryRate = respMatch[1];
    }
    
    const weightRegex = /(?:Weight|Wt):?\s*([\d\.]+)\s*(kg|lb)/i;
    const weightMatch = vitalsText.match(weightRegex);
    if (weightMatch) {
      result.vitalSigns.weight = `${weightMatch[1]} ${weightMatch[2]}`;
    }
    
    const heightRegex = /(?:Height|Ht):?\s*([\d\.]+)\s*(cm|in)/i;
    const heightMatch = vitalsText.match(heightRegex);
    if (heightMatch) {
      result.vitalSigns.height = `${heightMatch[1]} ${heightMatch[2]}`;
    }
  }
  
  // Extract plan
  const planRegex = /(?:Plan|Treatment Plan|Recommendations):?\s*([^]*?)(?:\n\n|\n[A-Z]|Follow-up|$)/i;
  const planMatch = content.match(planRegex);
  if (planMatch) {
    result.plan = planMatch[1].trim();
  }
  
  // Extract follow-up information
  const followUpRegex = /(?:Follow-up|Follow Up|Return Visit|Return to Clinic):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
  const followUpMatch = content.match(followUpRegex);
  if (followUpMatch) {
    result.followUp = followUpMatch[1].trim();
  }
  
  return result;
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
 * Format visit note data into a structured summary
 * @param {Object} visitData - The parsed visit note data
 * @returns {string} Formatted summary text
 */
function formatVisitSummary(visitData) {
  let summary = "";
  
  // Add visit type and date as title
  const visitTypeDisplay = visitData.visitType || "Office Visit";
  if (visitData.visitDate) {
    const formattedDate = formatDate(visitData.visitDate);
    summary += `# ${visitTypeDisplay} - ${formattedDate}\n\n`;
  } else {
    summary += `# ${visitTypeDisplay}\n\n`;
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
  
  // Add diagnoses
  if (visitData.diagnoses.length > 0) {
    summary += "## Diagnoses\n\n";
    
    for (const diagnosis of visitData.diagnoses) {
      summary += `- ${diagnosis}\n`;
    }
    
    summary += "\n";
  }
  
  // Add symptoms
  if (visitData.symptoms.length > 0) {
    summary += "## Symptoms Discussed\n\n";
    
    for (const symptom of visitData.symptoms) {
      summary += `- ${symptom}\n`;
    }
    
    summary += "\n";
  }
  
  // Add medications
  if (visitData.medications.length > 0) {
    summary += "## Medications\n\n";
    
    for (const medication of visitData.medications) {
      summary += `- ${medication}\n`;
    }
    
    summary += "\n";
  }
  
  // Add vital signs
  if (Object.keys(visitData.vitalSigns).length > 0) {
    summary += "## Vital Signs\n\n";
    
    for (const [key, value] of Object.entries(visitData.vitalSigns)) {
      // Convert camelCase to Title Case for display
      const formattedKey = key.replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase());
      
      summary += `- **${formattedKey}:** ${value}\n`;
    }
    
    summary += "\n";
  }
  
  // Add plan
  if (visitData.plan) {
    summary += "## Plan\n\n";
    summary += visitData.plan + "\n\n";
  }
  
  // Add follow-up
  if (visitData.followUp) {
    summary += "## Follow-up\n\n";
    summary += visitData.followUp + "\n\n";
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
  parseVisitNote,
  formatVisitSummary
}; 