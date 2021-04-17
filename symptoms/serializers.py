from rest_framework import serializers
from .models import Symptom, Disorder


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ("id", "term")


class DisorderSerializer(serializers.ModelSerializer):
    matching_symptoms = serializers.IntegerField()
    weighted_score = serializers.IntegerField()

    class Meta:
        model = Disorder
        fields = (
            "disorder_name",
            "disorder_type_name",
            "disorder_group_name",
            "matching_symptoms",
            "weighted_score",
        )
