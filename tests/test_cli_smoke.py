import pytest
import subprocess
import sys

def test_run_py_help():
    result = subprocess.run([sys.executable, "run.py", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "AutoJobForge" in result.stdout
    assert "--mode" in result.stdout
    assert "--limit" in result.stdout
