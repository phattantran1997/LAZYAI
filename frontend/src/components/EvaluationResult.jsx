import { Card, CardContent } from '@/components/ui/card'
import { CheckCircle2, XCircle } from 'lucide-react'

const EvaluationResult = ({ evaluation }) => {
  if (!evaluation) return null

  return (
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
  )
}

export default EvaluationResult 