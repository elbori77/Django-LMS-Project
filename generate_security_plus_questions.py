import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practice_tests.settings")
django.setup()

from exams.models import Question, Exam

fake = Faker()
exam = Exam.objects.get(id=3)

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

def generate_performance_based():
    task = f"Design an access control policy that ensures the principle of least privilege."
    return Question(
        exam=exam,
        text="Simulate this security task:",
        question_type='performance_based',
        extra_data={
            'task': task,
            'steps_required': random.randint(2, 4)
        }
    )

def run():
    Question.objects.filter(exam=exam).delete()
    questions = [generate_multiple_choice() for _ in range(240)]
    questions += [generate_drag_and_drop() for _ in range(30)]
    questions += [generate_performance_based() for _ in range(30)]
    random.shuffle(questions)
    Question.objects.bulk_create(questions)
    print(f"✅ Security+ Questions Generated: {len(questions)}")

if __name__ == '__main__':
    run()
