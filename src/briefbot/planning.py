"""Deterministic brief planning and action prioritization."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum

from .models import ActionItem, BriefInput, RiskItem


class ActionState(str, Enum):
    OVERDUE = "overdue"
    DUE_TODAY = "due_today"
    UPCOMING = "upcoming"
    UNSCHEDULED = "unscheduled"


@dataclass(frozen=True)
class PlannedAction:
    """An action enriched with a reproducible schedule state."""

    action: ActionItem
    state: ActionState
    days_until: int | None


@dataclass(frozen=True)
class Brief:
    """A validated, prioritized brief ready for formatting."""

    title: str
    audience: str
    objective: str
    as_of: date
    context: tuple[str, ...]
    decisions: tuple[str, ...]
    risks: tuple[RiskItem, ...]
    actions: tuple[PlannedAction, ...]


_STATE_PRIORITY = {
    ActionState.OVERDUE: 0,
    ActionState.DUE_TODAY: 1,
    ActionState.UPCOMING: 2,
    ActionState.UNSCHEDULED: 3,
}


def _plan_action(action: ActionItem, *, as_of: date) -> PlannedAction:
    if action.due_on is None:
        return PlannedAction(action, ActionState.UNSCHEDULED, None)
    days_until = (action.due_on - as_of).days
    if days_until < 0:
        state = ActionState.OVERDUE
    elif days_until == 0:
        state = ActionState.DUE_TODAY
    else:
        state = ActionState.UPCOMING
    return PlannedAction(action, state, days_until)


def build_brief(source: BriefInput, *, as_of: date) -> Brief:
    """Create a deterministic brief without mutating the source notes."""

    actions = tuple(_plan_action(item, as_of=as_of) for item in source.actions)
    ordered = tuple(
        sorted(
            actions,
            key=lambda item: (
                _STATE_PRIORITY[item.state],
                item.action.due_on or date.max,
                (item.action.owner or "").casefold(),
                item.action.description.casefold(),
            ),
        )
    )
    return Brief(
        title=source.title,
        audience=source.audience,
        objective=source.objective,
        as_of=as_of,
        context=source.context,
        decisions=source.decisions,
        risks=source.risks,
        actions=ordered,
    )
