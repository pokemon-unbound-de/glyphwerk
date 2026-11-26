"""Shared synthetic 64-KB GBA ROM fixtures (zero copyrighted ROM data).

The ROM builder lives in :mod:`glyphwerk.demo_data` so the demo can use it without
importing test code.
"""
from __future__ import annotations

import pytest

from glyphwerk.demo_data import SyntheticRomLayout, build_synthetic_rom


@pytest.fixture
def synthetic_rom() -> SyntheticRomLayout:
    return build_synthetic_rom()
