from django.core.management.base import BaseCommand
from exams.models import Question, Exam

class Command(BaseCommand):
    help = 'Displays the total number of questions and counts per exam.'

    def handle(self, *args, **kwargs):
        total = Question.objects.count()
        self.stdout.write(self.style.NOTICE(f"\n📊 Total questions in database: {total}\n"))

        for exam in Exam.objects.all():
            count = Question.objects.filter(exam=exam).count()
            self.stdout.write(self.style.SUCCESS(f"{exam.name}: {count} questions"))
