import csv
import os
from django.core.management.base import BaseCommand
from exams.models import Question, Exam
import json

class Command(BaseCommand):
    help = "Seed A+ questions from CSV"

    def handle(self, *args, **kwargs):
        file_path = os.path.join('exams', 'seed_data', 'a_plus_questions.csv')
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"CSV not found at {file_path}"))
            return

        exam = Exam.objects.get(name__icontains="A+ Practice Exam")

        self.stdout.write(self.style.NOTICE(f"Seeding from {file_path} ..."))
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for row in reader:
                extra_data = row['extra_data']
                question_type = row['question_type']

                if question_type == 'drag_and_drop' and extra_data:
                    try:
                        cleaned = extra_data.strip().replace('""', '"')
                        if cleaned.endswith(",}"):
                            cleaned = cleaned.replace(",}", "}")
                        parsed = json.loads(cleaned)
                        if isinstance(parsed, dict):
                            extra_data = {"pairs": parsed}
                        else:
                            extra_data = None
                    except Exception:
                        extra_data = None
                else:
                    extra_data = extra_data if extra_data else None

                question = Question(
                    exam=exam,
                    text=row['text'],
                    option_a=row['option_a'],
                    option_b=row['option_b'],
                    option_c=row['option_c'] if row['option_c'] else None,
                    option_d=row['option_d'] if row['option_d'] else None,
                    correct_option=row['correct_option'],
                    question_type=question_type,
                    extra_data=extra_data
                )
                question.save()
                count += 1


        self.stdout.write(self.style.SUCCESS(f"Seeded {count} A+ questions."))
