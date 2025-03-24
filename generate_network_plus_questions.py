import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practice_tests.settings")
django.setup()

from exams.models import Question, Exam

fake = Faker()
exam = Exam.objects.get(id=2)

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

def generate_performance_based():
    task = f"Design a secure topology for a small office network using at least one firewall and a DMZ."
    return Question(
        exam=exam,
        text="Simulate this network design task:",
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
    print(f"✅ Network+ Questions Generated: {len(questions)}")

if __name__ == '__main__':
    run()
