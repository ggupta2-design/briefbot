"""Local-first project brief automation."""

from .input import brief_from_dict, load_brief
from .models import ActionItem, BriefError, BriefInput, RiskItem
from .output import write_output
from .planning import ActionState, Brief, PlannedAction, build_brief
from .report import brief_to_dict, format_brief

__version__ = "0.1.0"

__all__ = [
    "ActionItem",
    "ActionState",
    "Brief",
    "BriefError",
    "BriefInput",
    "PlannedAction",
    "RiskItem",
    "brief_from_dict",
    "brief_to_dict",
    "build_brief",
    "format_brief",
    "load_brief",
    "write_output",
    "__version__",
]
