# AI-Powered Excel Mock Interviewer

![Local AI](https://img.shields.io/badge/AI-100%25%20Local-blue.svg)![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)![FastAPI](https://img.shields.io/badge/FastAPI-0.100-05998b?logo=fastapi)![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)

An automated system designed to assess a candidate's Microsoft Excel skills through a conversational AI agent. The entire application, including the AI model, runs 100% locally, ensuring zero API costs and complete data privacy.

---

### Live Demo


---

## Core Features

- **Multi-Turn Conversational Flow:** Guides candidates through a series of predefined Excel questions, from introduction to completion.
- **Local AI Evaluation:** Uses a locally-run LLM (via Ollama) to evaluate candidate answers in real-time based on correctness, completeness, and clarity.
- **Stateful Interview Sessions:** Manages the state of each interview, tracking questions asked and answers received.
- **Executive Summary Report:** At the end of the interview, it generates a holistic, AI-powered performance report for a hiring manager, including an overall recommendation, proficiency score, strengths, and weaknesses.

## Tech Stack

| Area               | Technology                            | Description                                                  |
| :----------------- | :------------------------------------ | :----------------------------------------------------------- |
| **AI**       | **Ollama with Llama 3 / Phi-3** | Provides the core language model that runs entirely locally. |
|                    | **LiteLLM**                     | A simple, unified interface for calling any LLM.             |
| **Backend**  | **Python 3.11+**                | Core programming language.                                   |
|                    | **FastAPI**                     | High-performance web framework for building the API.         |
|                    | **Uvicorn**                     | ASGI server to run the FastAPI application.                  |
| **Frontend** | **Next.js & React**             | Modern framework for building the user interface.            |
|                    | **TypeScript**                  | For type-safe frontend code.                                 |
|                    | **Tailwind CSS**                | For rapid, utility-first styling.                            |

## Project Philosophy: Local-First AI

This project was built with a "local-first" principle. The core goal was to create a fully functional AI application without relying on external, paid APIs like OpenAI or Anthropic.

- **Cost-Effective:** Zero API bills, no matter how much the tool is used.
- **Data Privacy:** All candidate data and interview transcripts remain on the local machine and are never sent to a third party.
- **Offline Capability:** The application can run without an internet connection once the initial setup is complete.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

1. **Git:** To clone the repository.
2. **Python 3.10+:** For the backend.
3. **Node.js & npm:** For the frontend.
4. **Ollama:** Download and install from [ollama.com](https://ollama.com).

### Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd ai-excel-interviewer
   ```
2. **Setup the AI Model:**
   Pull a model using Ollama. `phi3` is faster, `llama3` is more powerful.

   ```bash
   ollama pull phi3
   # OR
   ollama pull llama3
   ```

   *Ensure the model name in `backend/evaluation_service.py` and `backend/main.py` matches the one you pulled.*
3. **Setup the Backend:**

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Setup the Frontend:**

   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

You will need two separate terminal windows.

1. **Run the Backend Server:**
   *(In a terminal at the `backend` directory)*

   ```bash
   source venv/bin/activate
   uvicorn main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`.
2. **Run the Frontend Server:**
   *(In another terminal at the `frontend` directory)*

   ```bash
   npm run dev
   ```

   Open your browser and navigate to `http://localhost:3000`.

## Future Roadmap

- **Production-Ready Deployment:** Containerize the FastAPI backend using Docker and deploy to a service like Render, with Ollama running on a dedicated GPU server.
- **JD-Driven Question Personalization:** Allow a hiring manager to paste a job description, use an LLM call to extract key skills, and dynamically select relevant questions.
- **Hiring Manager Dashboard:** Implement user authentication and a dashboard for managers to review and compare reports from all candidate interviews.
# AI-Excel-Interviewer
