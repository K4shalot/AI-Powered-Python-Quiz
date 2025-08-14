import json
from django.core.management.base import BaseCommand
from models import Question, Option
from django.db import transaction

class Command(BaseCommand):
    help = "Import questions from JSON file"

    def handle(self, *args, **kwargs):
        with open('jsonquestions.txt', encoding='utf-8') as f:
            questions = json.load(f)

        created = 0
        with transaction.atomic():
            for q in questions:
                question_text = q.get("question", "").strip()
                correct_key = q.get("correct_answer", "").strip().lower()
                options_dict = q.get("options", {})

                if not question_text or not options_dict or correct_key not in options_dict:
                    continue

                question_obj = Question.objects.create(
                    question=question_text,
                    correct_answer_key=correct_key
                )

                for key, text in options_dict.items():
                    Option.objects.create(
                        question=question_obj,
                        key=key,
                        text=text.strip()
                    )

                created += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {created} questions."))
