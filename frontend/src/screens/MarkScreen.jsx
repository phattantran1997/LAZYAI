import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { FileCheck, Settings, Grid3X3, Send, CheckCircle2 } from 'lucide-react'
import { convertFileToRubric, validateRubricFile, downloadRubricAsXLSX } from '@/services/convertCsv'
import StudentFileUpload from '@/components/StudentFileUpload'
import RubricGrid from '@/components/RubricGrid'

const MarkScreen = () => {
  const [submission, setSubmission] = useState('')
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [studentFile, setStudentFile] = useState(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [csvError, setCsvError] = useState('')
  const [isLoadingCsv, setIsLoadingCsv] = useState(false)
  
  // Grid state - initialize with 3x3 grid
  const [rubricGrid, setRubricGrid] = useState([
    ['', '', '', ''], // Header row
    ['', '', '', ''],
    ['', '', '', ''],
    ['', '', '', '']
  ])

  const handleStudentFileUpload = (file) => {
    // Empty function for now - will handle later
    setStudentFile(file)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragOver(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.name.toLowerCase().endsWith('.csv') || file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls')) {
        handleFileUpload(file)
      } else {
        handleStudentFileUpload(file)
      }
    }
  }

  const handleStudentFileInputChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      if (file.name.toLowerCase().endsWith('.csv') || file.name.toLowerCase().endsWith('.xlsx') || file.name.toLowerCase().endsWith('.xls')) {
        handleFileUpload(file)
      } else {
        handleStudentFileUpload(file)
      }
    }
  }

  const removeStudentFile = () => {
    setStudentFile(null)
  }

  // Grid manipulation functions
  const updateGridCell = (rowIndex, colIndex, value) => {
    const newGrid = [...rubricGrid]
    newGrid[rowIndex][colIndex] = value
    setRubricGrid(newGrid)
  }

  const addRow = () => {
    const newRow = Array(rubricGrid[0].length).fill('')
    setRubricGrid([...rubricGrid, newRow])
  }

  const addColumn = () => {
    const newGrid = rubricGrid.map((row) => [...row, ''])
    setRubricGrid(newGrid)
  }

  const removeRow = (rowIndex) => {
    if (rubricGrid.length > 2) { // Keep at least header + 1 row
      const newGrid = rubricGrid.filter((_, index) => index !== rowIndex)
      setRubricGrid(newGrid)
    }
  }

  const removeColumn = (colIndex) => {
    if (rubricGrid[0].length > 2) { // Keep at least criteria column + 1 grade column
      const newGrid = rubricGrid.map(row => row.filter((_, index) => index !== colIndex))
      setRubricGrid(newGrid)
    }
  }

  // File handling functions
  const handleFileUpload = async (file) => {
    const fileName = file.name.toLowerCase()
    const isCSV = fileName.endsWith('.csv')
    const isXLSX = fileName.endsWith('.xlsx') || fileName.endsWith('.xls')
    const isTXT = fileName.endsWith('.txt')
    
    if (!isCSV && !isXLSX && !isTXT) {
      setCsvError('Please select a CSV, XLSX or TXT file')
      return
    }

    setIsLoadingCsv(true)
    setCsvError('')

    try {
      let fileData
      
      if (isTXT) {
        // Handle TXT files by reading as text and parsing
        const textContent = await new Promise((resolve, reject) => {
          const reader = new FileReader()
          reader.onload = (e) => resolve(e.target.result)
          reader.onerror = () => reject(new Error('Failed to read TXT file'))
          reader.readAsText(file)
        })
        
        // Simple parsing for TXT files - split by tabs or multiple spaces
        const lines = textContent.split('\n').filter(line => line.trim() !== '')
        fileData = lines.map(line => 
          line.split(/\t|\s{2,}/).map(cell => cell.trim())
        )
      } else {
        // Handle CSV and XLSX files using the existing service
        fileData = await convertFileToRubric(file)
      }
      
      const validation = validateRubricFile(fileData)
      
      if (!validation.isValid) {
        setCsvError(validation.message)
        return
      }

      setRubricGrid(fileData)
      setCsvError('')
    } catch (error) {
      setCsvError(error.message)
    } finally {
      setIsLoadingCsv(false)
    }
  }

  const handleDownloadXLSX = () => {
    downloadRubricAsXLSX(rubricGrid, 'marking_rubric.xlsx')
  }

  const handleClearAllData = () => {
    // Reset to initial empty grid
    setRubricGrid([
      ['', '', '', ''], // Header row
      ['', '', '', ''],
      ['', '', '', ''],
      ['', '', '', '']
    ])
  }

  const handleCSVFileInputChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFileUpload(file)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!submission.trim() && !studentFile) return

    setIsEvaluating(true)
    
    // Mock sending evaluation - change submission to show sent status
    const originalSubmission = submission
    setSubmission("✅ Evaluation sent successfully! The student will receive the feedback shortly.")
    
    // Simulate AI evaluation
    setTimeout(() => {
      const totalScore = Math.floor(Math.random() * 40) + 60 // Random score between 60-100
      
      // Generate criteria-based evaluation
      const criteriaEvaluation = rubricGrid
        .filter((row, index) => index > 0 && row[0] && row[0].trim()) // Get criteria rows
        .map((row, index) => {
          const criteriaName = row[0] || `Criteria ${index + 1}`
          const maxPoints = 20 // Mock max points per criteria
          const earnedPoints = Math.floor(Math.random() * maxPoints) + 10 // Random points between 10-30
          return `${criteriaName}: ${earnedPoints}/${maxPoints} points`
        })
        .join('\n')
      
      const evaluationText = `📊 EVALUATION RESULTS

🎯 Overall Score: ${totalScore}/100

📋 Criteria Breakdown:
${criteriaEvaluation}

💡 Feedback:
• Good understanding of the concepts
• Could improve on technical details
• Well-structured response
• Consider adding more examples

📝 Comments:
The student demonstrates solid understanding of the material with room for improvement in technical precision and depth of analysis.`

      setSubmission(evaluationText)
      setIsEvaluating(false)
    }, 2000)
  }

  return (
    <div className="container max-w-5xl py-8">
      <Card>
        <CardHeader>
          <CardTitle>Mark Assignment</CardTitle>
          <CardDescription>
            Upload student submission and marking criteria for AI-powered evaluation
          </CardDescription>
        </CardHeader>
                <CardContent>
          

          {/* Student Submission Section */}
          <div className="space-y-4 mb-8">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Student Submission
              </h3>
            </div>

            <StudentFileUpload
              onFileUpload={handleStudentFileInputChange}
              onFileRemove={removeStudentFile}
              uploadedFile={studentFile}
              isDragOver={isDragOver}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            />

            <RubricGrid
              rubricGrid={rubricGrid}
              updateGridCell={updateGridCell}
              addRow={addRow}
              addColumn={addColumn}
              removeRow={removeRow}
              removeColumn={removeColumn}
              handleClearAllData={handleClearAllData}
              handleFileUpload={handleCSVFileInputChange}
              handleDownloadXLSX={handleDownloadXLSX}
              isLoadingCsv={isLoadingCsv}
              csvError={csvError}
            />

            {(studentFile || submission.trim()) && rubricGrid.some(row => row.some((cell, index) => index > 0 && cell.trim())) && (
              <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg animate-in slide-in-from-top-2 duration-300">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <p className="text-sm text-green-700 font-medium">
                  Ready for evaluation! Both student submission and criteria are complete.
                </p>
              </div>
            )}
          </div>

          {/* Evaluate Button */}
          <div className="mb-6">
            <Button
              onClick={handleSubmit}
              disabled={(!submission.trim() && !studentFile) || !rubricGrid.some(row => row.some((cell, index) => index > 0 && cell.trim())) || isEvaluating}
              className="w-full"
            >
              {isEvaluating ? (
                <>
                  <FileCheck className="mr-2 h-4 w-4 animate-spin" />
                  Evaluating...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Send for Evaluation
                </>
              )}
            </Button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label
                htmlFor="submission"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Evaluation Feedback
              </label>
              <textarea
                id="submission"
                value={submission}
                onChange={(e) => setSubmission(e.target.value)}
                placeholder="Upload student file or paste student's submission here..."
                className="w-full min-h-[300px] p-3 border border-input bg-background text-sm rounded-md resize-y focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                style={{ 
                  lineHeight: '1.5',
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word'
                }}
              />
            </div>
            {/* Evaluate Button */}
          <div className="mb-6">
            <Button
              onClick={handleSubmit}
              disabled={!submission.trim() || isEvaluating}
              className="w-full"
            >
              {isEvaluating ? (
                <>
                  <FileCheck className="mr-2 h-4 w-4 animate-spin" />
                  Evaluating...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Send to student
                </>
              )}
            </Button>
          </div>
          </form>

          
        </CardContent>
      </Card>
    </div>
  )
}

export default MarkScreen 