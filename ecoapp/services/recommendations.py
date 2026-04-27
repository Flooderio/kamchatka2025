from __future__ import annotations

from ecoapp.models import Checklist, Recommendation
from ecoapp.services.calculation import CalculationOutcome


def get_recommendations_for_outcome(outcome: CalculationOutcome) -> tuple[list[Recommendation], Checklist | None]:
    top_category = max(outcome.breakdown, key=outcome.breakdown.get) if outcome.breakdown else ""
    queryset = Recommendation.objects.filter(is_active=True).filter(
        user_type__in=["", outcome.user_type]
    )

    selected: list[Recommendation] = []
    for recommendation in queryset:
        if recommendation.trigger_category and recommendation.trigger_category != top_category:
            continue
        if recommendation.min_total_emission and outcome.total_emission < recommendation.min_total_emission:
            continue
        selected.append(recommendation)

    if not selected:
        selected = list(
            Recommendation.objects.filter(is_active=True, user_type__in=["", outcome.user_type])[:3]
        )

    checklist = (
        Checklist.objects.filter(is_active=True, user_type__in=["", outcome.user_type])
        .order_by("code")
        .first()
    )
    return selected[:5], checklist
