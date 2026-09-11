"""Explicit disclosure policies for controlled brief sharing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .models import BriefError, BriefInput, validate_text
from .planning import build_brief


@dataclass(frozen=True)
class DisclosurePolicy:
    """Sections and metadata permitted in a share-ready brief."""

    name: str
    include_objective: bool = True
    include_context: bool = False
    include_decisions: bool = True
    include_risks: bool = False
    include_actions: bool = True
    include_owner_names: bool = False
    include_due_dates: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "name",
            validate_text(self.name, "disclosure policy name", max_length=200),
        )
        for field_name in (
            "include_objective",
            "include_context",
            "include_decisions",
            "include_risks",
            "include_actions",
            "include_owner_names",
            "include_due_dates",
        ):
            if not isinstance(getattr(self, field_name), bool):
                raise BriefError(f"{field_name} must be true or false")


@dataclass(frozen=True)
class SharedRisk:
    description: str
    owner: str | None


@dataclass(frozen=True)
class SharedAction:
    description: str
    owner: str | None
    due_on: date | None


@dataclass(frozen=True)
class SharedBrief:
    policy_name: str
    title: str
    audience: str
    as_of: date
    objective: str | None
    context: tuple[str, ...]
    decisions: tuple[str, ...]
    risks: tuple[SharedRisk, ...]
    actions: tuple[SharedAction, ...]
    included_sections: tuple[str, ...]


def build_shared_brief(
    source: BriefInput,
    *,
    as_of: date,
    policy: DisclosurePolicy,
) -> SharedBrief:
    """Build a view containing only values explicitly allowed by policy."""

    planned = build_brief(source, as_of=as_of)
    included = tuple(
        name
        for name, enabled in (
            ("objective", policy.include_objective),
            ("context", policy.include_context),
            ("decisions", policy.include_decisions),
            ("risks", policy.include_risks),
            ("actions", policy.include_actions),
        )
        if enabled
    )
    risks = (
        tuple(
            SharedRisk(
                description=item.description,
                owner=item.owner if policy.include_owner_names else None,
            )
            for item in planned.risks
        )
        if policy.include_risks
        else ()
    )
    actions = (
        tuple(
            SharedAction(
                description=item.action.description,
                owner=item.action.owner if policy.include_owner_names else None,
                due_on=item.action.due_on if policy.include_due_dates else None,
            )
            for item in planned.actions
        )
        if policy.include_actions
        else ()
    )
    return SharedBrief(
        policy_name=policy.name,
        title=planned.title,
        audience=planned.audience,
        as_of=planned.as_of,
        objective=planned.objective if policy.include_objective else None,
        context=planned.context if policy.include_context else (),
        decisions=planned.decisions if policy.include_decisions else (),
        risks=risks,
        actions=actions,
        included_sections=included,
    )
