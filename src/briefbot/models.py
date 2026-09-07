"""Validated domain models for project briefs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


class BriefError(ValueError):
    """Raised when brief input or output cannot be used safely."""


def validate_text(value: str, field_name: str, *, max_length: int = 2000) -> str:
    """Normalize required text while enforcing practical size limits."""

    if not isinstance(value, str):
        raise BriefError(f"{field_name} must be text")
    cleaned = value.strip()
    if not cleaned:
        raise BriefError(f"{field_name} cannot be blank")
    if len(cleaned) > max_length:
        raise BriefError(f"{field_name} cannot exceed {max_length} characters")
    return cleaned


def validate_optional_text(
    value: str | None,
    field_name: str,
    *,
    max_length: int = 200,
) -> str | None:
    if value is None:
        return None
    return validate_text(value, field_name, max_length=max_length)


@dataclass(frozen=True)
class ActionItem:
    """One action retained in a generated brief."""

    description: str
    owner: str | None = None
    due_on: date | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "description",
            validate_text(self.description, "action description"),
        )
        object.__setattr__(
            self,
            "owner",
            validate_optional_text(self.owner, "action owner"),
        )


@dataclass(frozen=True)
class RiskItem:
    """One project risk and its optional owner."""

    description: str
    owner: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "description",
            validate_text(self.description, "risk description"),
        )
        object.__setattr__(
            self,
            "owner",
            validate_optional_text(self.owner, "risk owner"),
        )


@dataclass(frozen=True)
class BriefInput:
    """Strict source material for one deterministic brief."""

    title: str
    audience: str
    objective: str
    context: tuple[str, ...] = ()
    decisions: tuple[str, ...] = ()
    risks: tuple[RiskItem, ...] = ()
    actions: tuple[ActionItem, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "title",
            validate_text(self.title, "title", max_length=200),
        )
        object.__setattr__(
            self,
            "audience",
            validate_text(self.audience, "audience", max_length=200),
        )
        object.__setattr__(
            self,
            "objective",
            validate_text(self.objective, "objective"),
        )
        for field_name in ("context", "decisions"):
            values = getattr(self, field_name)
            if len(values) > 100:
                raise BriefError(f"{field_name} cannot contain more than 100 items")
            object.__setattr__(
                self,
                field_name,
                tuple(
                    validate_text(item, f"{field_name} item")
                    for item in values
                ),
            )
        if len(self.risks) > 100:
            raise BriefError("risks cannot contain more than 100 items")
        if len(self.actions) > 100:
            raise BriefError("actions cannot contain more than 100 items")
