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

## ✨ Road map🚀 LazyAI Project Roadmap

A 3-month development plan to build a personalized AI system for educators and students using LLM fine-tuning, automated data processing, and intelligent hint/quiz generation.

---

## ✅ Current Status (Recap)

- ✅ MVP Frontend UI built:
  - Login screen (Student + Teacher)
  - Chat screen
  - Marking screen
  - Fine-tune process interface
- ✅ Lambda function for redacting PII (with `spaCy`)
- ✅ Core cloud architecture established:
  - S3 Buckets
  - Lambda Triggers
  - SQS Messaging
  - SageMaker (Unsloth)
  - ECS batch/task pipeline

---

## 🗓️ Month 1 – Data Pipeline Automation & SageMaker Integration

### Week 1: File Ingestion + Redaction ✅

- Build and deploy `Lambda-1`:
  - Triggered on `.zip` file uploads to `lazyai-input` (S3)
  - Unzip and extract text/PDF
  - Use `spaCy` to redact PII (names, emails, locations, etc.)
  - Package as Docker-based Lambda
- Output: Redacted content stored in `lazyai-output-chunkdata` (S3)
- Log activity via CloudWatch

---

### Week 2 & 3: Generate QA Pairs using SyntheticDataKit ✅

- Build `Lambda-2`:
  - Set up pip dependencies and model (`llama3-3b-instruct`)
  - Load Unsloth model from shared EBS or S3
  - Use `SyntheticDataKit.from_pretrained(...).generate()` to produce QA pairs
- Normalize QA output:
  - Format: `context`, `question`, `answer`, `topic`
  - Store as `.jsonl` or `.csv` in `lazyai-output` bucket
- Optional:
  - Add topic tagging (regex/classifier)
  - Push job metadata to SQS
  - Log status/errors via CloudWatch or SES

---

### Week 4: QA Review & Fine-Tune Prep

- Validate structure and quality of QA output
- Confirm compatibility with training pipeline
- Configure fine-tuning trigger logic:
  - Load base model from EBS/S3
  - Pass training dataset from `lazyai-output`
  - Define SageMaker Training Job parameters (LoRA/PEFT)
- End-to-end testing:
  - Upload ➝ Redact ➝ QA ➝ Prepare for fine-tuning

---

## 💡 Month 2 – Model Fine-tuning & Serving Infrastructure

### Week 5: Launch Fine-tuning Job from QA Data

- Use Lambda or ECS to trigger training when new QA is available
- Load:
  - Pre-trained `llama3-3b-instruct` model + tokenizer
  - QA dataset from `lazyai-output`
- Launch `SFTTrainer` fine-tuning job
- Save trained model to `lazyai-models` (S3), organized by:
  - User ID
  - Subject
  - Unit

---

### Week 6: Monitor Training & Register Models

- Stream logs to CloudWatch for live monitoring
- Optionally register models in SageMaker Model Registry
- Add metadata tags (subject, user ID, timestamp)
- Notify teacher (via SES) upon success/failure

---

### Week 7: Deploy Models + Inference API

- Serve models using:
  - Option A: SageMaker Endpoint (on-demand)
  - Option B: EC2 + FastAPI (lightweight, cached)
- Develop inference APIs:
  - Input: question, quiz, topic, or text
  - Output: hint, answer, or generated question
  - Support both chat and quiz evaluation

---

### Week 8: Feedback Loop & Frontend Integration

- Frontend:
  - Students: use fine-tuned models for hints & quizzes
  - Teachers: review model output, suggest edits
- Add feedback features:
  - Approve/reject QA
  - Trigger retraining via feedback

---

## 📈 Month 3 – Backend Completion, API Integration, and Final Testing

### Week 9: Chat & Marking API Development

- **Chat API**:
  - Support multi-turn student interaction with fine-tuned model
  - Input: student query
  - Output: hint/answer with explanation

- **Marking API**:
  - Input: student response + (optional) reference answer
  - Output: score, feedback, explanation
  - Teacher override supported

---

### Week 10: Full Frontend Integration

- Connect APIs to React/Next.js frontend:
  - Handle inference, error states, and latency
  - Show chat, feedback, quiz scores in UI
- Add access control:
  - Role-based: Student vs Teacher
  - Model access per unit/user

---

### Week 11–12: System Testing, Optimization, and Launch

- **End-to-End Flow Testing**:
  - Upload ➝ Redact ➝ QA ➝ Fine-tune ➝ Inference ➝ Feedback

- **Performance**:
  - Load test APIs (Lambda & EC2)
  - Optimize response time, memory & caching

- **Monitoring & Logging**:
  - Add log aggregation
  - CloudWatch alerts for failures or errors

- **Finalization**:
  - API Documentation (Swagger/Postman)
  - Developer setup & deployment guide
  - Launch-ready for demo or production

---

### 📦 Folder Structure (suggested)

```bash
📁 lazyai/
├── backend/
│   ├── api/
│   ├── lambda_redact/
│   ├── lambda_qa/
│   └── model_serving/
├── frontend/
│   └── nextjs-app/
├── data/
│   ├── input/
│   ├── redacted/
│   └── qa_pairs/
├── sagemaker/
│   ├── training/
│   └── fine_tune_jobs/
└── docs/
    └── README.md


## 🤝 Contributing

Pull requests are welcome. Please open an issue to discuss proposed changes first.

## 📜 License

MIT License.

## 🚀 Author

Built with ❤️ by Lazyteam
