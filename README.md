# Personal RAG Chatbot Project

This project is a personal AI chatbot application built with a separate backend and frontend.

The chatbot can answer user questions using uploaded documents from the `docs` folder. Users can add their own documents, such as resumes, PDFs, notes, or project files, based on their choice.

> Important: Do not commit API keys, `.env` files, resumes, or private documents to GitHub.

---

## Project Structure

```bash
project-root/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── docs/
│   │   └── .gitkeep
│   ├── .env.example
│   └── README.md
│
└── frontend/
    ├── package.json
    ├── next.config.js
    ├── app/
    ├── components/
    ├── .env.example
    └── README.md
```

---

## What This Project Does

This application allows users to:

- Ask questions through a web-based chatbot UI
- Upload or place documents inside the backend `docs` folder
- Use Retrieval-Augmented Generation, also called RAG
- Search document content before answering
- Use an LLM to generate answers based on retrieved context
- Keep private files and API keys outside GitHub

---

## Tech Stack

### Backend

- Python
- FastAPI
- LangChain
- OpenAI API
- ChromaDB or local vector store
- PDF/document loaders
- CORS support for frontend connection

### Frontend

- Next.js
- React
- Tailwind CSS
- shadcn/ui
- TypeScript or JavaScript
- API call to backend chatbot endpoint

---

## Important Security Notes

Do not push the following files to GitHub:

```bash
.env
.env.local
docs/*
*.pdf
*.docx
*.txt
```

The project should not include:

- OpenAI API key
- Any other secret key
- Personal resume
- Client documents
- Company documents
- Private medical, banking, or business documents

Instead, each user should create their own `.env` file and add their own documents locally.

---

## Recommended `.gitignore`

Add this to your `.gitignore` file:

```gitignore
# Environment files
.env
.env.local
.env.development
.env.production

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node
node_modules/
.next/
out/
dist/

# Private documents
docs/*
!docs/.gitkeep

# Vector DB / local indexes
chroma/
chroma_db/
.vectorstore/
```

---

# Backend Setup

Go to the backend folder:

```bash
cd backend
```

---

## Step 1: Create Virtual Environment

### Windows

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

## Step 2: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not created yet, install the common dependencies manually:

```bash
pip install fastapi uvicorn python-dotenv langchain langchain-openai langchain-community chromadb pypdf beautifulsoup4 requests
```

Then generate the `requirements.txt` file:

```bash
pip freeze > requirements.txt
```

---

## Step 3: Create Backend `.env` File

Create a file named `.env` inside the backend folder.

```bash
backend/.env
```

Add your own API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Do not commit this file to GitHub.

---

## Step 4: Add Documents

Inside the backend folder, create a folder named `docs` if it does not already exist:

```bash
mkdir docs
```

Add your own documents inside this folder.

Example:

```bash
backend/docs/my_resume.pdf
backend/docs/project_notes.pdf
backend/docs/company_faq.pdf
```

You can add:

- Resume
- PDF files
- Notes
- Knowledge base documents
- Project documentation
- Any other file you want the chatbot to read

This repository will not include any resume or private document. Each user should add their own files.

---

## Step 5: Run Backend Server

Run the FastAPI backend:

```bash
uvicorn app:app --reload
```

The backend should start at:

```bash
http://localhost:8000
```

---

## Step 6: Test Backend API

Open this URL in your browser:

```bash
http://localhost:8000/docs
```

This opens the FastAPI Swagger UI.

You can also test the chat endpoint using curl:

```bash
curl -X POST "http://localhost:8000/api/chat" ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Tell me about the uploaded documents\"}"
```

For macOS/Linux:

```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about the uploaded documents"}'
```

---

# Frontend Setup

Open a new terminal and go to the frontend folder:

```bash
cd frontend
```

---

## Step 1: Install Frontend Dependencies

```bash
npm install
```

If you are using pnpm:

```bash
pnpm install
```

If you are using yarn:

```bash
yarn install
```

---

## Step 2: Create Frontend `.env.local` File

Create a file named `.env.local` inside the frontend folder.

```bash
frontend/.env.local
```

Add the backend API URL:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Do not commit this file to GitHub.

---

## Step 3: Run Frontend App

```bash
npm run dev
```

If using pnpm:

```bash
pnpm dev
```

If using yarn:

```bash
yarn dev
```

The frontend should start at:

```bash
http://localhost:3000
```

---

# Full Run Order

Use two terminals.

---

## Terminal 1: Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

For macOS/Linux:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

---

## Terminal 2: Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# API Configuration

The frontend will call the backend API using:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Example frontend API call:

```javascript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    message: userMessage,
  }),
});
```

---

# Common Issues and Fixes

## 1. `POST /undefined/api/chat 404`

This means the frontend environment variable is missing.

Fix:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Then restart the frontend:

```bash
npm run dev
```

---

## 2. `OPTIONS /api/chat 405 Method Not Allowed`

This usually means CORS is not configured in the backend.

Add CORS middleware in FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then restart the backend.

---

## 3. OpenAI API Key Error

If you get an API key error, check:

- `.env` file exists in backend
- `OPENAI_API_KEY` is correctly added
- API key is valid
- Backend server was restarted after adding the key

---

## 4. No Document Answer Found

Check:

- Files are placed inside `backend/docs`
- Supported file type is used
- Backend was restarted after adding new files
- Vector store/index was regenerated if your project uses indexing

---

## 5. Module Not Found Error

Install missing dependency:

```bash
pip install package-name
```

Then update requirements:

```bash
pip freeze > requirements.txt
```

For frontend:

```bash
npm install package-name
```

---

# Example Backend `.env.example`

Create a file named `.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Commit only `.env.example`, not `.env`.

---

# Example Frontend `.env.example`

Create a file named `.env.example`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Commit only `.env.example`, not `.env.local`.

---

# How Users Should Add Their Own Resume

This project will not include any resume by default.

To use the chatbot with your own resume:

1. Go to the backend folder.
2. Open the `docs` folder.
3. Add your resume file, for example:

```bash
backend/docs/my_resume.pdf
```

4. Restart the backend server.
5. Ask the chatbot questions like:

```text
Summarize my resume.
What are my top skills?
Create a LinkedIn summary from my resume.
What projects are mentioned in my resume?
```

---

# Development Commands Summary

## Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

---

# Production Notes

Before deploying:

- Do not expose API keys in frontend code
- Keep OpenAI API key only in backend environment variables
- Use proper CORS origins
- Do not upload private documents to public servers
- Use environment-specific variables
- Add authentication if users upload private files
- Add rate limiting for API protection
- Add logging and monitoring

---

# Future Enhancements

Possible improvements:

- Add file upload from frontend
- Add user authentication using Clerk
- Add chat history
- Add multiple agents using MCP
- Add document management screen
- Add support for Word, Excel, CSV, and website URLs
- Add vector DB persistence
- Add deployment using Docker
- Add production deployment on AWS, GCP, or Render

---

# License

This project is for learning and personal development. Update the license based on your requirement.
