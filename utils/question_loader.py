import json
from pathlib import Path

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_questions():
    """
    App now uses ONLY ko_app.json.
    The file already contains:
    - id
    - question_en
    - answers_en
    - question_ko
    - answers_ko
    """

    base_dir = Path("data")
    ko_file = base_dir / "ko_app.json"

    if not ko_file.exists():
        raise FileNotFoundError("❗ ko_app.json not found in /data folder.")

    # Bilingual JSON 그대로 반환
    questions = load_json(ko_file)

    return questions
