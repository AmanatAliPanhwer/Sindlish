"""
Object model for the Sindlish language.

Re-exports all public types and type singletons.
"""

from .base import SHEY_TYPE, SdShey, SdType
from .collections import (
    FEHRIST_TYPE,
    LUGHAT_TYPE,
    MAJMUO_TYPE,
    SILSILO_TYPE,
    SdDict,
    SdList,
    SdRange,
    SdSet,
)
from .core import KAAM_TYPE, KHALI_TYPE, RESULT_TYPE, SdFunction, SdNull, SdResult
from .numbers import ADAD_TYPE, DAHAI_TYPE, FAISLO_TYPE, SdBool, SdNumber
from .strings import LAFZ_TYPE, SdString

__all__ = [
    "ADAD_TYPE",
    "DAHAI_TYPE",
    "FAISLO_TYPE",
    "FEHRIST_TYPE",
    "KAAM_TYPE",
    "KHALI_TYPE",
    "LAFZ_TYPE",
    "LUGHAT_TYPE",
    "MAJMUO_TYPE",
    "RESULT_TYPE",
    "SHEY_TYPE",
    "SILSILO_TYPE",
    "SdBool",
    "SdDict",
    "SdFunction",
    "SdList",
    "SdNull",
    "SdNumber",
    "SdRange",
    "SdResult",
    "SdSet",
    "SdShey",
    "SdString",
    "SdType",
]
