import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practice_tests.settings")
django.setup()

from exams.models import Question, Exam

fake = Faker()
exam = Exam.objects.get(id=2)  # Network+ Exam

protocols = ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'FTP']
devices = ['switch', 'router', 'firewall', 'access point', 'modem']
services = {
    '22': 'SSH',
    '23': 'Telnet',
    '53': 'DNS',
    '80': 'HTTP',
    '110': 'POP3',
    '443': 'HTTPS'
}

def generate_multiple_choice():
    qtext = f"Which protocol is best suited for {fake.bs()}?"
    options = random.sample(protocols, 4)
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
    sample = random.sample(list(services.items()), 3)
    return Question(
        exam=exam,
        text="Match each port to its corresponding service.",
        question_type='drag_and_drop',
        extra_data={'pairs': {k: v for k, v in sample}}
    )

def generate_true_false():
    statement = f"{random.choice(devices).capitalize()} operates at Layer 2 of the OSI model."
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
    print(f"✅ Network+ questions generated: {len(questions)}")

if __name__ == '__main__':
    run()
