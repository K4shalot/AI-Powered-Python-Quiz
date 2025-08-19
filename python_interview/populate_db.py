import os
import django
import json
import random
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_interview.settings')
django.setup()

from interview_app.models import Question, Option

def import_questions_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: The file '{file_path}' is not a valid JSON.")
        return

    print(f"Starting import from '{file_path}'...")

    for q in questions:
        question_text = q.get('question')
        options_dict = q.get('options', {})
        correct_answer_key = q.get('correct_answer')

        if not all([question_text, options_dict, correct_answer_key]):
            print(f"Skipping invalid question object: {q}")
            continue

        correct_text = options_dict.get(correct_answer_key)
        
        shuffled_items = list(options_dict.items())
        random.shuffle(shuffled_items)

        new_options = {}
        new_correct_key = None
        new_keys = [chr(i) for i in range(97, 97 + len(shuffled_items))]

        for new_key, (original_key, text) in zip(new_keys, shuffled_items):
            new_options[new_key] = text
            if original_key == correct_answer_key:
                new_correct_key = new_key

        question_obj = Question.objects.create(
            question=question_text,
            correct_answer_key=new_correct_key
        )
        for key, text in new_options.items():
            Option.objects.create(
                question=question_obj,
                key=key,
                text=text
            )

    print(f"✅ Questions from '{file_path}' imported successfully!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
        import_questions_from_json(json_file_path)
    else:
        print("Usage: python populate_db.py <path_to_json_file>")