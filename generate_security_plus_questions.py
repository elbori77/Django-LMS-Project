import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practice_tests.settings")
django.setup()

from exams.models import Question, Exam

fake = Faker()
exam = Exam.objects.get(id=3)  # Security+ Exam

attack_types = ['phishing', 'ransomware', 'SQL injection', 'DDoS', 'man-in-the-middle']
concepts = ['confidentiality', 'integrity', 'availability', 'authentication', 'non-repudiation']
controls = {
    'Firewall': 'Blocks unauthorized access',
    'IDS': 'Detects suspicious activity',
    'MFA': 'Adds multiple layers of authentication',
    'VPN': 'Encrypts communication over the internet'
}

def generate_multiple_choice():
    qtext = f"What type of cyberattack involves {fake.bs()}?"
    options = random.sample(attack_types, 4)
    return Question(
        exam=exam,
        text=qtext,
        question_type='multiple_choice',
        option_a=options[0],
        option_b=options[1],
        option_c=options[2],
        option_d=options[3],
        correct_option=random.choice(['A', 'B', 'C', 'D'])
    )

def generate_drag_and_drop():
    sample = random.sample(list(controls.items()), 3)
    return Question(
        exam=exam,
        text="Match each security control to its function.",
        question_type='drag_and_drop',
        extra_data={'pairs': {k: v for k, v in sample}}
    )

def generate_true_false():
    statement = f"{random.choice(concepts).capitalize()} ensures that only authorized parties can access information."
    answer = random.choice(['A', 'B'])  # A = True, B = False
    return Question(
        exam=exam,
        text=statement,
        question_type='true_false',
        option_a="True",
        option_b="False",
        correct_option=answer
    )

def run():
    Question.objects.filter(exam=exam).delete()
    questions = []

    for _ in range(220):
        questions.append(generate_multiple_choice())
    for _ in range(40):
        questions.append(generate_drag_and_drop())
    for _ in range(40):
        questions.append(generate_true_false())

    random.shuffle(questions)
    Question.objects.bulk_create(questions)
    print(f"✅ Security+ questions generated: {len(questions)}")

if __name__ == '__main__':
    run()
