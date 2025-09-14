import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError
from typing import List

from evaluation_service import evaluate_answer
import litellm

# --- Data Sanitization Helpers (The Fix) ---
def parse_score(value: any) -> int:
    """Safely parses a score from various AI outputs (str, float, int) into an integer."""
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        # Find the first number in the string (e.g., "4.5/5" -> "4.5")
        match = re.search(r'(\d+(\.\d+)?)', value)
        if match:
            try:
                return int(float(match.group(1)))
            except (ValueError, TypeError):
                return 0
    return 0

def parse_list_to_string(value: any) -> str:
    """Converts a list of strings into a single, bulleted string."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        # Join list items with a newline and bullet point
        return "- " + "\n- ".join(map(str, value))
    return ""

# --- Prompts and Setup ---
HIRING_MANAGER_PROMPT = """You are a hiring manager AI. Synthesize the interview transcript into a JSON summary. Your output MUST be a valid JSON object with keys: "overall_recommendation", "proficiency_score", "key_strengths", "areas_for_improvement", "summary". The 'key_strengths' and 'areas_for_improvement' should be bulleted lists inside a single string."""
interview_sessions = {}
QUESTIONS = []

def load_questions():
    global QUESTIONS
    with open("questions.json", "r") as f:
        QUESTIONS = json.load(f)

def generate_transcript(session_data: dict) -> str:
    transcript = ""
    for item in session_data.get("answers", []):
        transcript += f"Question: {item['question']}\nAnswer: {item['answer']}\nEvaluation: {item['evaluation']['score']}/5\n\n"
    return transcript.strip()

# --- Pydantic Models ---
class StartRequest(BaseModel): candidate_name: str
class StartResponse(BaseModel): session_id: str; first_question: str
class ChatRequest(BaseModel): session_id: str; answer: str
class ChatResponse(BaseModel): next_question: str | None; evaluation: dict; is_complete: bool
class ReportResponse(BaseModel): overall_recommendation: str; proficiency_score: int; key_strengths: str; areas_for_improvement: str; summary: str

# --- FastAPI App ---
app = FastAPI()
@app.on_event("startup")
def on_startup(): load_questions()

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.post("/interview/start", response_model=StartResponse)
def start_interview(req: StartRequest):
    session_id = f"session_{len(interview_sessions) + 1}"
    interview_sessions[session_id] = {"name": req.candidate_name, "idx": 0, "answers": []}
    return StartResponse(session_id=session_id, first_question=QUESTIONS[0]['text'])

@app.post("/interview/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    session = interview_sessions.get(req.session_id)
    if not session: raise HTTPException(404, "Session not found")
    
    current_idx = session["idx"]
    if current_idx >= len(QUESTIONS): raise HTTPException(400, "Interview complete")

    q = QUESTIONS[current_idx]['text']
    eval_res = evaluate_answer(question=q, answer=req.answer)
    session['answers'].append({"question": q, "answer": req.answer, "evaluation": eval_res})
    
    session["idx"] += 1
    next_idx = session["idx"]
    is_complete = next_idx >= len(QUESTIONS)
    next_q = QUESTIONS[next_idx]['text'] if not is_complete else None
    
    return ChatResponse(next_question=next_q, evaluation=eval_res, is_complete=is_complete)

@app.get("/interview/report/{session_id}", response_model=ReportResponse)
def get_report(session_id: str):
    session = interview_sessions.get(session_id)
    if not session: raise HTTPException(404, "Session not found")

    transcript = generate_transcript(session)
    prompt = HIRING_MANAGER_PROMPT.format(transcript=transcript)

    try:
        response = litellm.completion(model="ollama/phi3", messages=[{"role": "user", "content": prompt}], temperature=0.3, response_format={"type": "json_object"})
        report_json = json.loads(response.choices[0].message.content)
        
        # Sanitize the messy data from the AI before validation
        sanitized_data = {
            'overall_recommendation': str(report_json.get('overall_recommendation') or report_json.get('Recommendation', 'N/A')),
            'proficiency_score': parse_score(report_json.get('proficiency_score') or report_json.get('Overall_Skill_Score', 0)),
            'key_strengths': parse_list_to_string(report_json.get('key_strengths') or report_json.get('Key_Strengths', [])),
            'areas_for_improvement': parse_list_to_string(report_json.get('areas_for_improvement') or report_json.get('Areas_for_Improvement', [])),
            'summary': str(report_json.get('summary') or report_json.get('Professional_Summary', 'N/A'))
        }
        
        return ReportResponse(**sanitized_data)
        
    except Exception as e:
        print(f"CRITICAL ERROR generating report: {e}")
        raise HTTPException(status_code=500, detail=f"AI model failed to return a valid report. Details: {e}")
