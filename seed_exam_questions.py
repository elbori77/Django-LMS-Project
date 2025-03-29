import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practice_tests.settings")
django.setup()

from exams.models import Exam, Question

fake = Faker()

def create_questions(exam_id, count=300):
    exam = Exam.objects.get(id=exam_id)
    question_types = (
        ['multiple_choice'] * 220 +
        ['drag_and_drop'] * 40 +
        ['true_false'] * 40
    )
    random.shuffle(question_types)

    created = 0
    for qtype in question_types:
        text = f"[{qtype.upper()}] {fake.sentence()}"
        q = Question(
            exam=exam,
            text=text,
            question_type=qtype
        )

        if qtype == 'multiple_choice':
            q.option_a = fake.word()
            q.option_b = fake.word()
            q.option_c = fake.word()
            q.option_d = fake.word()
            q.correct_option = random.choice(['A', 'B', 'C', 'D'])

        elif qtype == 'drag_and_drop':
            q.extra_data = {
                'pairs': {
                    fake.word(): fake.word(),
                    fake.word(): fake.word(),
                    fake.word(): fake.word()
                }
            }

        elif qtype == 'true_false':
            q.option_a = "True"
            q.option_b = "False"
            q.correct_option = random.choice(['A', 'B'])

        q.save()
        created += 1

    print(f"✅ {created} questions created for Exam ID {exam_id} ({exam.name})")

# Create for each exam (1 = A+, 2 = Network+, 3 = Security+)
create_questions(1)
create_questions(2)
create_questions(3)
