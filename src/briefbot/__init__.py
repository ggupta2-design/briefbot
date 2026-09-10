"""Local-first project brief automation."""

from .batch import (
    BatchFinding,
    BatchReadinessResult,
    audit_brief_folder,
    discover_brief_files,
)
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
from .report import (
    brief_to_dict,
    format_batch_readiness,
    format_brief,
    format_diff,
    format_policy,
    format_readiness,
)

__version__ = "0.4.0"

__all__ = [
    "ActionItem",
    "ActionState",
    "BatchFinding",
    "BatchReadinessResult",
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
    "audit_brief_folder",
    "brief_from_dict",
    "brief_to_dict",
    "compare_briefs",
    "build_brief",
    "format_batch_readiness",
    "format_brief",
    "format_diff",
    "format_policy",
    "format_readiness",
    "discover_brief_files",
    "load_brief",
    "load_policy",
    "policy_from_dict",
    "write_output",
    "__version__",
]
