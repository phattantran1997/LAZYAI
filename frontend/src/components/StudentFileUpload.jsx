import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Upload, FileCheck, X } from 'lucide-react'

const StudentFileUpload = ({ onFileUpload, onFileRemove, uploadedFile, isDragOver, onDragOver, onDragLeave, onDrop }) => {
  return (
    <div
      className={`relative border-2 border-dashed rounded-lg p-6 transition-all duration-300 ease-in-out cursor-pointer group hover:border-primary/50 ${
        isDragOver 
          ? 'border-primary bg-primary/5 scale-[1.02]' 
          : 'border-muted-foreground/25'
      } ${uploadedFile ? 'border-green-500 bg-green-50' : ''}`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onClick={() => document.getElementById('student-file-input').click()}
    >
      <input
        id="student-file-input"
        type="file"
        className="hidden"
        accept=".pdf,.doc,.docx,.txt,.md,.csv,.xlsx,.xls"
        onChange={onFileUpload}
      />
      
      <div className="flex flex-col items-center text-center space-y-3">
        <div className={`p-3 rounded-full transition-all duration-300 ${
          uploadedFile 
            ? 'bg-green-100 text-green-600' 
            : isDragOver 
              ? 'bg-primary/10 text-primary scale-110' 
              : 'bg-muted text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary'
        }`}>
          {uploadedFile ? (
            <FileCheck className="h-6 w-6" />
          ) : (
            <Upload className="h-6 w-6" />
          )}
        </div>
        
        {uploadedFile ? (
          <div className="space-y-2">
            <p className="text-sm font-medium text-green-700">
              {uploadedFile.name}
            </p>
            <p className="text-xs text-green-600">
              {(uploadedFile.size / 1024).toFixed(1)} KB
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onFileRemove()
              }}
              className="text-xs"
            >
              <X className="h-3 w-3 mr-1" />
              Remove
            </Button>
          </div>
        ) : (
          <div className="space-y-1">
            <p className="text-sm font-medium">
              {isDragOver ? 'Drop your file here' : 'Upload student file'}
            </p>
            <p className="text-xs text-muted-foreground">
              PDF, DOC, TXT, MD, CSV or XLSX files
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default StudentFileUpload 