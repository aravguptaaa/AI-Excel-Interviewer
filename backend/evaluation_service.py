import litellm
import json

# Set LiteLLM to print detailed logs for debugging
litellm.set_verbose=False

MASTER_RUBRIC_PROMPT = """
You are an expert Excel Interviewer AI. Your task is to evaluate a candidate's answer to a technical Excel question.

**EVALUATION INSTRUCTIONS:**
1.  **Analyze the User's Answer:** Compare the user's answer against the provided question based on the following criteria:
    *   **Correctness:** Is the information factually accurate?
    *   **Completeness:** Does the answer cover the key aspects of the question?
    *   **Clarity:** Is the explanation clear and easy to understand?
2.  **Assign a Score:** Provide an integer score from 1 to 5, where 1 is "Very Poor" and 5 is "Excellent".
3.  **Provide a Rationale:** Write a concise, professional evaluation of the answer, highlighting strengths and weaknesses.
4.  **Format Your Output:** You MUST return your response as a valid JSON object with two keys: "score" (integer) and "evaluation" (string).

**Question:**
{question}

**Candidate's Answer:**
{answer}

**Your JSON Output:**
"""

def evaluate_answer(question: str, answer: str) -> dict:
    """
    Evaluates a candidate's answer using a local LLM.
    Returns a dictionary with 'score' and 'evaluation'.
    """
    prompt = MASTER_RUBRIC_PROMPT.format(question=question, answer=answer)

    try:
        response = litellm.completion(
            model="ollama/phi3",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Lower temperature for more consistent, factual evaluations
            response_format={"type": "json_object"} # Enforce JSON output
        )
        
        # The response content should be a JSON string
        result_str = response.choices[0].message.content
        result_json = json.loads(result_str)
        
        # Basic validation
        if "score" in result_json and "evaluation" in result_json:
            return result_json
        else:
            return {"score": 0, "evaluation": "Error: LLM returned malformed JSON."}

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"score": 0, "evaluation": f"An error occurred during evaluation: {e}"}

