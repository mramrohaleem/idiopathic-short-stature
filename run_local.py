"""Utility script to create a virtual environment, install dependencies, and generate the essay.

Run `python run_local.py` from the project root to set up the environment and build the DOCX file.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str], description: str) -> None:
    """Run a subprocess command with a friendly status message."""
    print(description)
    subprocess.run(command, check=True)


def ensure_virtualenv(venv_path: Path) -> Path:
    """Create the virtual environment if it does not already exist and return the Python executable path."""
    if not venv_path.exists():
        run_command([sys.executable, "-m", "venv", str(venv_path)], "Creating virtual environment...")
    else:
        print("Virtual environment already exists. Skipping creation.")

    if os.name == "nt":
        python_executable = venv_path / "Scripts" / "python.exe"
    else:
        python_executable = venv_path / "bin" / "python"

    if not python_executable.exists():
        raise FileNotFoundError(f"Cannot locate python executable inside virtual environment: {python_executable}")

    return python_executable


def main() -> None:
    project_root = Path(__file__).resolve().parent
    venv_path = project_root / ".venv"

    python_executable = ensure_virtualenv(venv_path)
    run_command([str(python_executable), "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip...")
    run_command([str(python_executable), "-m", "pip", "install", "python-docx"], "Installing dependencies...")
    run_command([str(python_executable), "generate_essay.py"], "Generating essay...")
    print("Essay generation complete. Output saved as Idiopathic_Short_Stature_Essay.docx")


if __name__ == "__main__":
    main()
