import * as XLSX from 'xlsx'

/**
 * File to Rubric Grid Converter
 * Handles parsing CSV and XLSX files and converting them to the rubric grid format
 */

/**
 * Parse CSV string and convert to 2D array
 * @param {string} csvString - Raw CSV content
 * @returns {Array<Array<string>>} 2D array representation of CSV
 */
export const parseCSV = (csvString) => {
  const lines = csvString.split('\n').filter(line => line.trim() !== '')
  const result = []
  
  for (let line of lines) {
    const row = []
    let current = ''
    let inQuotes = false
    
    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      
      if (char === '"') {
        inQuotes = !inQuotes
      } else if (char === ',' && !inQuotes) {
        row.push(current.trim())
        current = ''
      } else {
        current += char
      }
    }
    
    // Add the last field
    row.push(current.trim())
    result.push(row)
  }
  
  return result
}

/**
 * Parse XLSX file and convert to 2D array
 * @param {ArrayBuffer} arrayBuffer - XLSX file as ArrayBuffer
 * @returns {Array<Array<string>>} 2D array representation of XLSX
 */
export const parseXLSX = (arrayBuffer) => {
  try {
    const workbook = XLSX.read(arrayBuffer, { type: 'array' })
    const sheetName = workbook.SheetNames[0] // Use first sheet
    const worksheet = workbook.Sheets[sheetName]
    
    // Convert to 2D array
    const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 })
    
    // Convert all values to strings and handle undefined/null
    return data.map(row => 
      row.map(cell => {
        if (cell === undefined || cell === null) return ''
        return String(cell).trim()
      })
    )
  } catch (error) {
    throw new Error(`Failed to parse XLSX: ${error.message}`)
  }
}

/**
 * Convert file (CSV or XLSX) to rubric grid format
 * @param {File} file - File object (CSV or XLSX)
 * @returns {Promise<Array<Array<string>>>} Promise that resolves to rubric grid
 */
export const convertFileToRubric = async (file) => {
  return new Promise((resolve, reject) => {
    const fileName = file.name.toLowerCase()
    const isCSV = fileName.endsWith('.csv')
    const isXLSX = fileName.endsWith('.xlsx') || fileName.endsWith('.xls')
    
    if (!isCSV && !isXLSX) {
      reject(new Error('Unsupported file format. Please use CSV or XLSX files.'))
      return
    }
    
    if (isCSV) {
      // Handle CSV files
      const reader = new FileReader()
      
      reader.onload = (event) => {
        try {
          const csvString = event.target.result
          const parsedData = parseCSV(csvString)
          
          // Ensure we have at least 2 rows and 2 columns
          if (parsedData.length < 2 || parsedData[0].length < 2) {
            throw new Error('File must have at least 2 rows and 2 columns')
          }
          
          // Clean up the data - remove empty rows/columns and trim whitespace
          const cleanedData = parsedData
            .filter(row => row.some(cell => cell.trim() !== ''))
            .map(row => row.map(cell => cell.trim()))
          
          resolve(cleanedData)
        } catch (error) {
          reject(new Error(`Failed to parse CSV: ${error.message}`))
        }
      }
      
      reader.onerror = () => {
        reject(new Error('Failed to read CSV file'))
      }
      
      reader.readAsText(file)
    } else {
      // Handle XLSX files
      const reader = new FileReader()
      
      reader.onload = (event) => {
        try {
          const arrayBuffer = event.target.result
          const parsedData = parseXLSX(arrayBuffer)
          
          // Ensure we have at least 2 rows and 2 columns
          if (parsedData.length < 2 || parsedData[0].length < 2) {
            throw new Error('File must have at least 2 rows and 2 columns')
          }
          
          // Clean up the data - remove empty rows/columns and trim whitespace
          const cleanedData = parsedData
            .filter(row => row.some(cell => cell.trim() !== ''))
            .map(row => row.map(cell => cell.trim()))
          
          resolve(cleanedData)
        } catch (error) {
          reject(new Error(`Failed to parse XLSX: ${error.message}`))
        }
      }
      
      reader.onerror = () => {
        reject(new Error('Failed to read XLSX file'))
      }
      
      reader.readAsArrayBuffer(file)
    }
  })
}

/**
 * Convert CSV file to rubric grid format (legacy function for backward compatibility)
 * @param {File} file - CSV file object
 * @returns {Promise<Array<Array<string>>>} Promise that resolves to rubric grid
 */
export const convertCSVToRubric = async (file) => {
  return convertFileToRubric(file)
}

/**
 * Validate file structure for rubric format
 * @param {Array<Array<string>>} data - Parsed file data
 * @returns {Object} Validation result with isValid and message
 */
export const validateRubricFile = (data) => {
  if (!data || data.length < 2) {
    return { isValid: false, message: 'File must have at least 2 rows' }
  }
  
  if (data[0].length < 2) {
    return { isValid: false, message: 'File must have at least 2 columns' }
  }
  
  // Check if first row and first column have headers
  const hasGradeHeaders = data[0].some((cell, index) => index > 0 && cell.trim() !== '')
  const hasCriteriaHeaders = data.some((row, index) => index > 0 && row[0] && row[0].trim() !== '')
  
  if (!hasGradeHeaders) {
    return { isValid: false, message: 'First row should contain grade headers' }
  }
  
  if (!hasCriteriaHeaders) {
    return { isValid: false, message: 'First column should contain criteria headers' }
  }
  
  return { isValid: true, message: 'File format is valid for rubric' }
}

/**
 * Validate CSV structure for rubric format (legacy function for backward compatibility)
 * @param {Array<Array<string>>} data - Parsed CSV data
 * @returns {Object} Validation result with isValid and message
 */
export const validateRubricCSV = (data) => {
  return validateRubricFile(data)
}

/**
 * Convert rubric grid back to CSV format
 * @param {Array<Array<string>>} rubricGrid - Rubric grid data
 * @returns {string} CSV string
 */
export const convertRubricToCSV = (rubricGrid) => {
  return rubricGrid
    .map(row => 
      row.map(cell => {
        // Escape quotes and wrap in quotes if contains comma or newline
        const escaped = cell.replace(/"/g, '""')
        if (escaped.includes(',') || escaped.includes('\n') || escaped.includes('"')) {
          return `"${escaped}"`
        }
        return escaped
      }).join(',')
    )
    .join('\n')
}

/**
 * Convert rubric grid to XLSX format
 * @param {Array<Array<string>>} rubricGrid - Rubric grid data
 * @returns {ArrayBuffer} XLSX file as ArrayBuffer
 */
export const convertRubricToXLSX = (rubricGrid) => {
  try {
    // Create workbook and worksheet
    const workbook = XLSX.utils.book_new()
    const worksheet = XLSX.utils.aoa_to_sheet(rubricGrid)
    
    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Rubric')
    
    // Convert to ArrayBuffer
    const arrayBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
    return arrayBuffer
  } catch (error) {
    throw new Error(`Failed to create XLSX: ${error.message}`)
  }
}

/**
 * Download rubric grid as CSV file
 * @param {Array<Array<string>>} rubricGrid - Rubric grid data
 * @param {string} filename - Name for the downloaded file
 */
export const downloadRubricAsCSV = (rubricGrid, filename = 'rubric.csv') => {
  const csvContent = convertRubricToCSV(rubricGrid)
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  
  if (link.download !== undefined) {
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', filename)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

/**
 * Download rubric grid as XLSX file
 * @param {Array<Array<string>>} rubricGrid - Rubric grid data
 * @param {string} filename - Name for the downloaded file
 */
export const downloadRubricAsXLSX = (rubricGrid, filename = 'rubric.xlsx') => {
  try {
    const arrayBuffer = convertRubricToXLSX(rubricGrid)
    const blob = new Blob([arrayBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const link = document.createElement('a')
    
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', filename)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  } catch (error) {
    console.error('Failed to download XLSX:', error)
  }
}
