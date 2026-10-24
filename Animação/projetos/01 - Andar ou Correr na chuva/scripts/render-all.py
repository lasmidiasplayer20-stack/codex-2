"""Compatibility entry point: resumable render, assembly and validation."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("render-full.py")),run_name="__main__")
