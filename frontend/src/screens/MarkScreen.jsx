import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { FileCheck, CheckCircle2, XCircle } from 'lucide-react'

const MarkScreen = () => {
  const [submission, setSubmission] = useState('')
  const [evaluation, setEvaluation] = useState(null)
  const [isEvaluating, setIsEvaluating] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!submission.trim()) return

    setIsEvaluating(true)
    // Simulate AI evaluation
    setTimeout(() => {
      setEvaluation({
        score: Math.floor(Math.random() * 40) + 60, // Random score between 60-100
        feedback: [
          'Good understanding of the concepts',
          'Could improve on technical details',
          'Well-structured response',
          'Consider adding more examples',
        ].sort(() => Math.random() - 0.5).slice(0, 2), // Random 2 feedback points
      })
      setIsEvaluating(false)
    }, 2000)
  }

  return (
    <div className="container max-w-2xl py-8">
      <Card>
        <CardHeader>
          <CardTitle>Mark Assignment</CardTitle>
          <CardDescription>
            Paste the student's submission and get an AI-powered evaluation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <label
                htmlFor="submission"
                className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
              >
                Student Submission
              </label>
              <Input
                id="submission"
                as="textarea"
                rows="6"
                value={submission}
                onChange={(e) => setSubmission(e.target.value)}
                placeholder="Paste student's submission here..."
                className="min-h-[150px]"
              />
            </div>

            <Button
              type="submit"
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
                  <FileCheck className="mr-2 h-4 w-4" />
                  Evaluate
                </>
              )}
            </Button>
          </form>

          {evaluation && (
            <Card className="mt-8 bg-muted/50">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold">Evaluation Result</h2>
                  <div className="flex items-center gap-2">
                    {evaluation.score >= 80 ? (
                      <CheckCircle2 className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-yellow-500" />
                    )}
                    <span
                      className={`text-2xl font-bold ${
                        evaluation.score >= 80
                          ? 'text-green-500'
                          : evaluation.score >= 60
                          ? 'text-yellow-500'
                          : 'text-red-500'
                      }`}
                    >
                      {evaluation.score}%
                    </span>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="font-medium">Feedback:</h3>
                  <ul className="space-y-2">
                    {evaluation.feedback.map((item, index) => (
                      <li
                        key={index}
                        className="flex items-start gap-2 text-sm text-muted-foreground"
                      >
                        <span className="mt-1">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default MarkScreen 