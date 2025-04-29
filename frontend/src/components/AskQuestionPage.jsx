import React, { useState } from 'react';
import axios from 'axios';

function AskQuestionPage() {
    const [question, setQuestion] = useState('');
    const [response, setResponse] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post('http://localhost:8000/ask', { question });
            setResponse(res.data);
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <div className="p-4">
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask your question"
                    className="border p-2 w-full"
                />
                <button type="submit" className="bg-blue-500 text-white p-2 mt-2">Submit</button>
            </form>
            {response && <div>{JSON.stringify(response)}</div>}
        </div>
    );
}

export default AskQuestionPage; 