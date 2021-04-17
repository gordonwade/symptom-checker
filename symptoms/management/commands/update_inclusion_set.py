from django.core.management.base import BaseCommand
from symptoms.models import Symptom

INCLUSION_IDS = [
    19,
    133,
    18,
    79,
    21,
    53,
    123,
    335,
    69,
    427,
    569,
    30,
    8,
    23,
    77,
    274,
    326,
    658,
    20,
    22,
]


class Command(BaseCommand):
    help = "Update the symptoms to include in the patient survey."

    def handle(self, *args, **options):
        self.reset_all_symptoms()
        self.update_inclusion_symptoms()
        self.stdout.write(self.style.SUCCESS("DONE!"))

    def reset_all_symptoms(self):
        self.stdout.write(self.style.SUCCESS("Removing included symptoms..."))
        Symptom.objects.filter(include_in_form=True).update(include_in_form=False)

    def update_inclusion_symptoms(self):
        self.stdout.write(self.style.SUCCESS("Including new symptoms..."))
        Symptom.objects.filter(id__in=INCLUSION_IDS).update(include_in_form=True)
