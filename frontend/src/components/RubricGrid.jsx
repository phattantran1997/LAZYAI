import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Grid3X3, Plus, Download, Trash2, X, Upload, AlertCircle } from 'lucide-react'

const RubricGrid = ({ 
  rubricGrid, 
  updateGridCell, 
  addRow, 
  addColumn, 
  removeRow, 
  removeColumn, 
  handleClearAllData,
  handleFileUpload,
  handleDownloadXLSX,
  isLoadingCsv,
  csvError
}) => {
  return (
    <div className="mt-6 space-y-4 animate-in slide-in-from-top-2 duration-300">
      <div className="flex items-center justify-between">
        <h4 className="text-md font-medium flex items-center gap-2">
          <Grid3X3 className="h-4 w-4" />
          Custom Rubric
        </h4>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => document.getElementById('csv-upload-input').click()}
            className="flex items-center gap-1"
            disabled={isLoadingCsv}
          >
            {isLoadingCsv ? (
              <Upload className="h-3 w-3 animate-spin" />
            ) : (
              <Upload className="h-3 w-3" />
            )}
            {isLoadingCsv ? 'Loading...' : 'Import File'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadXLSX}
            className="flex items-center gap-1"
          >
            <Download className="h-3 w-3" />
            Export XLSX
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={addRow}
            className="flex items-center gap-1"
          >
            <Plus className="h-3 w-3" />
            Row
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={addColumn}
            className="flex items-center gap-1"
          >
            <Plus className="h-3 w-3" />
            Column
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleClearAllData}
            className="flex items-center gap-1 text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            <Trash2 className="h-3 w-3" />
            Clear All
          </Button>
        </div>
      </div>

      {/* Hidden CSV input */}
      <input
        id="csv-upload-input"
        type="file"
        className="hidden"
        accept=".csv,.xlsx,.xls,.txt"
        onChange={handleFileUpload}
      />

      {/* Error display */}
      {csvError && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg animate-in slide-in-from-top-2 duration-300">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <p className="text-sm text-red-700 font-medium">
            {csvError}
          </p>
        </div>
      )}

      <div className="overflow-x-auto">
        <div className="inline-block min-w-full">
          <div className="grid gap-1 p-4 bg-muted/30 rounded-lg border" style={{ gridTemplateColumns: `repeat(${rubricGrid[0]?.length || 1}, 1fr)` }}>
            {rubricGrid.map((row, rowIndex) => 
              row.map((cell, colIndex) => (
                <div key={`${rowIndex}-${colIndex}`} className="relative group">
                  {/* Header cells (first row and first column) */}
                  {(rowIndex === 0 || colIndex === 0) ? (
                    <div className="relative">
                      {rowIndex === 0 ? (
                        <Input
                          value={cell}
                          onChange={(e) => updateGridCell(rowIndex, colIndex, e.target.value)}
                          placeholder={
                            rowIndex === 0 && colIndex === 0 
                              ? '' 
                              : 'Grade'
                          }
                          className={`text-center font-medium text-sm h-10 ${
                            rowIndex === 0 && colIndex === 0 
                              ? 'bg-primary/10 border-primary/30' 
                              : 'bg-blue-50 border-blue-200'
                          }`}
                        />
                      ) : (
                        <Input
                          as="textarea"
                          rows="3"
                          value={cell}
                          onChange={(e) => updateGridCell(rowIndex, colIndex, e.target.value)}
                          placeholder="Criteria"
                          className="text-sm resize-none min-h-[80px] bg-green-50 border-green-200 font-medium"
                        />
                      )}
                      {/* Remove buttons for headers */}
                      {rowIndex === 0 && colIndex > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeColumn(colIndex)}
                          className="absolute -top-2 -right-2 h-5 w-5 p-0 opacity-0 group-hover:opacity-100 transition-opacity bg-red-100 hover:bg-red-200 border border-red-300"
                        >
                          <X className="h-3 w-3 text-red-600" />
                        </Button>
                      )}
                      {colIndex === 0 && rowIndex > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeRow(rowIndex)}
                          className="absolute -top-2 -right-2 h-5 w-5 p-0 opacity-0 group-hover:opacity-100 transition-opacity bg-red-100 hover:bg-red-200 border border-red-300"
                        >
                          <X className="h-3 w-3 text-red-600" />
                        </Button>
                      )}
                    </div>
                  ) : (
                    /* Content cells */
                    <Input
                      as="textarea"
                      rows="3"
                      value={cell}
                      onChange={(e) => updateGridCell(rowIndex, colIndex, e.target.value)}
                      placeholder="Enter description..."
                      className="text-sm resize-none min-h-[80px] bg-white hover:bg-gray-50 focus:bg-white transition-colors"
                    />
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      <div className="text-xs text-muted-foreground">
        <p>✨ Create your custom marking rubric by adding criteria rows and grade columns.</p>
        <p>📁 Import CSV/XLSX files with your existing rubric or export the current grid as XLSX.</p>
        <p>💡 Hover over headers to remove rows/columns. The grid will be used for AI evaluation.</p>
      </div>
    </div>
  )
}

export default RubricGrid 