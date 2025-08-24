from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Seed all exam questions (A+, Network+, Security+) from CSVs."

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Clearing all existing questions..."))
        call_command('clear_questions')

        self.stdout.write(self.style.NOTICE("Seeding A+ questions..."))
        call_command('seed_a_plus_questions')

        self.stdout.write(self.style.NOTICE("Seeding Network+ questions..."))
        call_command('seed_network_plus_questions')

        self.stdout.write(self.style.NOTICE("Seeding Security+ questions..."))
        call_command('seed_security_plus_questions')

        self.stdout.write(self.style.SUCCESS("All exam questions have been seeded."))
