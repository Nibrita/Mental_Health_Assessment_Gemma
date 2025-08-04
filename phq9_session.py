from ollama import Client
import random
import re

ollama_client = Client()

phq9_questions = [
    "Starting the First Question.Over the last 2 weeks, how often have you had little interest or pleasure in doing things?",
    "Over the last 2 weeks, how often have you been feeling down, depressed, or hopeless?",
    "Over the last 2 weeks, how often have you had trouble falling or staying asleep, or sleeping too much?",
    "Over the last 2 weeks, how often have you felt tired or had little energy?",
    "Over the last 2 weeks, how often have you had poor appetite or been overeating?",
    "Over the last 2 weeks, how often have you felt bad about yourself — or that you are a failure or have let yourself or your family down?",
    "Over the last 2 weeks, how often have you had trouble concentrating on things, such as reading or watching TV?",
    "Over the last 2 weeks, how often have you been moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you’ve been moving around a lot more than usual?",
    "Over the last 2 weeks, how often have you had thoughts that you would be better off dead or of hurting yourself in some way?"
]

def is_high_risk(text):
    lowered = text.lower()
    negation_keywords = ["not", "never", "no", "don't", "do not", "didn't", "did not"]
    if any(word in lowered for word in ["suicidal", "kill myself", "want to die", "don't want to live", "hurt myself", "end my life", "better off dead", "took pills", "took sleeping pills"]):
        if any(neg in lowered for neg in negation_keywords):
            return False
        else:
            return True
    return False

score_mapping = {
    "Not at all": 0,
    "Several days": 1,
    "More than half the days": 2,
    "Nearly every day": 3
}

confirmation_phrases = {
    "Not at all": ["I'll note that as 'not at all'.", "Thanks, marking 'not at all'."],
    "Several days": ["Noted as 'several days'.", "I'll mark that down."],
    "More than half the days": ["Noted: more than half the days."],
    "Nearly every day": ["Thanks for your honesty. Marking as 'nearly every day'."]
}

def classify_response(question, response):
    prompt = f"""
You are a mental health assistant evaluating a user's response to a PHQ-9 depression question.

Question:
{question}

Response:
{response}

Choose one of:
- Not at all
- Several days
- More than half the days
- Nearly every day

If the response is clearly positive or denies the symptom, classify as "Not at all".
Only reply with one of the options above.
"""
    result = ollama_client.chat(model="gemma3n:e2b", messages=[
        {"role": "user", "content": prompt}
    ])
    return result['message']['content'].strip()

def empathetic_reply(question, response):
    prompt = f"""
After reading this:
Q: {question}
A: {response}

Write one brief, warm sentence validating what they shared.
"""
    result = ollama_client.chat(model="gemma3n:e2b", messages=[
        {"role": "user", "content": prompt}
    ])
    return result['message']['content'].strip()

def final_summary(responses, total_score):
    full_text = "\n".join([f"Q: {q}\nA: {a}" for q, a, _ in responses])
    prompt = f"""
The user shared:
{full_text}

Their total PHQ-9 score is {total_score}.
Write a short, supportive message starting with:
"Depression severity: ..."
Then a warm paragraph (under 100 words) offering empathy and encouragement.
"""
    result = ollama_client.chat(model="gemma3n:e2b", messages=[
        {"role": "user", "content": prompt}
    ])
    return result['message']['content'].strip()

class PHQ9Session:
    def __init__(self):
        self.answers = []
        self.total_score = 0
        self.current_index = 0
        self.started = False

    def start(self):
        self.started = True
        self.answers = []
        self.total_score = 0
        self.current_index = 0
        return {
            "bot_message": phq9_questions[0],  # First PHQ-9 question
            "is_final": False,
            "interrupted": False
        }

    def reset(self):
        self.answers = []
        self.total_score = 0
        self.current_index = 0
        self.started = False

    def process_response(self, user_response):
        # If the PHQ-9 has not started and user says "start" or "start the assessment", trigger PHQ-9
        if not self.started:
            if user_response in ["start", "start the assessment"]:
                return self.start()  # Start the PHQ-9 assessment
            return {
                "bot_message": "Hello! You can start speaking to begin. Please say 'start the assessment' to begin the test.",
                "interrupted": False
            }

        # If all questions have been asked, return the result message
        if self.current_index >= len(phq9_questions):
            return {
                "bot_message": "You've completed the test!",
                "interrupted": False
            }

        # Process responses to PHQ-9 questions
        question = phq9_questions[self.current_index]
        classification = classify_response(question, user_response)
        score = score_mapping.get(classification, 0)
        self.total_score += score

        empathetic = empathetic_reply(question, user_response)
        confirm = random.choice(confirmation_phrases.get(classification, [f"Marked as {classification}"]))

        self.answers.append((question, user_response, classification))
        self.current_index += 1

        if self.current_index >= len(phq9_questions):
            final_message = final_summary(self.answers, self.total_score)
            self.started = False
            return {
                "is_final": True,
                "bot_message": f"{confirm}\n{empathetic}\n\U0001f9e0 Final message:\n{final_message}",
                "final_message": final_message,
                "interrupted": False
            }

        next_question = phq9_questions[self.current_index]
        return {
            "bot_message": f"{confirm}\n{empathetic}\n\n{next_question}",
            "is_final": False,
            "interrupted": False
        }

