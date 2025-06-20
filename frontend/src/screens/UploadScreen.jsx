import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Upload, Copy, Loader2 } from 'lucide-react'

const UploadScreen = () => {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('')
  const [shareLink, setShareLink] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const { user } = useAuth()

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    setFile(selectedFile)
    setStatus('')
    setShareLink('')
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    setIsUploading(true)
    setStatus('Waiting for fine-tune...')

    // Simulate API call
    setTimeout(() => {
      const link = `/chat/${user.username}`
      setShareLink(link)
      setStatus('Upload complete!')
      setIsUploading(false)
    }, 2000)
  }

  return (
    <div className="container max-w-2xl py-8">
      <Card>
        <CardHeader>
          <CardTitle>Upload Material</CardTitle>
          <CardDescription>
            Upload your teaching material to create an AI assistant
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUpload} className="space-y-6">
            <div className="border-2 border-dashed border-muted rounded-lg p-6">
              <div className="flex flex-col items-center gap-2">
                <Upload className="h-8 w-8 text-muted-foreground" />
                <div className="text-sm text-muted-foreground">
                  Drag and drop your file here, or click to select
                </div>
                <Input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={handleFileChange}
                  className="w-full"
                />
              </div>
            </div>

            {file && (
              <div className="text-sm text-muted-foreground">
                Selected file: {file.name}
              </div>
            )}

            <Button
              type="submit"
              disabled={!file || isUploading}
              className="w-full"
            >
              {isUploading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload
                </>
              )}
            </Button>

            {status && (
              <div className="text-center text-muted-foreground">
                <p>{status}</p>
              </div>
            )}

            {shareLink && (
              <Card className="bg-muted/50">
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground mb-2">
                    Share this link with your students:
                  </p>
                  <div className="flex items-center gap-2">
                    <Input
                      type="text"
                      value={window.location.origin + shareLink}
                      readOnly
                      className="flex-1"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      size="icon"
                      onClick={() => {
                        navigator.clipboard.writeText(window.location.origin + shareLink)
                      }}
                    >
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default UploadScreen 