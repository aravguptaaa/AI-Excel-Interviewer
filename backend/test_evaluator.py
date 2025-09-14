import json
from evaluation_service import evaluate_answer

def run_validation():
    print("--- Starting Golden Dataset Validation ---")

    with open("golden_dataset.json", "r") as f:
        data = json.load(f)

    # Assuming one question in the dataset for now
    question_data = data[0]
    question = question_data["question"]

    for sample in question_data["samples"]:
        sample_id = sample["id"]
        answer = sample["answer"]
        expert_evaluation = sample["expert_evaluation"]

        print(f"\n{'='*20} TESTING SAMPLE: {sample_id.upper()} {'='*20}")
        print(f"QUESTION: {question}")
        print(f"ANSWER: {answer}")
        print("-" * 50)
        print(f"EXPERT EVALUATION:\n  {expert_evaluation}")
        print("-" * 50)
        
        ai_result = evaluate_answer(question, answer)
        
        print(f"AI EVALUATION:\n  Score: {ai_result.get('score')}\n  Rationale: {ai_result.get('evaluation')}")
        print(f"{'='*58}\n")

if __name__ == "__main__":
    run_validation()
