import React from 'react';

function ResultPage({ feedback, finalAnswer }) {
    return (
        <div className="p-4">
            <h2>Feedback</h2>
            <p>{feedback}</p>
            {finalAnswer && (
                <>
                    <h3>Final Answer</h3>
                    <p>{finalAnswer}</p>
                </>
            )}
        </div>
    );
}

export default ResultPage; 