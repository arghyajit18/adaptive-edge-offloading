import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

def test_dashboard_import():
    from adaptive_engine.dashboard import app  # noqa: F401
    assert app is not None
