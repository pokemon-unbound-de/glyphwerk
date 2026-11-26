"""The synthetic demo ROM lives in the package, and the demo does not depend on ``tests``."""
import subprocess
import sys
from pathlib import Path

from glyphwerk.demo_data import build_synthetic_rom

DEMO = Path(__file__).resolve().parents[1] / "examples" / "minimal_synthetic_demo" / "run_demo.py"


def test_build_synthetic_rom_is_deterministic():
    first = build_synthetic_rom()
    second = build_synthetic_rom()
    assert len(first.rom) == 0x10000
    assert first.rom == second.rom
    assert first == second


def test_demo_runs_when_another_tests_package_is_loaded():
    # Simulate an unrelated top-level ``tests`` module already loaded (e.g. via a .pth file).
    code = (
        "import runpy, sys, types; "
        "sys.modules['tests'] = types.ModuleType('tests'); "
        f"runpy.run_path({str(DEMO)!r}, run_name='__main__')"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert "DEMO GREEN" in proc.stdout
