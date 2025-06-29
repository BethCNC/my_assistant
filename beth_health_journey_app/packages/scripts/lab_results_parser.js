// Lab Results Parser
// Specialized parser for extracting structured data from medical lab reports

/**
 * Extract key information from lab results
 * @param {string} content - The full text content of the lab report
 * @returns {Object} Structured lab data
 */
function parseLabResults(content) {
  // Initialize result object
  const result = {
    testName: null,
    testType: null,
    collectionDate: null,
    reportDate: null,
    provider: null,
    facility: null,
    patientInfo: {},
    results: [],
    abnormalFlags: [],
    comments: null,
    conclusions: null
  };
  
  // Extract test name/type
  const testNameRegex = /(?:Test|Procedure|Lab|Examination|Study)(?:\s+Name)?:?\s*([^\n]+)/i;
  const testNameMatch = content.match(testNameRegex);
  if (testNameMatch) {
    result.testName = testNameMatch[1].trim();
  } else {
    // Try to identify by common test names in the content
    const commonTests = [
      "Complete Blood Count", "CBC", 
      "Comprehensive Metabolic Panel", "CMP", "Basic Metabolic Panel", "BMP",
      "Thyroid Stimulating Hormone", "TSH", "Free T4", "Free T3",
      "Lipid Panel", "Cholesterol", "Triglycerides", "HDL", "LDL",
      "Hemoglobin A1C", "HbA1c", 
      "Urinalysis", "Urine Culture",
      "Vitamin D", "Vitamin B12",
      "C-Reactive Protein", "CRP", "Sedimentation Rate", "ESR",
      "Liver Function", "LFT",
      "Blood Culture",
      "Ferritin", "Iron",
      "Folate", "Folic Acid"
    ];
    
    for (const test of commonTests) {
      const testRegex = new RegExp(`\\b${test}\\b`, 'i');
      
      if (content.match(testRegex)) {
        result.testName = test;
        break;
      }
    }
  }
  
  // Try to determine test type if not specified
  if (!result.testType) {
    if (content.match(/blood|cbc|bmp|cmp|thyroid|lipid|panel|serum|plasma|complete blood|a1c|hemoglobin|metabolic/i)) {
      result.testType = "Blood Test";
    } else if (content.match(/urine|urinalysis|urology|bladder|kidney|renal/i)) {
      result.testType = "Urine Test";
    } else if (content.match(/stool|fecal|feces|colorectal|bowel|intestinal/i)) {
      result.testType = "Stool Test";
    } else if (content.match(/culture|bacteria|fungal|viral|pathogen|microb/i)) {
      result.testType = "Culture";
    } else if (content.match(/imaging|xray|x-ray|scan|ct|mri|ultrasound|sonogram|radiology/i)) {
      result.testType = "Imaging";
    } else if (content.match(/biopsy|pathology|cytology|specimen|tissue/i)) {
      result.testType = "Biopsy/Pathology";
    }
  }
  
  // Extract collection date
  const collectionDateRegex = /(?:Collection Date|Collected|Specimen Collected|Specimen Date|Date Collected|Drawn|Date Drawn|Sample Date):?\s*([^\n]+)/i;
  const collectionDateMatch = content.match(collectionDateRegex);
  if (collectionDateMatch) {
    result.collectionDate = parseDate(collectionDateMatch[1].trim());
  }
  
  // Extract report date
  const reportDateRegex = /(?:Report Date|Date Reported|Resulted|Result Date|Date of Result|Date of Report):?\s*([^\n]+)/i;
  const reportDateMatch = content.match(reportDateRegex);
  if (reportDateMatch) {
    result.reportDate = parseDate(reportDateMatch[1].trim());
  } else if (!result.collectionDate) {
    // If no specific dates found, look for any date
    const dateRegex = /(?:Date):?\s*([^\n]+)/i;
    const dateMatch = content.match(dateRegex);
    if (dateMatch) {
      result.collectionDate = parseDate(dateMatch[1].trim());
    }
  }
  
  // Extract ordering provider
  const providerRegex = /(?:Ordering (?:Provider|Doctor|Physician)|Physician|Ordered By|Provider|Doctor|Ordered by|Requesting):?\s*([^,\n]*(?:MD|DO|NP|PA)?[^,\n]*)/i;
  const providerMatch = content.match(providerRegex);
  if (providerMatch) {
    result.provider = providerMatch[1].trim();
  }
  
  // Extract facility/lab
  const facilityRegex = /(?:Facility|Lab(?:oratory)?|Location|Performed at|Performed by):?\s*([^\n]+)/i;
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
  
  // Parse test results - try different strategies
  parseTestResults(content, result);
  
  // Extract comments or notes
  const commentsRegex = /(?:Comments|Notes|Interpretation|Remarks|Impression):?\s*([^]*?)(?:\n\n|\n[A-Z]|Conclusion|Summary|$)/i;
  const commentsMatch = content.match(commentsRegex);
  if (commentsMatch) {
    result.comments = commentsMatch[1].trim();
  }
  
  // Extract conclusions
  const conclusionsRegex = /(?:Conclusion|Summary|Impression|Assessment|Final Diagnosis):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
  const conclusionsMatch = content.match(conclusionsRegex);
  if (conclusionsMatch) {
    result.conclusions = conclusionsMatch[1].trim();
  }
  
  return result;
}

/**
 * Parse test results section using different strategies
 * @param {string} content - The full text content
 * @param {Object} result - The result object to populate
 */
function parseTestResults(content, result) {
  // First strategy: Look for structured tables with test name, result, reference range
  const tablePattern = /\s*([\w\s\-\(\)\/\%]+)\s*\|\s*([\w\s\.\-\+\<\>\=\/]+)\s*\|\s*([\w\s\.\-\<\>\/\=\+\-]+)\s*(?:\||$)/g;
  let tableMatch;
  let tableFound = false;
  
  while ((tableMatch = tablePattern.exec(content)) !== null) {
    const testName = tableMatch[1].trim();
    const testResult = tableMatch[2].trim();
    const referenceRange = tableMatch[3].trim();
    
    // Ignore headers or short names
    if (testName.length < 2 || 
        testName.match(/^(test|name|parameter|component|analyte|examination|result|value|normal|reference|range|unit)$/i)) {
      continue;
    }
    
    tableFound = true;
    
    const resultObj = {
      testName: testName,
      value: testResult,
      unit: extractUnit(testResult),
      referenceRange: referenceRange,
      isAbnormal: isAbnormalResult(testResult, referenceRange)
    };
    
    result.results.push(resultObj);
    
    if (resultObj.isAbnormal) {
      result.abnormalFlags.push(testName);
    }
  }
  
  // If no table format found, try colon-separated format: "Test Name: Result (Reference Range)"
  if (!tableFound) {
    const colonPattern = /([\w\s\-\(\)\/\%]+):\s*([\w\s\.\-\+\<\>\=\/]+)(?:\s*\(([^\)]+)\))?/g;
    let colonMatch;
    
    while ((colonMatch = colonPattern.exec(content)) !== null) {
      const testName = colonMatch[1].trim();
      const testResult = colonMatch[2].trim();
      const referenceRange = colonMatch[3] ? colonMatch[3].trim() : '';
      
      // Ignore headers or non-test information
      if (testName.length < 2 || 
          testName.match(/^(patient|name|dob|date|id|mrn|physician|provider|facility|lab|collected|reported)$/i)) {
        continue;
      }
      
      const resultObj = {
        testName: testName,
        value: testResult,
        unit: extractUnit(testResult),
        referenceRange: referenceRange,
        isAbnormal: isAbnormalResult(testResult, referenceRange)
      };
      
      result.results.push(resultObj);
      
      if (resultObj.isAbnormal) {
        result.abnormalFlags.push(testName);
      }
    }
  }
  
  // If still no results, try to find lines with "H" or "L" flags for abnormal values
  if (result.results.length === 0) {
    const flagPattern = /([\w\s\-\(\)\/\%]+)\s+([\d\.]+\s*[\w\/%]+)\s+([HL])\s+([\d\.\-\s\<\>]+\s*[\w\/%]+)/g;
    let flagMatch;
    
    while ((flagMatch = flagPattern.exec(content)) !== null) {
      const testName = flagMatch[1].trim();
      const testResult = flagMatch[2].trim();
      const flag = flagMatch[3].trim();
      const referenceRange = flagMatch[4].trim();
      
      const resultObj = {
        testName: testName,
        value: testResult,
        unit: extractUnit(testResult),
        referenceRange: referenceRange,
        isAbnormal: flag === 'H' || flag === 'L'
      };
      
      result.results.push(resultObj);
      
      if (resultObj.isAbnormal) {
        result.abnormalFlags.push(testName);
      }
    }
  }
}

/**
 * Extract unit from a test result value
 * @param {string} value - The test result value
 * @returns {string|null} Extracted unit or null if none found
 */
function extractUnit(value) {
  if (!value) return null;
  
  // Common units pattern
  const unitPattern = /(?:[\d\.]+)\s*(mg\/dL|g\/dL|mmol\/L|μmol\/L|ng\/mL|pg\/mL|mIU\/L|U\/L|IU\/L|µg\/dL|mEq\/L|mmHg|µg\/L|ng\/dL|pmol\/L|mm\/hr|cells\/μL|k\/μL|g\/L|%|cm|mm|kg\/m2|μg\/mL)/i;
  const unitMatch = value.match(unitPattern);
  
  if (unitMatch) {
    return unitMatch[1];
  }
  
  return null;
}

/**
 * Determine if a test result is abnormal
 * @param {string} value - The test result value
 * @param {string} referenceRange - The reference range
 * @returns {boolean} True if result is abnormal
 */
function isAbnormalResult(value, referenceRange) {
  if (!value) return false;
  
  // Check for explicit flags
  if (value.match(/\b(H|HIGH|ELEVATED|ABNORMAL|POSITIVE|POS|L|LOW|DECREASED)\b/i)) {
    return true;
  }
  
  // Check if value is outside numerical reference range
  if (referenceRange) {
    // Extract the numeric part of the value
    const numericValue = parseFloat(value.replace(/[^\d\.]/g, ''));
    
    if (!isNaN(numericValue)) {
      // Check for ranges specified as min-max
      const rangeMatch = referenceRange.match(/([\d\.]+)\s*-\s*([\d\.]+)/);
      if (rangeMatch) {
        const min = parseFloat(rangeMatch[1]);
        const max = parseFloat(rangeMatch[2]);
        
        if (!isNaN(min) && !isNaN(max)) {
          return numericValue < min || numericValue > max;
        }
      }
      
      // Check for less than or greater than ranges
      const ltMatch = referenceRange.match(/< *([\d\.]+)/);
      if (ltMatch) {
        const max = parseFloat(ltMatch[1]);
        if (!isNaN(max)) {
          return numericValue >= max;
        }
      }
      
      const gtMatch = referenceRange.match(/> *([\d\.]+)/);
      if (gtMatch) {
        const min = parseFloat(gtMatch[1]);
        if (!isNaN(min)) {
          return numericValue <= min;
        }
      }
    }
  }
  
  return false;
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
 * Format lab results data into a structured summary
 * @param {Object} labData - The parsed lab data
 * @returns {string} Formatted summary text
 */
function formatLabSummary(labData) {
  let summary = "";
  
  // Lab test title and date
  if (labData.testName) {
    if (labData.collectionDate) {
      const formattedDate = formatDate(labData.collectionDate);
      summary += `# ${labData.testName} - ${formattedDate}\n\n`;
    } else if (labData.reportDate) {
      const formattedDate = formatDate(labData.reportDate);
      summary += `# ${labData.testName} - ${formattedDate}\n\n`;
    } else {
      summary += `# ${labData.testName}\n\n`;
    }
  } else {
    summary += `# Laboratory Results\n\n`;
  }
  
  // Add test type if available
  if (labData.testType) {
    summary += `**Test Type:** ${labData.testType}\n`;
  }
  
  // Add dates
  if (labData.collectionDate) {
    summary += `**Collection Date:** ${formatDate(labData.collectionDate)}\n`;
  }
  
  if (labData.reportDate) {
    summary += `**Report Date:** ${formatDate(labData.reportDate)}\n`;
  }
  
  // Add provider and facility info
  if (labData.provider) {
    summary += `**Ordering Provider:** ${labData.provider}\n`;
  }
  
  if (labData.facility) {
    summary += `**Facility/Laboratory:** ${labData.facility}\n`;
  }
  
  summary += "\n";
  
  // Highlight abnormal results first if present
  if (labData.abnormalFlags.length > 0) {
    summary += "## Abnormal Results\n\n";
    
    // Find all abnormal results
    const abnormalResults = labData.results.filter(result => result.isAbnormal);
    
    abnormalResults.forEach(result => {
      summary += `- **${result.testName}:** ${result.value}`;
      if (result.referenceRange) {
        summary += ` (Reference Range: ${result.referenceRange})`;
      }
      summary += "\n";
    });
    
    summary += "\n";
  }
  
  // Add all test results
  if (labData.results.length > 0) {
    summary += "## All Results\n\n";
    
    summary += "| Test | Result | Reference Range | Status |\n";
    summary += "|------|--------|----------------|--------|\n";
    
    labData.results.forEach(result => {
      const status = result.isAbnormal ? "**ABNORMAL**" : "Normal";
      
      summary += `| ${result.testName} | ${result.value} | ${result.referenceRange || 'N/A'} | ${status} |\n`;
    });
    
    summary += "\n";
  }
  
  // Add comments/interpretation
  if (labData.comments) {
    summary += `## Comments\n\n${labData.comments}\n\n`;
  }
  
  // Add conclusions
  if (labData.conclusions) {
    summary += `## Conclusions\n\n${labData.conclusions}\n\n`;
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
  parseLabResults,
  formatLabSummary
}; 