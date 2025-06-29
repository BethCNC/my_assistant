// Clinical Notes Parser
// Specialized parser for extracting structured data from medical visit notes

/**
 * Extract key information from clinical visit notes
 * @param {string} content - The full text content of the clinical note
 * @returns {Object} Structured clinical data
 */
function parseClinicalNotes(content) {
  // Initialize result object
  const result = {
    visitType: null,
    visitDate: null,
    provider: null,
    providerTitle: null,
    department: null,
    facility: null,
    patientInfo: {},
    chiefComplaint: null,
    vitalSigns: {},
    historyOfPresentIllness: null,
    reviewOfSystems: null,
    physicalExam: null,
    assessment: [],
    diagnoses: [],
    plan: null,
    medications: [],
    followUp: null,
    proceduresPerformed: [],
    labOrders: [],
    imaging: []
  };
  
  // Extract visit type
  const visitTypeRegex = /(?:Visit Type|Appointment Type|Encounter Type|Type of Visit):?\s*([^\n]+)/i;
  const visitTypeMatch = content.match(visitTypeRegex);
  if (visitTypeMatch) {
    result.visitType = visitTypeMatch[1].trim();
  } else {
    // Try to identify by common types in the content
    const commonTypes = {
      "Office Visit": /\b(?:office visit|clinic visit|outpatient visit)\b/i,
      "Follow-Up": /\b(?:follow\s*up|follow-up)\b/i,
      "Consultation": /\b(?:consultation|consult|second opinion)\b/i,
      "New Patient": /\b(?:new patient|initial visit|initial consultation)\b/i,
      "Urgent Care": /\b(?:urgent care|walk-in|immediate care)\b/i,
      "Emergency": /\b(?:emergency|ER visit|ED visit)\b/i,
      "Telemedicine": /\b(?:telemedicine|telehealth|virtual visit|video visit)\b/i,
      "Procedure": /\b(?:procedure|surgery|operation)\b/i,
      "Annual Physical": /\b(?:annual|yearly|wellness|physical|check-up|preventive)\b/i
    };
    
    for (const [type, regex] of Object.entries(commonTypes)) {
      if (content.match(regex)) {
        result.visitType = type;
        break;
      }
    }
  }
  
  // Extract visit date
  const visitDateRegex = /(?:Visit Date|Date of Service|Encounter Date|Date of Visit|Date):?\s*([^\n]+)/i;
  const visitDateMatch = content.match(visitDateRegex);
  if (visitDateMatch) {
    result.visitDate = parseDate(visitDateMatch[1].trim());
  }
  
  // Extract provider information
  const providerRegex = /(?:Provider|Physician|Doctor|Clinician|Attending|PCP):?\s*(?:Dr\.)?\s*([^,\n]*(?:MD|DO|NP|PA)?[^,\n]*)/i;
  const providerMatch = content.match(providerRegex);
  if (providerMatch) {
    result.provider = providerMatch[1].trim();
    
    // Extract provider title
    const titleRegex = /(?:MD|DO|PhD|ARNP|PA-C|RN|NP|FNP|CNM)/i;
    const titleMatch = result.provider.match(titleRegex);
    if (titleMatch) {
      result.providerTitle = titleMatch[0];
      // Clean provider name
      result.provider = result.provider.replace(titleRegex, '').trim();
    }
  }
  
  // Extract department/specialty
  const departmentRegex = /(?:Department|Specialty|Service|Clinic|Division):?\s*([^\n]+)/i;
  const departmentMatch = content.match(departmentRegex);
  if (departmentMatch) {
    result.department = departmentMatch[1].trim();
  }
  
  // Extract facility information
  const facilityRegex = /(?:Facility|Hospital|Location|Clinic|Center|Office):?\s*([^\n]+)/i;
  const facilityMatch = content.match(facilityRegex);
  if (facilityMatch) {
    result.facility = facilityMatch[1].trim();
  }
  
  // Extract patient information
  const nameRegex = /(?:Patient|Name):?\s*([^\n]+)/i;
  const nameMatch = content.match(nameRegex);
  if (nameMatch) {
    result.patientInfo.name = nameMatch[1].trim();
  }
  
  const dobRegex = /(?:DOB|Date of Birth):?\s*([^\n]+)/i;
  const dobMatch = content.match(dobRegex);
  if (dobMatch) {
    result.patientInfo.dateOfBirth = parseDate(dobMatch[1].trim());
  }
  
  const mrnRegex = /(?:MRN|Medical Record Number|Chart|Patient ID):?\s*([^\n]+)/i;
  const mrnMatch = content.match(mrnRegex);
  if (mrnMatch) {
    result.patientInfo.mrn = mrnMatch[1].trim();
  }
  
  // Extract chief complaint
  result.chiefComplaint = extractSection(content, 
    /(?:Chief Complaint|CC|Reason for Visit|Presenting Problem|Reason|Presenting Complaint):?\s*([^]*?)(?=\n\s*(?:History|HPI|Past|Vital|Exam|Review|Assessment|Plan|Impression|$))/i);
  
  // Extract vital signs
  const vitalsSection = extractSection(content,
    /(?:Vital Signs|Vitals):?\s*([^]*?)(?=\n\s*(?:History|HPI|Past|Exam|Review|Assessment|Plan|Impression|$))/i);
  
  if (vitalsSection) {
    // Parse height
    const heightRegex = /(?:Height|Ht):\s*([0-9.]+)\s*(?:cm|in|feet|ft|\')/i;
    const heightMatch = vitalsSection.match(heightRegex);
    if (heightMatch) {
      result.vitalSigns.height = heightMatch[1].trim();
    }
    
    // Parse weight
    const weightRegex = /(?:Weight|Wt):\s*([0-9.]+)\s*(?:kg|lbs|pounds|lb)/i;
    const weightMatch = vitalsSection.match(weightRegex);
    if (weightMatch) {
      result.vitalSigns.weight = weightMatch[1].trim();
    }
    
    // Parse temperature
    const tempRegex = /(?:Temperature|Temp|T):\s*([0-9.]+)\s*(?:C|F|celsius|fahrenheit|°C|°F)/i;
    const tempMatch = vitalsSection.match(tempRegex);
    if (tempMatch) {
      result.vitalSigns.temperature = tempMatch[1].trim();
    }
    
    // Parse blood pressure
    const bpRegex = /(?:Blood Pressure|BP):\s*([0-9]+\/[0-9]+)\s*(?:mmHg)?/i;
    const bpMatch = vitalsSection.match(bpRegex);
    if (bpMatch) {
      result.vitalSigns.bloodPressure = bpMatch[1].trim();
    }
    
    // Parse pulse
    const pulseRegex = /(?:Pulse|Heart Rate|HR):\s*([0-9]+)\s*(?:bpm)?/i;
    const pulseMatch = vitalsSection.match(pulseRegex);
    if (pulseMatch) {
      result.vitalSigns.pulse = pulseMatch[1].trim();
    }
    
    // Parse respiration
    const respRegex = /(?:Respiratory Rate|Resp|RR):\s*([0-9]+)\s*(?:breaths\/min)?/i;
    const respMatch = vitalsSection.match(respRegex);
    if (respMatch) {
      result.vitalSigns.respiratoryRate = respMatch[1].trim();
    }
    
    // Parse oxygen saturation
    const o2Regex = /(?:Oxygen Saturation|O2 Sat|SpO2|SaO2|Oxygen|O2):\s*([0-9]+)%?/i;
    const o2Match = vitalsSection.match(o2Regex);
    if (o2Match) {
      result.vitalSigns.oxygenSaturation = o2Match[1].trim();
    }
    
    // Parse BMI
    const bmiRegex = /(?:BMI|Body Mass Index):\s*([0-9.]+)/i;
    const bmiMatch = vitalsSection.match(bmiRegex);
    if (bmiMatch) {
      result.vitalSigns.bmi = bmiMatch[1].trim();
    }
  }
  
  // Extract history of present illness
  result.historyOfPresentIllness = extractSection(content,
    /(?:History of Present Illness|HPI|Present Illness|History):?\s*([^]*?)(?=\n\s*(?:Past|Review|Physical|Vital|Exam|Assessment|Plan|Impression|$))/i);
  
  // Extract review of systems
  result.reviewOfSystems = extractSection(content,
    /(?:Review of Systems|ROS|Systems Review):?\s*([^]*?)(?=\n\s*(?:Physical|Exam|Assessment|Plan|Impression|$))/i);
  
  // Extract physical exam
  result.physicalExam = extractSection(content,
    /(?:Physical Examination|Physical Exam|Examination|Exam|PE):?\s*([^]*?)(?=\n\s*(?:Assessment|Plan|Impression|Diagnosis|$))/i);
  
  // Extract assessment & diagnoses
  const assessmentSection = extractSection(content,
    /(?:Assessment|Impression|Diagnosis|Diagnoses|Clinical Impression|A\/P|A&P):?\s*([^]*?)(?=\n\s*(?:Plan|Treatment|Follow|Disposition|Orders|Recommendations|Medications|$))/i);
  
  if (assessmentSection) {
    // Try to extract individual diagnoses
    const diagnosisLines = assessmentSection.split('\n');
    const diagnoses = [];
    
    // Regex patterns for diagnoses
    const diagnosisPatterns = [
      /^\s*\d+\.\s+(.+)$/,               // Numbered list: "1. Diagnosis"
      /^\s*[-•*]\s+(.+)$/,               // Bullet points: "• Diagnosis"
      /^\s*([A-Z][\w\s,]+(?:disease|disorder|syndrome|pain|infection|dysfunction|injury|fracture|symptoms|depression|anxiety))(?:[:.]\s*|\s*$)/i, // Common diagnostic terms
      /^\s*([^:]+):\s*(?:Confirmed|Suspected|Possible|Rule out|Chronic|Acute|Active|Resolved)/i // Followed by status
    ];
    
    for (const line of diagnosisLines) {
      if (line.trim().length === 0) continue;
      
      // Try to match each pattern
      for (const pattern of diagnosisPatterns) {
        const match = line.match(pattern);
        if (match) {
          const diagnosis = match[1].trim();
          // Skip if too short or common words
          if (diagnosis.length > 3 && 
              !diagnosis.match(/^(normal|negative|none|review|plan|see|patient|treatment)$/i)) {
            diagnoses.push(diagnosis);
          }
          break;
        }
      }
    }
    
    if (diagnoses.length > 0) {
      result.diagnoses = diagnoses;
    }
    
    // Also save the full assessment section
    result.assessment = assessmentSection;
  }
  
  // Extract plan
  result.plan = extractSection(content,
    /(?:Plan|Treatment Plan|Recommendations|Management|Disposition):?\s*([^]*?)(?=\n\s*(?:Follow|Disposition|Orders|Medications|$))/i);
  
  // Extract medications
  const medicationsSection = extractSection(content,
    /(?:Medications|Medication|Current Medications|Prescribed|Prescriptions|Meds):?\s*([^]*?)(?=\n\s*(?:Follow|Disposition|Orders|Plan|$))/i);
  
  if (medicationsSection) {
    // Try to extract individual medications
    const medicationLines = medicationsSection.split('\n');
    const medications = [];
    
    // Regex patterns for medications
    const medicationPatterns = [
      /^\s*\d+\.\s+(.+)$/,              // Numbered list: "1. Medication"
      /^\s*[-•*]\s+(.+)$/,              // Bullet points: "• Medication"
      /^\s*([A-Za-z0-9\s]+(?:\s+\d+\s*(?:mg|mcg|g|mL|pill|tablet|cap))(?:\/[A-Za-z0-9\s]+)?)(?:\s+\d+\s*times\s+(?:daily|a day|per day)|$)/i,    // Common medication formats
      /^\s*([A-Za-z0-9\s\-]+)\s+(?:\(\w+\))?\s*(?:\d+(?:\.\d+)?\s*(?:mg|mcg|g|mL|pill|tablet|cap))/i  // With dosage
    ];
    
    for (const line of medicationLines) {
      if (line.trim().length === 0) continue;
      
      // Try to match each pattern
      for (const pattern of medicationPatterns) {
        const match = line.match(pattern);
        if (match) {
          medications.push(line.trim());
          break;
        }
      }
    }
    
    if (medications.length > 0) {
      result.medications = medications;
    }
  }
  
  // Extract follow-up
  result.followUp = extractSection(content,
    /(?:Follow[\s-]*up|Return|Next Visit|Next Appointment):?\s*([^]*?)(?=\n\s*(?:Orders|Additional|Instructions|$))/i);
  
  // Extract procedures
  const proceduresSection = extractSection(content,
    /(?:Procedures|Procedure Performed|Surgery|Operation|Interventions):?\s*([^]*?)(?=\n\s*(?:Assessment|Plan|Impression|$))/i);
  
  if (proceduresSection) {
    // Try to extract individual procedures
    const procedureLines = proceduresSection.split('\n');
    const procedures = [];
    
    // Regex patterns for procedures
    const procedurePatterns = [
      /^\s*\d+\.\s+(.+)$/,             // Numbered list: "1. Procedure"
      /^\s*[-•*]\s+(.+)$/,             // Bullet points: "• Procedure"
      /^\s*([A-Z][A-Za-z\s\-]+(?:procedure|surgery|incision|removal|biopsy|excision|repair|injection|aspiration|catheter|therapy|test))(?:[:.]\s*|\s*$)/i // Common procedure terms
    ];
    
    for (const line of procedureLines) {
      if (line.trim().length === 0) continue;
      
      // Try to match each pattern
      for (const pattern of procedurePatterns) {
        const match = line.match(pattern);
        if (match) {
          procedures.push(match[1].trim());
          break;
        }
      }
    }
    
    if (procedures.length > 0) {
      result.proceduresPerformed = procedures;
    }
  }
  
  // Extract lab orders
  const labSection = extractSection(content,
    /(?:Laboratory|Lab(?:oratory)? Tests|Lab(?:oratory)? Orders|Tests Ordered):?\s*([^]*?)(?=\n\s*(?:Imaging|Radiology|Assessment|Plan|Impression|$))/i);
  
  if (labSection) {
    // Try to extract individual lab orders
    const labLines = labSection.split('\n');
    const labs = [];
    
    // Regex patterns for labs
    const labPatterns = [
      /^\s*\d+\.\s+(.+)$/,             // Numbered list: "1. Lab test"
      /^\s*[-•*]\s+(.+)$/,             // Bullet points: "• Lab test"
      /^\s*([A-Z][A-Za-z\s\-]+(?:panel|test|level|count|culture|screen|profile|assessment|function))(?:[:.]\s*|\s*$)/i // Common lab terms
    ];
    
    for (const line of labLines) {
      if (line.trim().length === 0) continue;
      
      // Try to match each pattern
      for (const pattern of labPatterns) {
        const match = line.match(pattern);
        if (match) {
          labs.push(match[1].trim());
          break;
        }
      }
    }
    
    if (labs.length > 0) {
      result.labOrders = labs;
    }
  }
  
  // Extract imaging
  const imagingSection = extractSection(content,
    /(?:Imaging|Radiology|Diagnostic|X-ray|CT|MRI|Ultrasound|Imaging Studies):?\s*([^]*?)(?=\n\s*(?:Assessment|Plan|Impression|$))/i);
  
  if (imagingSection) {
    // Try to extract individual imaging orders
    const imagingLines = imagingSection.split('\n');
    const imaging = [];
    
    // Regex patterns for imaging
    const imagingPatterns = [
      /^\s*\d+\.\s+(.+)$/,             // Numbered list: "1. Imaging test"
      /^\s*[-•*]\s+(.+)$/,             // Bullet points: "• Imaging test"
      /^\s*([A-Z][A-Za-z\s\-]+(?:x-ray|MRI|CT|ultrasound|scan|imaging|sonogram|mammogram|nuclear|PET))(?:[:.]\s*|\s*$)/i // Common imaging terms
    ];
    
    for (const line of imagingLines) {
      if (line.trim().length === 0) continue;
      
      // Try to match each pattern
      for (const pattern of imagingPatterns) {
        const match = line.match(pattern);
        if (match) {
          imaging.push(match[1].trim());
          break;
        }
      }
    }
    
    if (imaging.length > 0) {
      result.imaging = imaging;
    }
  }
  
  return result;
}

/**
 * Extract a section from the clinical note based on a regex pattern
 * @param {string} content - The full text content
 * @param {RegExp} sectionPattern - Regex pattern to extract the section
 * @returns {string|null} The extracted section or null if not found
 */
function extractSection(content, sectionPattern) {
  const match = content.match(sectionPattern);
  if (match && match[1]) {
    return match[1].trim();
  }
  return null;
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
 * Format clinical note data into a structured summary
 * @param {Object} clinicalData - The parsed clinical data
 * @returns {string} Formatted summary text
 */
function formatClinicalSummary(clinicalData) {
  let summary = "";
  
  // Visit title and date
  const visitTypes = {
    "Office Visit": "Office Visit",
    "Follow-Up": "Follow-Up Visit",
    "Consultation": "Consultation",
    "New Patient": "New Patient Visit",
    "Urgent Care": "Urgent Care Visit",
    "Emergency": "Emergency Visit",
    "Telemedicine": "Telemedicine Visit",
    "Procedure": "Procedure",
    "Annual Physical": "Annual Physical"
  };
  
  const visitType = visitTypes[clinicalData.visitType] || "Medical Visit";
  
  if (clinicalData.visitDate) {
    const formattedDate = formatDate(clinicalData.visitDate);
    summary += `# ${visitType} - ${formattedDate}\n\n`;
  } else {
    summary += `# ${visitType}\n\n`;
  }
  
  // Add provider info
  if (clinicalData.provider) {
    let providerInfo = `**Provider:** ${clinicalData.provider}`;
    if (clinicalData.providerTitle) {
      providerInfo += `, ${clinicalData.providerTitle}`;
    }
    summary += providerInfo + "\n";
  }
  
  // Add department/specialty
  if (clinicalData.department) {
    summary += `**Department/Specialty:** ${clinicalData.department}\n`;
  }
  
  // Add facility
  if (clinicalData.facility) {
    summary += `**Facility:** ${clinicalData.facility}\n`;
  }
  
  summary += "\n";
  
  // Add chief complaint
  if (clinicalData.chiefComplaint) {
    summary += `## Chief Complaint / Reason for Visit\n\n${clinicalData.chiefComplaint}\n\n`;
  }
  
  // Add vital signs
  if (Object.keys(clinicalData.vitalSigns).length > 0) {
    summary += "## Vital Signs\n\n";
    
    for (const [key, value] of Object.entries(clinicalData.vitalSigns)) {
      if (value) {
        let label;
        let formattedValue = value;
        
        switch (key) {
          case "height":
            label = "Height";
            break;
          case "weight":
            label = "Weight";
            break;
          case "temperature":
            label = "Temperature";
            break;
          case "bloodPressure":
            label = "Blood Pressure";
            break;
          case "pulse":
            label = "Pulse";
            formattedValue = `${value} bpm`;
            break;
          case "respiratoryRate":
            label = "Respiratory Rate";
            formattedValue = `${value} breaths/min`;
            break;
          case "oxygenSaturation":
            label = "Oxygen Saturation";
            formattedValue = `${value}%`;
            break;
          case "bmi":
            label = "BMI";
            break;
          default:
            label = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
        }
        
        summary += `- **${label}:** ${formattedValue}\n`;
      }
    }
    
    summary += "\n";
  }
  
  // Add history of present illness
  if (clinicalData.historyOfPresentIllness) {
    summary += `## History of Present Illness\n\n${clinicalData.historyOfPresentIllness}\n\n`;
  }
  
  // Add procedures if performed
  if (clinicalData.proceduresPerformed && clinicalData.proceduresPerformed.length > 0) {
    summary += "## Procedures Performed\n\n";
    
    clinicalData.proceduresPerformed.forEach(procedure => {
      summary += `- ${procedure}\n`;
    });
    
    summary += "\n";
  }
  
  // Add assessment and diagnoses
  if (clinicalData.diagnoses && clinicalData.diagnoses.length > 0) {
    summary += "## Diagnoses\n\n";
    
    clinicalData.diagnoses.forEach((diagnosis, index) => {
      summary += `${index + 1}. ${diagnosis}\n`;
    });
    
    summary += "\n";
  } else if (clinicalData.assessment) {
    summary += `## Assessment\n\n${clinicalData.assessment}\n\n`;
  }
  
  // Add plan
  if (clinicalData.plan) {
    summary += `## Plan\n\n${clinicalData.plan}\n\n`;
  }
  
  // Add medications
  if (clinicalData.medications && clinicalData.medications.length > 0) {
    summary += "## Medications\n\n";
    
    clinicalData.medications.forEach(medication => {
      summary += `- ${medication}\n`;
    });
    
    summary += "\n";
  }
  
  // Add lab orders
  if (clinicalData.labOrders && clinicalData.labOrders.length > 0) {
    summary += "## Lab Orders\n\n";
    
    clinicalData.labOrders.forEach(lab => {
      summary += `- ${lab}\n`;
    });
    
    summary += "\n";
  }
  
  // Add imaging
  if (clinicalData.imaging && clinicalData.imaging.length > 0) {
    summary += "## Imaging\n\n";
    
    clinicalData.imaging.forEach(image => {
      summary += `- ${image}\n`;
    });
    
    summary += "\n";
  }
  
  // Add follow-up
  if (clinicalData.followUp) {
    summary += `## Follow-Up\n\n${clinicalData.followUp}\n\n`;
  }
  
  // Add a review of systems if available
  if (clinicalData.reviewOfSystems) {
    summary += `## Review of Systems\n\n${clinicalData.reviewOfSystems}\n\n`;
  }
  
  // Add physical exam if available
  if (clinicalData.physicalExam) {
    summary += `## Physical Examination\n\n${clinicalData.physicalExam}\n\n`;
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
  parseClinicalNotes,
  formatClinicalSummary
}; 