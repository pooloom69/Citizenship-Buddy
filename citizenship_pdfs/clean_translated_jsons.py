# 📄 clean_translated_jsons.py
import json
from pathlib import Path

def clean_language_json(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 0, 2, 4, 6 ... 번째(영어) 항목 제거
    cleaned = [item for i, item in enumerate(data) if i % 2 == 1]

    # id 재정렬 (1부터 순서대로)
    for i, q in enumerate(cleaned, start=1):
        q["id"] = i

    out_path = file_path
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"✅ Cleaned {file_path.name}: kept {len(cleaned)} questions")


if __name__ == "__main__":
    folder = Path(".")
    for file in folder.glob("128-Civics-Questions-and-Answers-*.json"):
        clean_language_json(file)
