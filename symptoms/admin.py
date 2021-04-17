from django.contrib import admin
from .models import Disorder, Symptom, SymptomDisorder


@admin.register(Disorder)
class DisorderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "disorder_name",
        "disorder_type_id",
        "disorder_type_name",
        "disorder_group_id",
        "disorder_group_name",
    )
    search_fields = ("disorder_name", "disorder_type_name", "disorder_group_name")


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ("id", "term", "include_in_form")
    search_fields = ("term", "include_in_form")


@admin.register(SymptomDisorder)
class SymptomDisorderAdmin(admin.ModelAdmin):
    list_display = (
        "symptom_name",
        "disorder_name",
        "frequency_id",
        "frequency_name",
    )
    search_fields = ("symptom_id",)

    def symptom_name(self, obj):
        return obj.symptom_id.term

    def disorder_name(self, obj):
        return obj.disorder_id.disorder_name
