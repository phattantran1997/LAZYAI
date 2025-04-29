import React, { useState } from 'react';
import axios from 'axios';

function QuizPage({ quiz }) {
    const [answers, setAnswers] = useState({});

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post('http://localhost:8000/submit-quiz', { answers });
            console.log(res.data);
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="p-4">
            <form onSubmit={handleSubmit}>
                {quiz.map((q, index) => (
                    <div key={index}>
                        <p>{q.question}</p>
                        {q.options.map((option, i) => (
                            <label key={i}>
                                <input
                                    type="radio"
                                    name={`question-${index}`}
                                    value={option}
                                    onChange={(e) => setAnswers({ ...answers, [index]: e.target.value })}
                                />
                                {option}
                            </label>
                        ))}
                    </div>
                ))}
                <button type="submit" className="bg-blue-500 text-white p-2 mt-2">Submit Answers</button>
            </form>
        </div>
    );
}

export default QuizPage; 