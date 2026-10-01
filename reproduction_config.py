"""Portable paths for reproducing the existing manuscript figures.

Set STRESS_DATA_ROOT to the folder containing the four dataset folders.
Set STRESS_OUTPUT_ROOT to choose where generated figures are saved.
"""
from pathlib import Path
import os

PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = Path(os.environ.get("STRESS_DATA_ROOT", str(PACKAGE_ROOT / "data"))).expanduser()
OUTPUT_ROOT = Path(os.environ.get("STRESS_OUTPUT_ROOT", str(PACKAGE_ROOT / "results"))).expanduser()
