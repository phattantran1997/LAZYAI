import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useFile } from '../hooks/useFile'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Upload, Loader2 } from 'lucide-react'

const UploadScreen = () => {
  const { user } = useAuth()
  const [file, setFile] = useState(null)
  const { uploading, status, upload } = useFile()

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
  }

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    upload(file, user.username);
  };

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
              disabled={!file || uploading}
              className="w-full"
            >
              {uploading ? (
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

            {(status) && (
              <div className="text-center text-muted-foreground">
                <p>{status}</p>
              </div>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

export default UploadScreen