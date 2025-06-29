// Lab Result Parser
// Specialized parser for extracting structured data from lab result reports

/**
 * Extract key information from lab result text
 * @param {string} content - The full text content of the lab report
 * @returns {Object} Structured lab result data
 */
function parseLabResult(content) {
  // Initialize result object
  const result = {
    testName: null,
    testDate: null,
    collectionDate: null,
    reportDate: null,
    provider: null,
    facility: null,
    patientInfo: {},
    results: [],
    abnormalResults: [],
    interpretation: null,
    followUpRecommendations: null
  };
  
  // Extract test name
  const testNameRegex = /(?:Test Name|Test|Procedure|Lab|Laboratory|Lab Test):?\s*([^\n]+)/i;
  const testNameMatch = content.match(testNameRegex);
  if (testNameMatch) {
    result.testName = testNameMatch[1].trim();
  } else {
    // Try to infer test name from headers or content
    const possibleHeaders = [
      /CBC(?:\s+with\s+Differential)?/i,
      /Complete Blood Count/i,
      /Basic Metabolic Panel/i,
      /Comprehensive Metabolic Panel/i,
      /Lipid Panel/i,
      /Thyroid(?:\s+Function)?\s+Test/i,
      /Hemoglobin A1C/i,
      /Urinalysis/i,
      /Liver\s+Function\s+Test/i,
      /TSH/i,
      /MRI/i,
      /CT\s+Scan/i,
      /X-Ray/i,
      /Ultrasound/i
    ];
    
    for (const regex of possibleHeaders) {
      const match = content.match(regex);
      if (match) {
        result.testName = match[0].trim();
        break;
      }
    }
  }
  
  // Extract dates
  const collectionDateRegex = /(?:Collection Date|Collected|Specimen Collection|Collected On|Collection Time):?\s*([^\n]+)/i;
  const collectionDateMatch = content.match(collectionDateRegex);
  if (collectionDateMatch) {
    result.collectionDate = parseDate(collectionDateMatch[1].trim());
  }
  
  const reportDateRegex = /(?:Report Date|Reported|Date Reported|Reported On|Completion Date):?\s*([^\n]+)/i;
  const reportDateMatch = content.match(reportDateRegex);
  if (reportDateMatch) {
    result.reportDate = parseDate(reportDateMatch[1].trim());
  }
  
  // If we have collection or report date but not test date, use one of those
  if (!result.testDate) {
    result.testDate = result.collectionDate || result.reportDate;
  }
  
  // Extract provider information
  const providerRegex = /(?:Provider|Physician|Doctor|Ordering Provider|Ordered By):?\s*([^,\n]*(?:MD|DO|NP|PA)?[^,\n]*)/i;
  const providerMatch = content.match(providerRegex);
  if (providerMatch) {
    result.provider = providerMatch[1].trim();
  }
  
  // Extract facility information
  const facilityRegex = /(?:Facility|Laboratory|Lab|Clinic|Location|Testing Facility):?\s*([^\n]+)/i;
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
  
  // Extract test results
  extractTestResults(content, result);
  
  // Extract interpretation/summary
  const interpretationRegex = /(?:Interpretation|Impression|Summary|Conclusion|Assessment|Comment):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
  const interpretationMatch = content.match(interpretationRegex);
  if (interpretationMatch) {
    result.interpretation = interpretationMatch[1].trim();
  }
  
  // Extract follow-up recommendations
  const followUpRegex = /(?:Follow-up|Recommendation|Suggested Follow-up|Further Testing):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
  const followUpMatch = content.match(followUpRegex);
  if (followUpMatch) {
    result.followUpRecommendations = followUpMatch[1].trim();
  }
  
  return result;
}

/**
 * Extract individual test results from the lab report content
 * @param {string} content - The full text content of the lab report
 * @param {Object} result - The result object to populate
 */
function extractTestResults(content, result) {
  // Try to find the results section
  const resultsSectionRegex = /(?:Results|Test Results|Laboratory Results|Laboratory Data|RESULTS|LABORATORY DATA):?\s*([^]*?)(?:\n\n|\n[A-Z]|Interpretation|Assessment|Comment|$)/i;
  const resultsSectionMatch = content.match(resultsSectionRegex);
  
  if (resultsSectionMatch) {
    const resultsText = resultsSectionMatch[1].trim();
    
    // Method 1: Look for structured result lines
    // Pattern: Test Name Result Units Reference Range Flag
    const resultLineRegex = /([A-Za-z0-9\s\-\(\)]+?)[\s:]+([<>]?\s*\d+\.?\d*\s*(?:-\s*\d+\.?\d*)?|(?:Positive|Negative|Normal|Abnormal|Detected|Not Detected|Reactive|Non-Reactive))(?:\s+([A-Za-z\/%]+))?(?:\s+\(([^)]+)\))?(?:\s+([HL]|\*|Abnormal|High|Low|Critical|Outside Reference Range))?/g;
    
    let resultMatch;
    while ((resultMatch = resultLineRegex.exec(resultsText)) !== null) {
      // Extract result components
      const testName = resultMatch[1]?.trim();
      const resultValue = resultMatch[2]?.trim();
      const unit = resultMatch[3]?.trim() || "";
      const referenceRange = resultMatch[4]?.trim() || "";
      const flag = resultMatch[5]?.trim();
      
      // Check if we have valid test name and result value
      if (testName && resultValue && testName.length > 1 && !testName.match(/^(?:name|test|result|value|lab|unit|range)$/i)) {
        const resultObj = {
          name: testName,
          value: resultValue,
          unit: unit,
          referenceRange: referenceRange,
          isAbnormal: !!flag
        };
        
        result.results.push(resultObj);
        
        if (resultObj.isAbnormal) {
          result.abnormalResults.push(resultObj);
        }
      }
    }
    
    // Method 2: Try to find results in tabular format
    if (result.results.length === 0) {
      const lines = resultsText.split('\n');
      let currentTest = null;
      
      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine) continue;
        
        // Check if line looks like a test name
        if (trimmedLine.match(/^[A-Za-z\s\-\(\)]+:$/)) {
          currentTest = trimmedLine.replace(/:$/, '').trim();
        } 
        // Check if line contains a result value with possibly a reference range
        else if (currentTest && trimmedLine.match(/[\d\.]+/)) {
          // Try to split and extract components
          const parts = trimmedLine.split(/\s+/);
          if (parts.length >= 1) {
            let resultValue = parts[0];
            let unit = parts.length >= 2 ? parts[1] : "";
            let referenceRange = "";
            let isAbnormal = false;
            
            // Look for reference range in parentheses
            const rangeMatch = trimmedLine.match(/\(([^)]+)\)/);
            if (rangeMatch) {
              referenceRange = rangeMatch[1];
            }
            
            // Check for abnormal flags
            if (trimmedLine.includes('*') || 
                trimmedLine.includes('H') || 
                trimmedLine.includes('L') || 
                trimmedLine.includes('HIGH') || 
                trimmedLine.includes('LOW') ||
                trimmedLine.includes('ABNORMAL') ||
                trimmedLine.includes('CRITICAL')) {
              isAbnormal = true;
            }
            
            const resultObj = {
              name: currentTest,
              value: resultValue,
              unit: unit,
              referenceRange: referenceRange,
              isAbnormal: isAbnormal
            };
            
            result.results.push(resultObj);
            
            if (isAbnormal) {
              result.abnormalResults.push(resultObj);
            }
          }
        }
      }
    }
    
    // Method 3: Try to find imaging or pathology results
    if (result.results.length === 0 && (
        content.includes('RADIOLOGY') || 
        content.includes('IMAGING') || 
        content.includes('PATHOLOGY') ||
        content.includes('MRI') ||
        content.includes('CT SCAN') ||
        content.includes('X-RAY') ||
        content.includes('ULTRASOUND')
    )) {
      // For imaging reports, often the entire findings section is the result
      const findingsRegex = /(?:FINDINGS|IMPRESSION|INTERPRETATION|DIAGNOSIS):?\s*([^]*?)(?:\n\n|\n[A-Z]|$)/i;
      const findingsMatch = content.match(findingsRegex);
      
      if (findingsMatch) {
        const findings = findingsMatch[1].trim();
        result.results.push({
          name: result.testName || "Imaging Results",
          value: findings,
          unit: "",
          referenceRange: "Normal Findings",
          isAbnormal: findings.toLowerCase().includes('abnormal') || findings.toLowerCase().includes('concerning')
        });
        
        // If abnormal, add to abnormal results
        if (result.results[0].isAbnormal) {
          result.abnormalResults.push(result.results[0]);
        }
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
 * Format lab result data into a structured summary
 * @param {Object} labData - The parsed lab result data
 * @returns {string} Formatted summary text
 */
function formatLabSummary(labData) {
  let summary = "";
  
  // Add test name and date as title
  if (labData.testName) {
    if (labData.testDate) {
      const formattedDate = formatDate(labData.testDate);
      summary += `# ${labData.testName} - ${formattedDate}\n\n`;
    } else {
      summary += `# ${labData.testName}\n\n`;
    }
  } else {
    summary += `# Lab Results\n\n`;
  }
  
  // Add provider and facility info
  if (labData.provider) {
    summary += `**Ordering Provider:** ${labData.provider}\n`;
  }
  
  if (labData.facility) {
    summary += `**Testing Facility:** ${labData.facility}\n`;
  }
  
  // Add date information
  if (labData.collectionDate) {
    summary += `**Collection Date:** ${formatDate(labData.collectionDate)}\n`;
  }
  
  if (labData.reportDate) {
    summary += `**Report Date:** ${formatDate(labData.reportDate)}\n`;
  }
  
  summary += "\n";
  
  // Add abnormal results first for quick reference
  if (labData.abnormalResults.length > 0) {
    summary += "## Abnormal Results\n\n";
    
    summary += "| Test | Result | Reference Range |\n";
    summary += "|------|--------|----------------|\n";
    
    for (const result of labData.abnormalResults) {
      // Format with unit if available
      const valueWithUnit = result.unit ? `${result.value} ${result.unit}` : result.value;
      
      summary += `| **${result.name}** | **${valueWithUnit}** | ${result.referenceRange} |\n`;
    }
    
    summary += "\n";
  }
  
  // Add all results
  if (labData.results.length > 0) {
    summary += "## All Results\n\n";
    
    // For imaging or text-based results
    if (labData.results.length === 1 && !labData.results[0].unit && labData.results[0].value.length > 50) {
      summary += labData.results[0].value + "\n\n";
    } else {
      // For typical lab numeric results
      summary += "| Test | Result | Reference Range |\n";
      summary += "|------|--------|----------------|\n";
      
      for (const result of labData.results) {
        // Format with unit if available
        const valueWithUnit = result.unit ? `${result.value} ${result.unit}` : result.value;
        
        // Mark abnormal results with bold
        if (result.isAbnormal) {
          summary += `| **${result.name}** | **${valueWithUnit}** | ${result.referenceRange} |\n`;
        } else {
          summary += `| ${result.name} | ${valueWithUnit} | ${result.referenceRange} |\n`;
        }
      }
      
      summary += "\n";
    }
  }
  
  // Add interpretation
  if (labData.interpretation) {
    summary += "## Interpretation\n\n";
    summary += labData.interpretation + "\n\n";
  }
  
  // Add follow-up recommendations
  if (labData.followUpRecommendations) {
    summary += "## Follow-up Recommendations\n\n";
    summary += labData.followUpRecommendations + "\n\n";
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
  parseLabResult,
  formatLabSummary
}; 