"""Auto-registers all motor adapters into a MotorRegistry.

To add a new motor:
  1. Create adapters/motor_NNN.py with a class that extends BaseMotorAdapter
  2. Add it to REAL_ADAPTERS below
  3. Done — the registry picks it up automatically

To swap an adapter: replace the class in REAL_ADAPTERS and the next run uses it.
"""
from __future__ import annotations

from ..motor_registry import MotorRegistry
from .motor_001 import Motor001Adapter
from .motor_002 import Motor002Adapter
from .motor_003 import Motor003Adapter
from .motor_004 import Motor004Adapter
from .motor_005 import Motor005Adapter
from .motor_006 import Motor006Adapter
from .motor_007 import Motor007Adapter
from .motor_008 import Motor008Adapter
from .motor_009 import Motor009Adapter
from .motor_010 import Motor010Adapter
from .motor_011 import Motor011Adapter
from .motor_012 import Motor012Adapter
from .motor_013 import Motor013Adapter
from .motor_014 import Motor014Adapter
from .motor_015 import Motor015Adapter
from .motor_016 import Motor016Adapter
from .motor_017 import Motor017Adapter
from .motor_018 import Motor018Adapter
from .motor_019 import Motor019Adapter
from .motor_020 import Motor020Adapter
from .motor_021 import Motor021Adapter
from .motor_022 import Motor022Adapter
from .motor_023 import Motor023Adapter
from .motor_026 import Motor026Adapter
from .motor_024 import Motor024Adapter
from .motor_025 import Motor025Adapter
from .motor_027 import Motor027Adapter
from .motor_028 import Motor028Adapter
from .motor_029 import Motor029Adapter
from .motor_030 import Motor030Adapter
from .motor_031 import Motor031Adapter
from .motor_032 import Motor032Adapter
from .motor_033 import Motor033Adapter
from .motor_034 import Motor034Adapter
from .motor_035 import Motor035Adapter
from .motor_036 import Motor036Adapter
from .motor_037 import Motor037Adapter
from .motor_038 import Motor038Adapter
from .motor_039 import Motor039Adapter
from .motor_040 import Motor040Adapter
from .motor_041 import Motor041Adapter
from .motor_042 import Motor042Adapter
from .motor_043 import Motor043Adapter
from .motor_044 import Motor044Adapter
from .motor_045 import Motor045Adapter
from .motor_046 import Motor046Adapter
from .motor_047 import Motor047Adapter
from .motor_048 import Motor048Adapter
from .motor_049 import Motor049Adapter
from .motor_050 import Motor050Adapter
from .motor_051 import Motor051Adapter
from .motor_052 import Motor052Adapter
from .motor_053 import Motor053Adapter
from .motor_054 import Motor054Adapter
from .motor_055 import Motor055Adapter
from .motor_056 import Motor056Adapter
from .motor_057 import Motor057Adapter
from .motor_058 import Motor058Adapter
from .motor_059 import Motor059Adapter
from .stub import StubMotorAdapter

# ── Real adapters (motors with executable code) ───────────────────────────────
REAL_ADAPTERS = [
    Motor001Adapter(),
    Motor002Adapter(),
    Motor003Adapter(),
    Motor004Adapter(),
    Motor005Adapter(),
    Motor006Adapter(),
    Motor007Adapter(),
    Motor008Adapter(),
    Motor009Adapter(),
    Motor010Adapter(),
    Motor011Adapter(),
    Motor012Adapter(),
    Motor013Adapter(),
    Motor014Adapter(),
    Motor015Adapter(),
    Motor016Adapter(),
    Motor017Adapter(),
    Motor018Adapter(),
    Motor019Adapter(),
    Motor020Adapter(),
    Motor021Adapter(),
    Motor022Adapter(),
    Motor023Adapter(),
    Motor026Adapter(),
    Motor024Adapter(),
    Motor025Adapter(),
    Motor027Adapter(),
    Motor028Adapter(),
    Motor029Adapter(),
    Motor030Adapter(),
    Motor031Adapter(),
    Motor032Adapter(),
    Motor033Adapter(),
    Motor034Adapter(),
    Motor035Adapter(),
    Motor036Adapter(),
    Motor037Adapter(),
    Motor038Adapter(),
    Motor039Adapter(),
    Motor040Adapter(),
    Motor041Adapter(),
    Motor042Adapter(),
    Motor043Adapter(),
    Motor044Adapter(),
    Motor045Adapter(),
    Motor046Adapter(),
    Motor047Adapter(),
    Motor048Adapter(),
    Motor049Adapter(),
    Motor050Adapter(),
    Motor051Adapter(),
    Motor052Adapter(),
    Motor053Adapter(),
    Motor054Adapter(),
    Motor055Adapter(),
    Motor056Adapter(),
    Motor057Adapter(),
    Motor058Adapter(),
    Motor059Adapter(),
]

# ── Stub adapters for motors without code yet ─────────────────────────────────
# Dependencies mirror motor_dependencies.json exactly.
STUB_ADAPTERS = [
]


def build_registry() -> MotorRegistry:
    """Return a fully populated MotorRegistry with all registered adapters."""
    registry = MotorRegistry()
    for adapter in REAL_ADAPTERS:
        registry.register(adapter)
    for adapter in STUB_ADAPTERS:
        registry.register(adapter)
    return registry
