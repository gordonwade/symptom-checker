from django.db import models


class Symptom(models.Model):
    id = models.IntegerField(primary_key=True)
    term = models.CharField(max_length=250)
    include_in_form = models.BooleanField(default=False)


class Disorder(models.Model):
    id = models.IntegerField(primary_key=True)
    disorder_name = models.CharField(max_length=250)
    disorder_type_id = models.IntegerField()
    disorder_type_name = models.CharField(max_length=250)
    disorder_group_id = models.IntegerField()
    disorder_group_name = models.CharField(max_length=250)


class SymptomDisorder(models.Model):
    symptom_id = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    disorder_id = models.ForeignKey(Disorder, on_delete=models.CASCADE)
    frequency_id = models.IntegerField()
    frequency_name = models.CharField(max_length=250)
