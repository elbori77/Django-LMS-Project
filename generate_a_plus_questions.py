import os
import django
import random
from faker import Faker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "practice_tests.settings")
django.setup()

from exams.models import Question, Exam

fake = Faker()
exam = Exam.objects.get(id=1)  # A+ Exam

hardware_terms = ['CPU', 'RAM', 'SSD', 'GPU', 'BIOS', 'motherboard']
os_terms = ['Windows 10', 'Linux', 'macOS', 'File Explorer', 'Task Manager']
network_ports = {
    '20': 'FTP Data',
    '21': 'FTP Control',
    '22': 'SSH',
    '23': 'Telnet',
    '25': 'SMTP',
    '53': 'DNS',
    '80': 'HTTP',
    '443': 'HTTPS'
}

def generate_multiple_choice():
    question = f"What component is most likely responsible for {fake.sentence(nb_words=5)}?"
    options = random.sample(hardware_terms + os_terms, 4)
    correct = random.choice(['A', 'B', 'C', 'D'])
    return Question(
        exam=exam,
        text=question,
        question_type='multiple_choice',
        option_a=options[0],
        option_b=options[1],
        option_c=options[2],
        option_d=options[3],
        correct_option=correct
    )

def generate_drag_and_drop():
    sample = random.sample(list(network_ports.items()), 3)
    return Question(
        exam=exam,
        text="Match the port number with the correct protocol.",
        question_type='drag_and_drop',
        extra_data={'pairs': {k: v for k, v in sample}}
    )

def generate_true_false():
    statement = f"{fake.word().capitalize()} is a type of input device."
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
    all_questions = []

    for _ in range(220):
        all_questions.append(generate_multiple_choice())
    for _ in range(40):
        all_questions.append(generate_drag_and_drop())
    for _ in range(40):
        all_questions.append(generate_true_false())

    random.shuffle(all_questions)
    Question.objects.bulk_create(all_questions)
    print(f"✅ A+ questions generated: {len(all_questions)}")

if __name__ == '__main__':
    run()
