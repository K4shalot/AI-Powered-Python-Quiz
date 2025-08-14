import os
import django
import json
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_interview.settings')

django.setup()

from interview_app.models import Question, Option

def import_questions_from_json():

    with open('jsonquestions_3.txt', encoding='utf-8') as f:
        questions = json.load(f)

    for q in questions:
        question_text = q['question']
        correct_text = q['options'][q['correct_answer']]
        shuffled_items = list(q['options'].items())
        random.shuffle(shuffled_items)

        new_options = {}
        new_correct_key = None
        new_keys = [chr(i) for i in range(97, 97 + len(shuffled_items))]

        for new_key, (_, text) in zip(new_keys, shuffled_items):
            new_options[new_key] = text
            if text == correct_text:
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

    print("Questions imported successfully")

if __name__ == "__main__":
    import_questions_from_json()
