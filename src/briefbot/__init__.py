"""Local-first project brief automation."""

from .diffing import BriefDiff, SectionDelta, compare_briefs
from .input import brief_from_dict, load_brief
from .models import ActionItem, BriefError, BriefInput, RiskItem
from .output import write_output
from .planning import ActionState, Brief, PlannedAction, build_brief
from .policy import load_policy, policy_from_dict
from .readiness import (
    ReadinessCode,
    ReadinessFinding,
    ReadinessPolicy,
    ReadinessResult,
    ReadinessSeverity,
    assess_readiness,
)
from .report import brief_to_dict, format_brief, format_diff, format_policy, format_readiness

__version__ = "0.3.0"

__all__ = [
    "ActionItem",
    "ActionState",
    "Brief",
    "BriefError",
    "BriefDiff",
    "BriefInput",
    "PlannedAction",
    "RiskItem",
    "SectionDelta",
    "ReadinessCode",
    "ReadinessFinding",
    "ReadinessPolicy",
    "ReadinessResult",
    "ReadinessSeverity",
    "assess_readiness",
    "brief_from_dict",
    "brief_to_dict",
    "compare_briefs",
    "build_brief",
    "format_brief",
    "format_diff",
    "format_policy",
    "format_readiness",
    "load_brief",
    "load_policy",
    "policy_from_dict",
    "write_output",
    "__version__",
]
