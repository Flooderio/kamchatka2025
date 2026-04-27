from __future__ import annotations

from ecoapp.models import Checklist, Recommendation
from ecoapp.services.calculation import CalculationOutcome


def build_report_text(
    outcome: CalculationOutcome,
    recommendations: list[Recommendation],
    checklist: Checklist | None,
) -> str:
    breakdown_lines = [
        f"- {label}: {value:.2f} кг CO2e"
        for label, value in outcome.breakdown.items()
    ]
    recommendation_lines = [f"- {item.title}: {item.content}" for item in recommendations]
    checklist_line = ""
    if checklist:
        checklist_line = f"\nЧек-лист: {checklist.title}\n{checklist.content}"
        if checklist.url:
            checklist_line += f"\nСсылка: {checklist.url}"

    route_line = outcome.route.name if outcome.route else "не указан"
    return (
        f"Тип пользователя: {outcome.user_type}\n"
        f"Маршрут: {route_line}\n"
        f"Итоговый углеродный след: {outcome.total_emission:.2f} кг CO2e\n\n"
        f"Детализация:\n" + "\n".join(breakdown_lines) + "\n\n"
        f"Рекомендации:\n" + "\n".join(recommendation_lines) + checklist_line
    )
