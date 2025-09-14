import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from evaluation_service import evaluate_answer, MASTER_RUBRIC_PROMPT
import litellm

# --- New Master Prompt for Final Report ---
HIRING_MANAGER_PROMPT = """
You are a senior hiring manager AI for a top finance firm. Your task is to synthesize an entire interview transcript into a concise, actionable executive summary for a busy hiring manager.

**INSTRUCTIONS:**
1.  **Review the Transcript:** Analyze the full Q&A transcript provided.
2.  **Synthesize Performance:** Do not evaluate question by question. Instead, form a holistic view of the candidate's Excel proficiency.
3.  **Generate a JSON Report:** Your output MUST be a valid JSON object with the following keys:
    *   : A direct recommendation (e.g., "Strong Hire", "Hire with Reservations", "Do Not Hire").
    *   : An overall integer score from 1-100 representing their skill level.
    *   : A bulleted list (as a single string with '\n- ') of 2-3 key strengths demonstrated.
    *   : A bulleted list (as a single string with '\n- ') of 2-3 areas for improvement.
    *   : A 2-3 sentence professional summary of the candidate's performance.

**INTERVIEW TRANSCRIPT:**
{transcript}

**Your JSON Output:**
"""

# --- In-Memory Database and Question Loading ---
interview_sessions = {}
QUESTIONS = []

def load_questions():
    global QUESTIONS
    with open("questions.json", "r") as f:
        QUESTIONS = json.load(f)

def generate_transcript(session_data: dict) -> str:
    transcript = ""
    for i, answer_data in enumerate(session_data.get("answers", [])):
        transcript += f"Question {i+1}: {answer_data['question']}\n"
        transcript += f"Candidate Answer: {answer_data['answer']}\n"
        transcript += f"Evaluation Score: {answer_data['evaluation']['score']}/5\n"
        transcript += f"Evaluation Rationale: {answer_data['evaluation']['evaluation']}\n\n"
    return transcript.strip()

# --- Pydantic Models ---
class StartRequest(BaseModel):
    candidate_name: str

class StartResponse(BaseModel):
    session_id: str
    first_question: str

class ChatRequest(BaseModel):
    session_id: str
    answer: str

class ChatResponse(BaseModel):
    next_question: str | None
    evaluation: dict
    is_complete: bool

class ReportResponse(BaseModel):
    overall_recommendation: str
    proficiency_score: int
    key_strengths: str
    areas_for_improvement: str
    summary: str

# --- FastAPI Application ---
app = FastAPI()

@app.on_event("startup")
def on_startup():
    load_questions()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---
@app.post("/interview/start", response_model=StartResponse)
def start_interview(request: StartRequest):
    session_id = f"session_{len(interview_sessions) + 1}"
    interview_sessions[session_id] = {
        "candidate_name": request.candidate_name,
        "current_question_index": 0,
        "answers": []
    }
    return StartResponse(session_id=session_id, first_question=QUESTIONS[0]['text'])

@app.post("/interview/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest):
    session = interview_sessions.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current_idx = session["current_question_index"]
    if current_idx >= len(QUESTIONS):
        raise HTTPException(status_code=400, detail="Interview complete")

    current_question = QUESTIONS[current_idx]['text']
    evaluation_result = evaluate_answer(question=current_question, answer=request.answer)
    session['answers'].append({"question": current_question, "answer": request.answer, "evaluation": evaluation_result})
    
    session["current_question_index"] += 1
    next_idx = session["current_question_index"]
    is_complete = next_idx >= len(QUESTIONS)
    next_question = QUESTIONS[next_idx]['text'] if not is_complete else None
    
    return ChatResponse(next_question=next_question, evaluation=evaluation_result, is_complete=is_complete)

@app.get("/interview/report/{session_id}", response_model=ReportResponse)
def get_report(session_id: str):
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    transcript = generate_transcript(session)
    prompt = HIRING_MANAGER_PROMPT.format(transcript=transcript)

    try:
        response = litellm.completion(
            model="ollama/llama3", # or "ollama/phi3"
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        result_str = response.choices[0].message.content
        report_json = json.loads(result_str)
        return report_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {e}")
