import React from 'react';

function HintPage({ hint, suggestedApproach, quiz }) {
    return (
        <div className="p-4">
            <h2>Hint</h2>
            <p>{hint}</p>
            <h3>Suggested Approach</h3>
            <p>{suggestedApproach}</p>
            <h3>Quiz</h3>
            <ul>
                {quiz.map((q, index) => (
                    <li key={index}>{q.question}</li>
                ))}
            </ul>
        </div>
    );
}

export default HintPage; 