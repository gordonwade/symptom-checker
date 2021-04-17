import requests
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand, CommandError
from symptoms.models import Symptom, Disorder, SymptomDisorder


class Command(BaseCommand):
    help = (
        "Download and parse XML symptom and disorder data. Load it into the"
        "Django database."
    )

    @staticmethod
    def download_xml():
        url = "http://www.orphadata.org/data/xml/en_product4.xml"
        r = requests.get(url)

        with open("disease_mapping.xml", "wb") as f:
            f.write(r.content)

    def parse_all(self, xmlfile):
        tree = ET.parse(xmlfile)
        root = tree.getroot()

        # Parse the "disorders" into models and save
        all_disorder_sets = root.findall(
            "./HPODisorderSetStatusList/HPODisorderSetStatus"
        )
        parsed_disorders = [
            self.model_disorder_set(disorder_set) for disorder_set in all_disorder_sets
        ]
        [m.save() for m in parsed_disorders]
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully parsed {len(parsed_disorders)} disorder models."
            )
        )

        # Parse the "symptoms" into models and save
        all_hpos = root.findall(
            "./HPODisorderSetStatusList/HPODisorderSetStatus/Disorder/HPODisorderAssociationList/HPODisorderAssociation/HPO"
        )
        symptom_models = self.model_all_symptoms(all_hpos)
        [m.save() for m in symptom_models]
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully parsed {len(symptom_models)} symptom models."
            )
        )

        # Parse the "relationships" into models and save
        all_disorders = root.findall(
            "./HPODisorderSetStatusList/HPODisorderSetStatus/Disorder"
        )
        relationship_models = self.model_relationships(all_disorders)
        [m.save() for m in relationship_models]
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully parsed {len(relationship_models)} relationship models."
            )
        )

    def model_disorder_set(self, disorder_set):
        disorder = disorder_set.find("Disorder")
        name = disorder.find("Name").text
        disorder_id = disorder.get("id")

        disorder_type = disorder.find("DisorderType")
        disorder_type_id = disorder_type.get("id")
        disorder_type_name = disorder_type.find("Name").text

        disorder_group = disorder.find("DisorderGroup")
        disorder_group_id = disorder_group.get("id")
        disorder_group_name = disorder_group.find("Name").text

        return Disorder(
            id=disorder_id,
            disorder_name=name,
            disorder_type_id=disorder_type_id,
            disorder_type_name=disorder_type_name,
            disorder_group_id=disorder_group_id,
            disorder_group_name=disorder_group_name,
        )

    def model_all_symptoms(self, hpos):
        all_symptoms = [self.parse_symptom(hpo) for hpo in hpos]
        all_symptoms_set = list(
            map(dict, set(tuple(sorted(sd.items())) for sd in all_symptoms))
        )

        return [Symptom(id=s["symptom_id"], term=s["term"]) for s in all_symptoms_set]

    def parse_symptom(self, hpo):
        # From HPO
        return {"symptom_id": hpo.get("id"), "term": hpo.find("HPOTerm").text}

    def model_relationships(self, all_disorders):
        all_relationships = []
        for d in all_disorders:
            all_relationships.extend(self.parse_relationships(d))

        return [
            SymptomDisorder(
                symptom_id=entry["symptom_id"],
                disorder_id=entry["disorder_id"],
                frequency_id=entry["frequency_id"],
                frequency_name=entry["frequency_name"],
            )
            for entry in all_relationships
        ]

    def parse_relationships(self, disorder):
        # From Disorder (not DisorderSetStatus)
        disorder_id = disorder.get("id")
        association_list = disorder.find("./HPODisorderAssociationList")
        associations = association_list.findall("./HPODisorderAssociation")

        return [self.parse_relationship(a, disorder_id) for a in associations]

    def parse_relationship(self, association, disorder_id):
        symptom_id = association.find("HPO").get("id")

        frequency_id = association.find("HPOFrequency").get("id")
        frequency_name = association.find("HPOFrequency").find("Name").text

        return {
            "disorder_id": Disorder.objects.get(id=disorder_id),
            "symptom_id": Symptom.objects.get(id=symptom_id),
            "frequency_id": frequency_id,
            "frequency_name": frequency_name,
        }

    def handle(self, *args, **options):
        self.download_xml()
        self.parse_all("disease_mapping.xml")
