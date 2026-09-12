"""Local-first project brief automation."""

from .batch import (
    BatchFinding,
    BatchReadinessResult,
    audit_brief_folder,
    discover_brief_files,
)
from .diffing import BriefDiff, SectionDelta, compare_briefs
from .disclosure import (
    DisclosurePolicy,
    SharedAction,
    SharedBrief,
    SharedRisk,
    build_shared_brief,
)
from .input import brief_from_dict, load_brief
from .models import ActionItem, BriefError, BriefInput, RiskItem
from .output import write_output
from .planning import ActionState, Brief, PlannedAction, build_brief
from .policy import load_policy, policy_from_dict
from .share_policy import disclosure_policy_from_dict, load_disclosure_policy
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
    format_disclosure_policy,
    format_policy,
    format_readiness,
    format_shared_brief,
    shared_brief_to_dict,
    format_workload,
    workload_to_dict,
)

from .workload import (
    BriefWorkload,
    PortfolioWorkload,
    WorkloadCounts,
    summarize_brief_folder,
    summarize_brief_workload,
    validate_window_days,
)

__version__ = "0.6.0"

__all__ = [
    "ActionItem",
    "ActionState",
    "BatchFinding",
    "BatchReadinessResult",
    "Brief",
    "BriefError",
    "BriefDiff",
    "BriefInput",
    "BriefWorkload",
    "DisclosurePolicy",
    "PlannedAction",
    "PortfolioWorkload",
    "RiskItem",
    "SectionDelta",
    "SharedAction",
    "SharedBrief",
    "SharedRisk",
    "WorkloadCounts",
    "ReadinessCode",
    "ReadinessFinding",
    "ReadinessPolicy",
    "ReadinessResult",
    "ReadinessSeverity",
    "assess_readiness",
    "audit_brief_folder",
    "brief_from_dict",
    "brief_to_dict",
    "build_shared_brief",
    "compare_briefs",
    "build_brief",
    "format_batch_readiness",
    "format_brief",
    "format_diff",
    "format_disclosure_policy",
    "format_policy",
    "format_readiness",
    "format_shared_brief",
    "format_workload",
    "disclosure_policy_from_dict",
    "discover_brief_files",
    "load_brief",
    "load_disclosure_policy",
    "load_policy",
    "summarize_brief_folder",
    "summarize_brief_workload",
    "policy_from_dict",
    "shared_brief_to_dict",
    "validate_window_days",
    "workload_to_dict",
    "write_output",
    "__version__",
]
