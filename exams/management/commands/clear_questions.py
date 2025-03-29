from django.core.management.base import BaseCommand
from exams.models import Question

class Command(BaseCommand):
    help = "Delete all questions"

    def handle(self, *args, **kwargs):
        Question.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(" All questions deleted."))
