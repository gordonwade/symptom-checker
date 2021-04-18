from django.db.models import Count, Q
from rest_framework import viewsets, generics
from .serializers import SymptomSerializer, DisorderSerializer
from .models import Symptom, Disorder


# Frequency lookup for reference
#  frequency_id |     frequency_name
# --------------+------------------------
#         28433 | Very rare (<4-1%)
#         28440 | Excluded (0%)
#         28426 | Occasional (29-5%)
#         28412 | Very frequent (99-80%)
#         28419 | Frequent (79-30%)
#         28405 | Obligate (100%)


MAX_RESULTS = 10


class SymptomView(viewsets.ModelViewSet):
    serializer_class = SymptomSerializer
    queryset = Symptom.objects.all().filter(include_in_form=True)


class DisorderView(generics.ListAPIView):
    serializer_class = DisorderSerializer

    def get_queryset(self):
        symptom_keys = self.request.query_params.get(
            "symptom_keys"
        ) or self.request.data.get("symptom_keys")
        if symptom_keys:
            symptom_key_list = symptom_keys.split(",")
            return (
                Disorder.objects.all()
                .filter(
                    symptomdisorder__symptom_id__in=symptom_key_list,
                )
                .annotate(
                    matching_symptoms=Count(
                        "symptomdisorder__symptom_id",
                        filter=Q(symptomdisorder__symptom_id__in=symptom_key_list),
                    )
                )
                .annotate(
                    weighted_score=Count(
                        "symptomdisorder__symptom_id",
                        filter=Q(symptomdisorder__symptom_id__in=symptom_key_list)
                        & Q(symptomdisorder__frequency_id__exact=28405),
                    )
                    * 10
                    + Count(
                        "symptomdisorder__symptom_id",
                        filter=Q(symptomdisorder__symptom_id__in=symptom_key_list)
                        & Q(symptomdisorder__frequency_id__exact=28412),
                    )
                    * 9
                    + Count(
                        "symptomdisorder__symptom_id",
                        filter=Q(symptomdisorder__symptom_id__in=symptom_key_list)
                        & Q(symptomdisorder__frequency_id__exact=28419),
                    )
                    * 6
                    + Count(
                        "symptomdisorder__symptom_id",
                        filter=Q(symptomdisorder__symptom_id__in=symptom_key_list)
                        & Q(symptomdisorder__frequency_id__exact=28426),
                    )
                    * 2
                )
                .order_by("-weighted_score")[:MAX_RESULTS]
            )

    def post(self, request, *args, **kwargs):
        # Support querying via POST request
        return self.list(request, *args, **kwargs)
