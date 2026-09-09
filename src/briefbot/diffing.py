"""Deterministic, value-free comparisons between validated brief versions."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Hashable, Iterable

from .models import BriefInput


@dataclass(frozen=True)
class SectionDelta:
    """Aggregate changes for one brief collection."""

    added: int
    removed: int
    unchanged: int

    @property
    def changed(self) -> bool:
        return self.added > 0 or self.removed > 0

    @property
    def change_count(self) -> int:
        return self.added + self.removed


@dataclass(frozen=True)
class BriefDiff:
    """Value-free difference between two validated brief inputs."""

    metadata_changed: tuple[str, ...]
    context: SectionDelta
    decisions: SectionDelta
    risks: SectionDelta
    actions: SectionDelta

    @property
    def changed(self) -> bool:
        return bool(self.metadata_changed) or any(
            section.changed
            for section in (self.context, self.decisions, self.risks, self.actions)
        )

    @property
    def total_changes(self) -> int:
        return len(self.metadata_changed) + sum(
            section.change_count
            for section in (self.context, self.decisions, self.risks, self.actions)
        )


def _compare_items(
    previous: Iterable[Hashable],
    current: Iterable[Hashable],
) -> SectionDelta:
    before = Counter(previous)
    after = Counter(current)
    shared = before & after
    return SectionDelta(
        added=sum((after - before).values()),
        removed=sum((before - after).values()),
        unchanged=sum(shared.values()),
    )


def compare_briefs(previous: BriefInput, current: BriefInput) -> BriefDiff:
    """Compare two briefs without returning any source values."""

    metadata_changed = tuple(
        field_name
        for field_name in ("title", "audience", "objective")
        if getattr(previous, field_name) != getattr(current, field_name)
    )
    return BriefDiff(
        metadata_changed=metadata_changed,
        context=_compare_items(previous.context, current.context),
        decisions=_compare_items(previous.decisions, current.decisions),
        risks=_compare_items(previous.risks, current.risks),
        actions=_compare_items(previous.actions, current.actions),
    )
