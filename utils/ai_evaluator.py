from openai import OpenAI
import re
client = OpenAI()

def normalize(text):
    # Lowercase
    text = text.lower()

    # Remove parentheses + content inside optionally
    text = re.sub(r"\(.*?\)", "", text)  # remove (U.S.)
    
    # Remove punctuation
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)

    # Strip extra whitespace
    text = text.strip()

    return text

def evaluate_answer(correct_answers, user_answer):
    """
    GPT-enhanced evaluator with strong lenient mode.
    """

    # Normalize answers
    normalized_correct = [normalize(a) for a in correct_answers]
    normalized_user = normalize(user_answer)

    # If main noun matches (super lenient)
    for ans in normalized_correct:
        if ans in normalized_user or normalized_user in ans:
            return {
                "is_correct": True,
                "feedback": "🟢 Correct! (meaning matches)"
            }

    # GPT fallback for deeper meaning check
    prompt = f"""
You are a USCIS civics test evaluator.

Determine if the user's answer has the SAME MEANING as ANY of the correct answers.

IMPORTANT RULES:
- Ignore parentheses and their content (e.g., "(U.S.)").
- Ignore articles, punctuation, casing, spacing.
- Ignore missing qualifiers ("U.S." vs "Constitution").
- If the user's answer contains the core meaning, mark it as correct.

Correct answers: {correct_answers}
User answer: {user_answer}

Return ONLY JSON:
{{
    "is_correct": true/false,
    "feedback": "short explanation"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    try:
        return eval(content)
    except:
        return {
            "is_correct": False,
            "feedback": "❌ Could not parse evaluation."
        }
