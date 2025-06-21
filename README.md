# 🧠 AI Critical Thinking Mentor

An AI-powered FastAPI backend that discourages passive AI reliance by guiding users with hints, challenging them with quizzes, and promoting active learning — not just giving direct answers.
![image](https://github.com/user-attachments/assets/b4aa71b4-c67c-4d61-9ea6-d6259f143205)

## 🚀 Features

- **/ask** — User submits a question, gets AI hint + suggested approach + quiz.
- **/submit-quiz** — User submits quiz answers, receives feedback and final answer.
- FastAPI + LangChain + Ollama (deepseek-r1 model) powered backend.
- MongoDB ready (future extension for tracking user history).
- Local dev with virtual environment and .env file support.
- Docker support with docker-compose.yml (backend + MongoDB).

## 🛠️ Project Structure
<pre>backend/
├── app/
│ ├── routers/
│ │ ├── ask_router.py
│ │ └── quiz.py
│ ├── services/
│ │ ├── hint_service.py
│ │ └── ai_service.py
│ ├── database/
│ └── main.py
├── requirements.txt
├── Dockerfile
└── .env
docker-compose.yml
frontend/ (future)
</pre>
```

## ⚙️ Setup & Run Locally

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-repo/ai-critical-thinking-mentor.git
   cd ai-critical-thinking-mentor
   ```

2. **Setup backend**

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   # or
   .venv\Scripts\activate     # Windows

   pip install -r requirements.txt
   ```

3. **Create .env**

   ```dotenv
   MONGODB_URI=mongodb://localhost:27017/mydb
   ```

4. **Run the server**

   ```bash
   uvicorn app.main:app --reload
   ```

   Server available at: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🐳 Run with Docker (Optional)

## 🛡️ API Endpoints

| Method | Route         | Description                                      |
|--------|---------------|--------------------------------------------------|
| POST   | /ask          | Submit a question, receive a hint and quiz.      |
| POST   | /submit-quiz  | Submit quiz answers for feedback and answer reveal. |
| GET    | /health       | Simple health check endpoint.                    |

### Example Request for /ask

```json
{
  "question": "How do I center a div in CSS?"
}
```

### Example Request for /submit-quiz

```json
{
  "answers": {
    "q1": "A",
    "q2": "C",
    "q3": "B"
  }
}
```

## 📚 Tech Stack

- FastAPI
- LangChain
- Ollama LLM (deepseek-r1)
- Motor (MongoDB driver)
- Docker & Docker Compose

## ✨ Future Plans

- Add user authentication and quiz result saving.
- Frontend with React or Next.js.
- Advanced AI feedback personalization.

## 🤝 Contributing

Pull requests are welcome. Please open an issue to discuss proposed changes first.

## 📜 License

MIT License.

## 🚀 Author

Built with ❤️ by Lazyteam
